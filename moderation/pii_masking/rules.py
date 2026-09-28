"""Regex rules and validation algorithms (Verhoeff for Aadhaar) for PII detection."""

import re

# -------------------------------------------------------------
# Verhoeff Algorithm for 12-digit Aadhaar Number Validation
# Ensures only genuine Aadhaar checksums are masked, not random numbers.
# -------------------------------------------------------------
_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def validate_verhoeff_aadhaar(aadhaar_digits: str) -> bool:
    """Validates 12-digit Aadhaar number using Verhoeff checksum algorithm."""
    digits = re.sub(r"\D", "", aadhaar_digits)
    if len(digits) != 12 or digits[0] in ("0", "1"):
        return False

    c = 0
    reversed_digits = [int(d) for d in reversed(digits)]
    for i, num in enumerate(reversed_digits):
        c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][num]]
    return c == 0


# -------------------------------------------------------------
# Regular Expressions for Indian Municipal PII Entities
# -------------------------------------------------------------

# Aadhaar: 12 digits, optional spaces or dashes (e.g., 2345 6789 0123)
AADHAAR_REGEX = re.compile(r"\b([2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4})\b")

# PAN Card: 5 uppercase letters + 4 digits + 1 uppercase letter (e.g., ABCDE1234F)
PAN_REGEX = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", re.IGNORECASE)

# Indian Mobile Phone Numbers: Optional +91 / 91 / 0, starts with 6-9, exactly 10 digits
PHONE_REGEX = re.compile(r"(?:(?:\+91|91|0)[-.\s]?)?([6-9]\d{9})\b")

# Email Address
EMAIL_REGEX = re.compile(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")

# Bank IFSC Code: 4 letters + 0 + 6 alphanumeric (e.g., SBIN0001234, HDFC0000456)
IFSC_REGEX = re.compile(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", re.IGNORECASE)

# Bank Account Numbers: 9 to 18 digits preceded by banking keywords in English or Marathi
BANK_ACCOUNT_REGEX = re.compile(
    r"(?i)\b(?:a/c|acc|account|khate|खाते|खाते क्रमांक|a/c no|acc no\.?)\s*[:#\-]?\s*([0-9]{9,18})\b"
)
