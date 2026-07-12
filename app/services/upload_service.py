import io
import logging
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

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
from app.utils.attendance import compute_overall_from_attendance
from app.utils.sanitize import sanitize_text

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

        # Phase 1: validate + parse every row in memory. No DB calls here yet,
        # so a large file can't time out mid-parse.
        parsed_rows: list[dict] = []
        for index, row in df.iterrows():
            row_number = int(index) + 2
            if self._is_blank_row(row):
                continue
            try:
                parsed_rows.append(self._parse_row(row))
            except (ValidationError, ValueError) as exc:
                summary.failed += 1
                summary.errors.append(f"Row {row_number}: {exc}")
                logger.warning("Upload row %s failed: %s", row_number, exc)

        if not parsed_rows:
            await self._store_upload_history(filename, summary)
            if summary.failed == 0:
                raise ValidationError(
                    "No attendance rows were imported. Check that the file has data below the header row."
                )
            raise ValidationError(
                "Upload failed for all rows. Fix the file and try again. "
                f"First error: {summary.errors[0]}"
            )

        # Phase 2: merge rows per student in memory (last row for a given
        # subject code wins, matching the previous row-by-row behaviour).
        students: dict[str, dict] = {}
        for parsed in parsed_rows:
            reg_no = parsed["register_number"]
            entry = students.setdefault(
                reg_no,
                {"profile": parsed["profile"], "subjects": {}, "row_count": 0},
            )
            entry["profile"] = parsed["profile"]
            entry["subjects"][parsed["subject_code"]] = parsed["subject_entry"]
            entry["row_count"] += 1

        # Phase 3: one query to fetch every existing student in this batch,
        # instead of one find_one() per row.
        existing_docs = await self.student_service.collection.find(
            {"register_number": {"$in": list(students.keys())}}
        ).to_list(length=None)
        existing_map = {doc["register_number"]: doc for doc in existing_docs}

        logger.info(
            "Upload debug — parsed_rows: %s, unique_students: %s, existing_matched: %s, sample_keys: %s",
            len(parsed_rows),
            len(students),
            len(existing_map),
            list(students.keys())[:5],
        )

        now = datetime.now(UTC)
        bulk_ops: list[UpdateOne] = []

        for reg_no, data in students.items():
            existing = existing_map.get(reg_no)
            is_new_student = existing is None

            attendance_list = list(existing.get("attendance", [])) if existing else []
            for index, item in enumerate(attendance_list):
                code = item["subject_code"]
                if code in data["subjects"]:
                    attendance_list[index] = data["subjects"].pop(code)
            attendance_list.extend(data["subjects"].values())

            overall_pct, _, _ = compute_overall_from_attendance(attendance_list)

            bulk_ops.append(
                UpdateOne(
                    {"register_number": reg_no},
                    {
                        "$set": {
                            "register_number": reg_no,
                            **data["profile"],
                            "photo": (existing or {}).get("photo"),
                            "attendance": attendance_list,
                            "overall_percentage": overall_pct,
                            "last_updated": now,
                        }
                    },
                    upsert=True,
                )
            )

            if is_new_student:
                summary.added += 1
                summary.updated += data["row_count"] - 1
            else:
                summary.updated += data["row_count"]

        # Phase 4: one bulk write for the whole file, instead of one
        # insert_one/update_one per row.
        if bulk_ops:
            result = await self.student_service.collection.bulk_write(bulk_ops, ordered=False)
            logger.info(
                "Upload debug — bulk_write result: matched=%s, modified=%s, upserted=%s, upserted_ids=%s",
                result.matched_count,
                result.modified_count,
                result.upserted_count,
                list(result.upserted_ids.values())[:15] if result.upserted_ids else [],
            )

        await self._store_upload_history(filename, summary)

        if summary.added == 0 and summary.updated == 0 and summary.failed == 0:
            raise ValidationError(
                "No attendance rows were imported. Check that the file has data below the header row."
            )

        if summary.added == 0 and summary.updated == 0 and summary.failed > 0:
            raise ValidationError(
                "Upload failed for all rows. Fix the file and try again. "
                f"First error: {summary.errors[0]}"
            )

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

    def _parse_row(self, row: pd.Series) -> dict:
        """Validate a single row and return parsed data. Makes no DB calls —
        used so an entire large file can be validated in memory before any
        network round trip happens."""
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

        return {
            "register_number": register_number,
            "profile": {
                "name": sanitize_text(name),
                "department": sanitize_text(department),
                "year": sanitize_text(year, 20),
                "section": sanitize_text(section, 20),
                "semester": sanitize_text(semester, 20),
            },
            "subject_code": subject_code,
            "subject_entry": {
                "subject_code": subject_code,
                "subject_name": sanitize_text(subject_name),
                "classes_conducted": classes_conducted,
                "classes_attended": classes_attended,
                "percentage": percentage,
            },
        }

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
