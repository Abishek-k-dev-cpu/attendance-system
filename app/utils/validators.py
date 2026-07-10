from pathlib import Path

from app.utils.exceptions import ValidationError
from app.utils.register_number import normalize_register_number_input, validate_register_number

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_upload_file(filename: str, content: bytes, max_size_bytes: int) -> None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if not content:
        raise ValidationError("Uploaded file is empty.")

    if len(content) > max_size_bytes:
        raise ValidationError(f"File exceeds maximum size of {max_size_bytes // (1024 * 1024)} MB.")


def validate_attendance_counts(classes_conducted: int, classes_attended: int) -> None:
    if classes_conducted < 0:
        raise ValidationError("Classes conducted cannot be negative.")
    if classes_attended < 0:
        raise ValidationError("Classes attended cannot be negative.")
    if classes_attended > classes_conducted:
        raise ValidationError("Classes attended cannot exceed classes conducted.")
