import io
import logging
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.config import get_settings
from app.schemas import UploadSummaryResponse
from app.services.student_service import StudentService
from app.utils import (
    ValidationError,
    calculate_percentage,
    normalize_register_number_input,
    validate_attendance_counts,
    validate_upload_file,
)

logger = logging.getLogger(__name__)

COLUMN_ALIASES: dict[str, list[str]] = {
    "register_number": ["register number", "register_number", "reg no", "regno", "register no"],
    "name": ["student name", "name", "student_name"],
    "department": ["department", "dept"],
    "year": ["year"],
    "section": ["section", "sec"],
    "semester": ["semester", "sem"],
    "subject_code": ["subject code", "subject_code", "sub code", "code"],
    "subject_name": ["subject name", "subject_name", "sub name", "subject"],
    "classes_conducted": ["classes conducted", "classes_conducted", "conducted", "total classes"],
    "classes_attended": ["classes attended", "classes_attended", "attended", "present"],
}


class UploadService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.student_service = StudentService(db)
        self.uploads_collection = db.attendance_uploads
        self.settings = get_settings()

    async def process_upload(self, filename: str, content: bytes) -> UploadSummaryResponse:
        logger.info("Upload started: %s", filename)
        validate_upload_file(filename, content, self.settings.max_upload_size_bytes)

        upload_path = Path(self.settings.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        saved_path = upload_path / filename
        saved_path.write_bytes(content)
        logger.info("Saved upload file to %s", saved_path)

        df = self._read_file(filename, content)
        df = self._normalize_columns(df)
        df = df.dropna(how="all")

        if df.empty:
            raise ValidationError("Uploaded file contains no data rows.")

        required = set(COLUMN_ALIASES.keys())
        missing = required - set(df.columns)
        if missing:
            raise ValidationError(f"Missing required columns: {', '.join(sorted(missing))}")

        summary = UploadSummaryResponse(updated=0, added=0, failed=0, errors=[])

        for index, row in df.iterrows():
            row_number = int(index) + 2
            if self._is_blank_row(row):
                continue

            try:
                record_summary = await self._process_row(row)
                summary.updated += record_summary["updated"]
                summary.added += record_summary["added"]
            except (ValidationError, ValueError) as exc:
                summary.failed += 1
                summary.errors.append(f"Row {row_number}: {exc}")
                logger.warning("Upload row %s failed: %s", row_number, exc)

        await self._store_upload_history(filename, summary)
        logger.info(
            "Upload success — added: %s, updated: %s, failed: %s",
            summary.added,
            summary.updated,
            summary.failed,
        )
        return summary

    async def _store_upload_history(self, filename: str, summary: UploadSummaryResponse) -> None:
        await self.uploads_collection.insert_one(
            {
                "upload_time": datetime.now(UTC),
                "filename": filename,
                "uploaded_records": summary.added,
                "updated_records": summary.updated,
                "failed_records": summary.failed,
            }
        )

    def _read_file(self, filename: str, content: bytes) -> pd.DataFrame:
        extension = Path(filename).suffix.lower()
        buffer = io.BytesIO(content)
        try:
            if extension == ".csv":
                return pd.read_csv(buffer, dtype=str, keep_default_na=False)
            return pd.read_excel(buffer, engine="openpyxl", dtype=str)
        except Exception as exc:
            raise ValidationError(f"Unable to read file: {exc}") from exc

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized = df.copy()
        normalized.columns = [str(col).strip().lower() for col in normalized.columns]

        rename_map: dict[str, str] = {}
        for canonical, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in normalized.columns:
                    rename_map[alias] = canonical
                    break

        return normalized.rename(columns=rename_map)

    async def _process_row(self, row: pd.Series) -> dict[str, int]:
        if pd.isna(row["register_number"]) or str(row["register_number"]).strip() == "":
            raise ValidationError("Register number is missing.")

        register_number = normalize_register_number_input(row["register_number"])
        name = self._require_text(row["name"], "Student name")
        department = self._require_text(row["department"], "Department")
        year = self._require_text(row["year"], "Year")
        section = self._require_text(row["section"], "Section")
        semester = self._require_text(row["semester"], "Semester")
        subject_code = self._require_text(row["subject_code"], "Subject code").upper()
        subject_name = self._require_text(row["subject_name"], "Subject name")

        classes_conducted = self._parse_int(row["classes_conducted"], "Classes conducted")
        classes_attended = self._parse_int(row["classes_attended"], "Classes attended")
        validate_attendance_counts(classes_conducted, classes_attended)

        percentage = calculate_percentage(classes_attended, classes_conducted)

        return await self.student_service.upsert_student_attendance(
            register_number=register_number,
            name=name,
            department=department,
            year=year,
            section=section,
            semester=semester,
            subject_code=subject_code,
            subject_name=subject_name,
            classes_conducted=classes_conducted,
            classes_attended=classes_attended,
            percentage=percentage,
        )

    @staticmethod
    def _is_blank_row(row: pd.Series) -> bool:
        return all(pd.isna(value) or str(value).strip() == "" for value in row)

    @staticmethod
    def _require_text(value: object, field_name: str) -> str:
        if pd.isna(value) or str(value).strip() == "":
            raise ValidationError(f"{field_name} is missing.")
        return str(value).strip()

    @staticmethod
    def _parse_int(value: object, field_name: str) -> int:
        if pd.isna(value):
            raise ValidationError(f"{field_name} is missing.")
        try:
            return int(float(value))
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"{field_name} must be a valid integer.") from exc
