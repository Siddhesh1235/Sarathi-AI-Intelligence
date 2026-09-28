"""Schemas for multi-turn session state management in Sarathi AI."""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """Represents a single message turn in the conversation."""
    timestamp: float = Field(default_factory=time.time)
    role: str  # "citizen" or "assistant"
    text: str = ""
    intent: Optional[str] = None
    media_attached: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionState(BaseModel):
    """Active conversational session for a citizen on WhatsApp or Web."""
    session_id: str
    citizen_phone: str
    language: str = "mr"
    active_intent: Optional[str] = None
    pending_action: Optional[str] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)
    turns: List[ConversationTurn] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    last_active_at: float = Field(default_factory=time.time)

    def is_expired(self, ttl_seconds: int = 900) -> bool:
        """Checks if session has expired due to citizen inactivity (default 15 mins)."""
        return (time.time() - self.last_active_at) > ttl_seconds

    def touch(self) -> None:
        """Updates the last active timestamp."""
        self.last_active_at = time.time()
