import re

from app.utils.exceptions import ValidationError

REGISTER_NUMBER_PATTERN = re.compile(r"^[A-Za-z0-9\-_/]+$")
SCIENTIFIC_NOTATION_PATTERN = re.compile(r"^[\d.]+\s*[Ee]\s*[+-]?\d+$")


def _clean_text(value: str) -> str:
    return value.replace("\ufeff", "").replace("\u00a0", "").strip()


def normalize_register_number_input(value: object) -> str:
    if value is None:
        raise ValidationError("Register number is missing.")

    if isinstance(value, int):
        text = str(value)
    elif isinstance(value, float):
        if value != value:  # NaN
            raise ValidationError("Register number is missing.")
        text = f"{value:.0f}" if value.is_integer() else str(value)
    else:
        text = _clean_text(str(value))

    if not text or text.lower() == "nan":
        raise ValidationError("Register number is missing.")

    if "E" in text.upper() and SCIENTIFIC_NOTATION_PATTERN.match(text.replace(" ", "")):
        raise ValidationError(
            "Register number is in scientific notation (for example 6.13524E+11). "
            "In Excel, select the Register Number column, set format to Text, re-enter the values, "
            "then export again."
        )

    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]

    return validate_register_number(text)


def validate_register_number(register_number: str) -> str:
    value = _clean_text(register_number).upper()
    if not value:
        raise ValidationError("Register number is required.")
    if len(value) > 50:
        raise ValidationError("Register number must be at most 50 characters.")
    if not REGISTER_NUMBER_PATTERN.match(value):
        raise ValidationError("Register number contains invalid characters.")
    return value
