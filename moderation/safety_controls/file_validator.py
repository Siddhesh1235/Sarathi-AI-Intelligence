"""File format, size, and extension validator for citizen attachments."""

import os
from typing import Tuple, Optional
from shared.config.settings import settings

DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".dll", ".so", ".bin", ".py", ".js", ".vbs",
    ".ps1", ".jar", ".apk", ".msi", ".scr", ".com", ".pif"
}


class FileValidator:
    """Validates citizen uploaded documents, photos, audio, and videos."""

    def __init__(self):
        self.max_size = settings.moderation.max_file_size_bytes
        self.allowed_mimes = set(settings.moderation.allowed_mime_types)

    def validate(
        self,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        size_bytes: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates the file attributes.
        
        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        # 1. Check size limit
        if size_bytes is not None and size_bytes > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            return False, f"File size exceeds maximum permitted limit of {max_mb:.0f}MB."

        # 2. Check dangerous extensions
        if filename:
            _, ext = os.path.splitext(filename.lower())
            if ext in DANGEROUS_EXTENSIONS:
                return False, f"Executable or script file type '{ext}' is prohibited."

        # 3. Check MIME type if provided
        if mime_type:
            clean_mime = mime_type.lower().split(";")[0].strip()
            if clean_mime not in self.allowed_mimes:
                return False, f"MIME type '{clean_mime}' is not supported. Please upload PDF, JPEG, PNG, MP4, or Audio."

        return True, None
