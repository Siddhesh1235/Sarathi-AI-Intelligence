"""Unit tests for Stage 4.1 Input Validator."""

from preprocessing.input_validator import InputValidator


def test_empty_payload_rejected():
    validator = InputValidator()
    result = validator.validate(text="", media_bytes=None)
    assert result.is_valid is False
    assert result.error_code == "EMPTY_PAYLOAD"


def test_empty_zero_byte_file_rejected():
    validator = InputValidator()
    result = validator.validate(text="Pothole photo", media_bytes=b"")
    assert result.is_valid is False
    assert result.error_code == "EMPTY_FILE"


def test_oversized_file_rejected():
    validator = InputValidator()
    # 16 MB dummy bytes
    oversized = b"0" * (16 * 1024 * 1024)
    result = validator.validate(text="Pothole", media_bytes=oversized)
    assert result.is_valid is False
    assert result.error_code == "FILE_TOO_LARGE"


def test_prohibited_extension_rejected():
    validator = InputValidator()
    result = validator.validate(
        text="Bill doc",
        media_bytes=b"dummy content",
        media_filename="invoice_receipt.exe",
    )
    assert result.is_valid is False
    assert result.error_code == "DANGEROUS_EXTENSION"


def test_invalid_phone_number_rejected():
    validator = InputValidator()
    # Invalid 5-digit number
    result = validator.validate(text="Hello", citizen_phone="12345")
    assert result.is_valid is False
    assert result.error_code == "INVALID_PHONE_NUMBER"


def test_valid_input_accepted():
    validator = InputValidator()
    result = validator.validate(
        text="Streetlight problem in Wakad",
        media_bytes=b"\xff\xd8\xff\xe0" + b"0" * 100,  # valid dummy jpeg header
        media_filename="light.jpg",
        media_mime_type="image/jpeg",
        citizen_phone="+919822112233",
    )
    assert result.is_valid is True
    assert result.error_message is None
