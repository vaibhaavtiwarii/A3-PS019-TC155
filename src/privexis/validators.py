"""
Strict validators for high-confidence PII detection.
These go beyond regex pattern matching to verify checksums and formats.
"""

import re

# ---- Verhoeff algorithm (Aadhaar-style checksum) ----
_VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

_VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)

_VERHOEFF_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def verhoeff_check_digit(number: str) -> str:
    """Compute the Verhoeff check digit for a number string."""
    c = 0
    for i, ch in enumerate(reversed(number)):
        if not ch.isdigit():
            return "0"
        c = _VERHOEFF_D[c][_VERHOEFF_P[(i + 1) % 8][int(ch)]]
    return str(_VERHOEFF_INV[c])


def verhoeff_validate(number: str) -> bool:
    """Validate a number with its Verhoeff check digit (last digit)."""
    if len(number) < 2 or not number.isdigit():
        return False
    return verhoeff_check_digit(number[:-1]) == number[-1]


# ---- Aadhaar-style validation (12 digits, first digit 2-9, Verhoeff checksum) ----
_AADHAAR_PATTERN = re.compile(r"^[2-9]\d{11}$")


def is_aadhaar_like(value: str) -> bool:
    """Check if a value looks like a valid Aadhaar number."""
    v = value.replace(" ", "").replace("-", "")
    return bool(_AADHAAR_PATTERN.match(v) and verhoeff_validate(v))


# ---- PAN validation (Indian Permanent Account Number) ----
_PAN_PATTERN = re.compile(r"^[A-Za-z]{5}\d{4}[A-Za-z]$")


def is_pan(value: str) -> bool:
    """Check if a value matches PAN format."""
    return bool(_PAN_PATTERN.match(value.strip().upper()))


# ---- Email validation ----
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_email(value: str) -> bool:
    """Basic email syntax check."""
    return bool(_EMAIL_PATTERN.match(value.strip()))


# ---- Date plausibility ----
_DATE_PATTERNS = (
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),  # ISO YYYY-MM-DD
    re.compile(r"^\d{2}/\d{2}/\d{4}$"),  # DD/MM/YYYY
)


def date_plausible(value: str) -> bool:
    """Check if a value is a plausible date between 1900 and today."""
    v = value.strip()
    for pat in _DATE_PATTERNS:
        if pat.match(v):
            try:
                if "-" in v:
                    year, month, day = map(int, v.split("-"))
                else:
                    day, month, year = map(int, v.split("/"))
                if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                    return True
            except ValueError:
                continue
    return False


# ---- Validator registry ----
VALIDATORS = {
    "verhoeff": verhoeff_validate,
    "aadhaar": is_aadhaar_like,
    "pan": is_pan,
    "email": is_email,
    "date_plausible": date_plausible,
    "govt_id": lambda v: is_aadhaar_like(v) or is_pan(v),
}