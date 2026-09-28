"""Pydantic schemas for Content Moderation requests, results, and audit trails."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ViolationCategory(str, Enum):
    """Categories of moderation violations."""
    NONE = "NONE"
    PII_EXPOSURE = "PII_EXPOSURE"
    PROFANITY_ABUSE = "PROFANITY_ABUSE"
    HATE_SPEECH = "HATE_SPEECH"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    JAILBREAK_ATTEMPT = "JAILBREAK_ATTEMPT"
    HARMFUL_ILLEGAL = "HARMFUL_ILLEGAL"
    UNSAFE_FILE = "UNSAFE_FILE"
    SPAM_FLOODING = "SPAM_FLOODING"


class SafetyStatus(str, Enum):
    """Overall safety decision."""
    SAFE = "SAFE"
    SANITIZED_SAFE = "SANITIZED_SAFE"  # Safe after PII was redacted
    UNSAFE = "UNSAFE"                  # Blocked due to violations


class ChannelType(str, Enum):
    """Citizen input channels."""
    WHATSAPP = "whatsapp"
    WEB_PORTAL = "web_portal"
    VOICE_NOTE = "voice_note"


class MaskedEntity(BaseModel):
    """Details of a masked sensitive PII entity."""
    entity_type: str = Field(description="Type of entity: AADHAAR, PAN, PHONE, EMAIL, BANK_ACC")
    masked_text: str = Field(description="Redacted representation")


class CitizenInputPayload(BaseModel):
    """Citizen incoming input payload."""
    citizen_phone: Optional[str] = Field(default=None, description="Citizen WhatsApp number")
    text: Optional[str] = Field(default="", description="Citizen text or transcribed voice note")
    language: str = Field(default="mr", description="Detected or preferred language: mr, hi, en")
    channel: ChannelType = Field(default=ChannelType.WHATSAPP)
    media_filename: Optional[str] = None
    media_mime_type: Optional[str] = None
    media_size_bytes: Optional[int] = None
    location_coords: Optional[Dict[str, float]] = None  # {"lat": 18.62, "lng": 73.81}


class ModerationCheckResponse(BaseModel):
    """Response returned by the master moderation pipeline."""
    is_safe: bool = Field(description="True if safe to proceed to AI Orchestrator / Agents")
    status: SafetyStatus = Field(description="SAFE, SANITIZED_SAFE, or UNSAFE")
    original_text: str = Field(description="Original citizen text before moderation")
    cleaned_text: str = Field(description="Sanitized and PII-masked text ready for LLM/Agents")
    detected_language: str = Field(default="mr")
    violations: List[ViolationCategory] = Field(default_factory=list)
    masked_entities: List[MaskedEntity] = Field(default_factory=list)
    polite_warning: Optional[str] = Field(
        default=None,
        description="Polite, respectful notification for the citizen if blocked"
    )
    audit_log: Dict[str, Any] = Field(default_factory=dict, description="Metadata for CERT-In audit logs")


class OutputModerationPayload(BaseModel):
    """Model response payload to be checked before sending to citizen."""
    raw_response: str
    target_language: str = "mr"
    citizen_phone: Optional[str] = None


class OutputModerationResponse(BaseModel):
    """Result of output verification."""
    is_safe: bool
    safe_response: str
    pii_redacted_count: int = 0
    formatted_for_whatsapp: bool = True
