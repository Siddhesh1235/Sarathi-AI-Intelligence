"""Shared configuration and settings for Sarathi AI."""

import os
from typing import List, Optional
from pydantic import BaseModel, Field


class ModerationSettings(BaseModel):
    """Configuration settings for Content Moderation."""
    # Feature Flags
    enable_pii_masking: bool = True
    enable_profanity_filter: bool = True
    enable_prompt_injection_check: bool = True
    enable_file_validation: bool = True
    enable_output_moderation: bool = True

    # Strictness & Thresholds
    profanity_sensitivity: float = Field(default=0.8, ge=0.0, le=1.0)
    prompt_injection_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_file_size_bytes: int = 15 * 1024 * 1024  # 15 MB limit (WhatsApp limit)
    allowed_mime_types: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
        "audio/ogg",
        "audio/opus",
        "audio/wav",
        "audio/mp3",
        "video/mp4",
    ]


class Settings(BaseModel):
    """Global Application Settings."""
    app_name: str = "Sarathi AI - PCMC Civic Intelligence"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    moderation: ModerationSettings = Field(default_factory=ModerationSettings)


# Global settings singleton
settings = Settings()
