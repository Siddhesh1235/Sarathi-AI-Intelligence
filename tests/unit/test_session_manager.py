"""Unit tests for the SessionContextManager."""

import time
import pytest
from orchestration.session_context.session_manager import SessionContextManager


def test_session_lifecycle():
    manager = SessionContextManager(ttl_seconds=2)
    phone = "9822112233"

    # 1. Create session
    session = manager.get_or_create_session(phone, language="mr")
    assert session.citizen_phone == phone
    assert session.language == "mr"
    assert session.active_intent is None

    # 2. Update session
    manager.update_session(
        phone,
        active_intent="TEXT_GRIEVANCE",
        pending_action="AWAITING_MEDIA_OR_LOCATION",
        context_updates={"category": "PotHoles"},
    )
    retrieved = manager.get_session(phone)
    assert retrieved.active_intent == "TEXT_GRIEVANCE"
    assert retrieved.pending_action == "AWAITING_MEDIA_OR_LOCATION"
    assert retrieved.context_data.get("category") == "PotHoles"

    # 3. Add turns
    manager.add_turn(phone, role="citizen", text="खड्डा पडला आहे", intent="TEXT_GRIEVANCE")
    manager.add_turn(phone, role="assistant", text="कृपया फोटो किंवा ठिकाण पाठवा.")
    assert len(retrieved.turns) == 2

    # 4. Clear session
    manager.clear_session(phone)
    assert manager.get_session(phone) is None


def test_session_expiration():
    # TTL of 1 second
    manager = SessionContextManager(ttl_seconds=1)
    phone = "9822001122"

    manager.get_or_create_session(phone)
    assert manager.get_session(phone) is not None

    # Wait for expiration
    time.sleep(1.2)
    assert manager.get_session(phone) is None
