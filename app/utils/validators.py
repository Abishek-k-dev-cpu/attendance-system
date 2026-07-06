import re
from pathlib import Path

from app.utils.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
REGISTER_NUMBER_PATTERN = re.compile(r"^[A-Za-z0-9\-_/]+$")


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


def validate_register_number(register_number: str) -> str:
    value = register_number.strip().upper()
    if not value:
        raise ValidationError("Register number is required.")
    if len(value) > 50:
        raise ValidationError("Register number must be at most 50 characters.")
    if not REGISTER_NUMBER_PATTERN.match(value):
        raise ValidationError("Register number contains invalid characters.")
    return value


def validate_attendance_counts(classes_conducted: int, classes_attended: int) -> None:
    if classes_conducted < 0:
        raise ValidationError("Classes conducted cannot be negative.")
    if classes_attended < 0:
        raise ValidationError("Classes attended cannot be negative.")
    if classes_attended > classes_conducted:
        raise ValidationError("Classes attended cannot exceed classes conducted.")
