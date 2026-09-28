"""Session Context Manager for Multi-turn Conversations in Sarathi AI.

Maintains conversation history and pending actions per citizen phone number
with TTL expiration (15 minutes WhatsApp standard).
"""

import time
import logging
from threading import Lock
from typing import Dict, Any, Optional

from orchestration.session_context.schemas import SessionState, ConversationTurn

logger = logging.getLogger(__name__)


class SessionContextManager:
    """Thread-safe multi-turn session storage and manager."""

    def __init__(self, ttl_seconds: int = 900):
        self._sessions: Dict[str, SessionState] = {}
        self._lock = Lock()
        self.ttl_seconds = ttl_seconds

    def _evict_if_expired(self, citizen_phone: str) -> bool:
        """Evicts a session if it has passed its TTL. Internal use with lock held."""
        session = self._sessions.get(citizen_phone)
        if session and session.is_expired(self.ttl_seconds):
            logger.info("Session for citizen %s expired after %ds of inactivity", citizen_phone, self.ttl_seconds)
            del self._sessions[citizen_phone]
            return True
        return False

    def get_session(self, citizen_phone: str) -> Optional[SessionState]:
        """Retrieves active session if present and not expired."""
        if not citizen_phone:
            return None

        with self._lock:
            if self._evict_if_expired(citizen_phone):
                return None
            session = self._sessions.get(citizen_phone)
            if session:
                session.touch()
            return session

    def get_or_create_session(self, citizen_phone: str, language: str = "mr") -> SessionState:
        """Retrieves existing active session or creates a new one."""
        if not citizen_phone:
            # Fallback anonymous session
            return SessionState(
                session_id=f"anon-{int(time.time() * 1000)}",
                citizen_phone="anonymous",
                language=language,
            )

        with self._lock:
            self._evict_if_expired(citizen_phone)
            session = self._sessions.get(citizen_phone)
            if not session:
                session = SessionState(
                    session_id=f"sess-{citizen_phone}-{int(time.time())}",
                    citizen_phone=citizen_phone,
                    language=language,
                )
                self._sessions[citizen_phone] = session
                logger.debug("Created new session for citizen %s", citizen_phone)
            else:
                session.touch()
                if language:
                    session.language = language
            return session

    def update_session(
        self,
        citizen_phone: str,
        active_intent: Optional[str] = None,
        pending_action: Optional[str] = None,
        context_updates: Optional[Dict[str, Any]] = None,
    ) -> Optional[SessionState]:
        """Updates intent, pending action, and context variables for a session."""
        if not citizen_phone:
            return None

        with self._lock:
            session = self._sessions.get(citizen_phone)
            if not session:
                return None

            session.touch()
            if active_intent is not None:
                session.active_intent = active_intent
            if pending_action is not None:
                session.pending_action = pending_action
            if context_updates:
                session.context_data.update(context_updates)

            return session

    def add_turn(
        self,
        citizen_phone: str,
        role: str,
        text: str = "",
        intent: Optional[str] = None,
        media_attached: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Appends a conversation turn to the citizen's session history."""
        if not citizen_phone:
            return

        with self._lock:
            session = self._sessions.get(citizen_phone)
            if not session:
                return

            turn = ConversationTurn(
                role=role,
                text=text,
                intent=intent,
                media_attached=media_attached,
                metadata=metadata or {},
            )
            session.turns.append(turn)
            # Retain maximum 20 turns per session to conserve memory
            if len(session.turns) > 20:
                session.turns = session.turns[-20:]
            session.touch()

    def clear_session(self, citizen_phone: str) -> None:
        """Terminates and purges the citizen's session."""
        if not citizen_phone:
            return

        with self._lock:
            if citizen_phone in self._sessions:
                del self._sessions[citizen_phone]
                logger.debug("Cleared session for citizen %s", citizen_phone)

    def cleanup_all_expired(self) -> int:
        """Scans and clears all expired sessions across the system."""
        with self._lock:
            expired_keys = [
                phone for phone, session in self._sessions.items()
                if session.is_expired(self.ttl_seconds)
            ]
            for phone in expired_keys:
                del self._sessions[phone]
            return len(expired_keys)


# Global singleton instance
session_manager = SessionContextManager()
