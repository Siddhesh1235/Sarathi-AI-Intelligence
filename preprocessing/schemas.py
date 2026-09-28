"""Data schemas for Input Validation and Preprocessing."""

from typing import Optional
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Result of Stage 4.1 Input Validation."""
    is_valid: bool
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class ExtractedEXIF(BaseModel):
    """Camera metadata and GPS coordinates extracted from citizen photos."""
    has_gps: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capture_time: Optional[str] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None


class PreprocessedPayload(BaseModel):
    """Cleaned, normalized, and enriched citizen payload ready for Gatekeeper Moderation."""
    request_id: str = Field(description="Unique correlation ID for tracing")
    timestamp: str = Field(description="ISO-8601 server timestamp")
    normalized_text: str = Field(default="", description="Sanitized and whitespace-normalized text")
    has_media: bool = False
    image_bytes: Optional[bytes] = None
    media_filename: Optional[str] = None
    media_mime_type: Optional[str] = None
    exif_data: Optional[ExtractedEXIF] = None
    citizen_phone: Optional[str] = None
    language: str = "mr"
