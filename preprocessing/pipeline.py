"""Preprocessing Pipeline: Coordinates Stage 4.1 Input Validation and Stage 4.2 Preprocessing."""

import uuid
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any

from preprocessing.schemas import (
    ValidationResult,
    PreprocessedPayload,
    ExtractedEXIF,
)
from preprocessing.input_validator import InputValidator
from preprocessing.text_normalizer import TextNormalizer
from preprocessing.image_preprocessor import ImagePreprocessor


class PreprocessingPipeline:
    """
    Coordinates Input Validation (4.1) and Data Preprocessing (4.2)
    before handing off to Gatekeeper Content Moderation (4.3).
    """

    def __init__(self):
        self.validator = InputValidator()
        self.text_normalizer = TextNormalizer()
        self.image_preprocessor = ImagePreprocessor()

    def process(self, raw_input: Dict[str, Any]) -> Tuple[bool, Optional[PreprocessedPayload], Optional[str]]:
        """
        Executes validation followed by normalization and enrichment.
        
        Returns:
            (success: bool, preprocessed_payload: Optional[PreprocessedPayload], error_message: Optional[str])
        """
        text = raw_input.get("text")
        media_bytes = raw_input.get("media_bytes")
        media_filename = raw_input.get("media_filename")
        media_mime = raw_input.get("media_mime_type")
        phone = raw_input.get("citizen_phone")
        lang = raw_input.get("language", "mr")

        # -------------------------------------------------------------
        # Step 4.1: Input Validation
        # -------------------------------------------------------------
        val_result: ValidationResult = self.validator.validate(
            text=text,
            media_bytes=media_bytes,
            media_filename=media_filename,
            media_mime_type=media_mime,
            citizen_phone=phone,
        )

        if not val_result.is_valid:
            return False, None, val_result.error_message

        # -------------------------------------------------------------
        # Step 4.2: Data Preprocessing & Enrichment
        # -------------------------------------------------------------
        # 1. Generate unique correlation request ID and server timestamp
        req_date = datetime.now(timezone.utc).strftime("%Y%m%d")
        unique_suffix = uuid.uuid4().hex[:8].upper()
        request_id = f"REQ-{req_date}-{unique_suffix}"
        iso_timestamp = datetime.now(timezone.utc).isoformat()

        # 2. Text Normalization
        normalized_text = self.text_normalizer.normalize(text or "")

        # 3. Image Preprocessing & EXIF extraction
        processed_image_bytes = None
        exif_data = None
        has_media = bool(media_bytes)

        if has_media and media_bytes:
            try:
                # Check if it's an image format by mime or extension
                is_image = True
                if media_mime and not media_mime.startswith("image/"):
                    is_image = False
                elif media_filename and not media_filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    is_image = False

                if is_image:
                    processed_image_bytes, exif_data = self.image_preprocessor.process(media_bytes)
                else:
                    processed_image_bytes = media_bytes
            except Exception:
                # If image processing fails (e.g. non-image attachment like PDF), keep raw bytes
                processed_image_bytes = media_bytes

        payload = PreprocessedPayload(
            request_id=request_id,
            timestamp=iso_timestamp,
            normalized_text=normalized_text,
            has_media=has_media,
            image_bytes=processed_image_bytes,
            media_filename=media_filename,
            media_mime_type=media_mime,
            exif_data=exif_data,
            citizen_phone=phone,
            language=lang,
        )

        return True, payload, None


# Pipeline singleton instance
preprocessing_pipeline = PreprocessingPipeline()
