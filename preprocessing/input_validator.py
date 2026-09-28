"""Stage 4.1: Input Validator for PCMC Sarathi AI.

Performs immediate technical verification of incoming citizen payloads before any AI processing.
"""

import os
import re
from typing import Optional
from preprocessing.schemas import ValidationResult
from shared.config.settings import settings

DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".dll", ".so", ".bin", ".py", ".js", ".vbs",
    ".ps1", ".jar", ".apk", ".msi", ".scr", ".com", ".pif"
}

INDIAN_PHONE_REGEX = re.compile(r"^(?:(?:\+91|91|0)?[6-9]\d{9})$")


class InputValidator:
    """Validates raw citizen input requests for format, payload integrity, and size limits."""

    def __init__(self):
        self.max_size_bytes = settings.moderation.max_file_size_bytes
        self.allowed_mimes = set(settings.moderation.allowed_mime_types)

    def validate(
        self,
        text: Optional[str] = None,
        media_bytes: Optional[bytes] = None,
        media_filename: Optional[str] = None,
        media_mime_type: Optional[str] = None,
        citizen_phone: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validates incoming request parameters.
        
        Returns:
            ValidationResult(is_valid: bool, error_message: Optional[str], error_code: Optional[str])
        """
        has_text = bool(text and text.strip())
        has_media = (media_bytes is not None) or bool(media_filename)

        # 1. Payload Sanity: Must contain at least text OR media
        if not has_text and not has_media:
            return ValidationResult(
                is_valid=False,
                error_message="Request payload is empty. Please provide text or an attachment.",
                error_code="EMPTY_PAYLOAD",
            )

        # 2. File Validation (if media is provided)
        if has_media:
            # Check empty file (0 bytes)
            if media_bytes is not None and len(media_bytes) == 0:
                return ValidationResult(
                    is_valid=False,
                    error_message="Uploaded file is empty (0 bytes).",
                    error_code="EMPTY_FILE",
                )

            # Check file size limit (15 MB)
            if media_bytes is not None and len(media_bytes) > self.max_size_bytes:
                max_mb = self.max_size_bytes / (1024 * 1024)
                return ValidationResult(
                    is_valid=False,
                    error_message=f"File size exceeds permitted limit of {max_mb:.0f}MB.",
                    error_code="FILE_TOO_LARGE",
                )

            # Check dangerous file extensions
            if media_filename:
                _, ext = os.path.splitext(media_filename.lower())
                if ext in DANGEROUS_EXTENSIONS:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"File extension '{ext}' is prohibited for security reasons.",
                        error_code="DANGEROUS_EXTENSION",
                    )

            # Check MIME type if provided
            if media_mime_type:
                clean_mime = media_mime_type.lower().split(";")[0].strip()
                if clean_mime not in self.allowed_mimes:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Unsupported file format '{clean_mime}'. Allowed formats: JPEG, PNG, WebP, PDF, Audio.",
                        error_code="UNSUPPORTED_MIME_TYPE",
                    )

        # 3. Phone Number Validation (if provided)
        if citizen_phone:
            clean_phone = re.sub(r"[\s\-]", "", citizen_phone)
            if not INDIAN_PHONE_REGEX.match(clean_phone):
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid mobile phone number. Must be a valid 10-digit Indian number.",
                    error_code="INVALID_PHONE_NUMBER",
                )

        return ValidationResult(is_valid=True)
