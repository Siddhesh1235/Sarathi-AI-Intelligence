"""Unit tests for the Master Intent Router Agent."""

import pytest
from orchestration.agents.router_agent import (
    RouterAgent,
    IntentType,
    RouterDispatchResponse,
)
from moderation.schemas import SafetyStatus


@pytest.fixture
def router():
    return RouterAgent()


def test_intent_classification(router):
    # Greeting
    assert router.classify_intent("नमस्कार, मला मदत हवी आहे", False) == IntentType.GREETING
    assert router.classify_intent("Hi there", False) == IntentType.GREETING

    # Billing & Tax
    assert router.classify_intent("माझे पाणी बिल किती आहे?", False) == IntentType.BILLING_TAX
    assert router.classify_intent("Property tax payment receipt", False) == IntentType.BILLING_TAX

    # Text Grievance
    assert router.classify_intent("आमच्या रस्त्यावर खूप खड्डा पडला आहे", False) == IntentType.TEXT_GRIEVANCE
    assert router.classify_intent("Streetlight light band ahe", False) == IntentType.TEXT_GRIEVANCE

    # RTS Tracking
    assert router.classify_intent("जन्म दाखला अर्जाची स्थिती तपासायची आहे", False) == IntentType.RTS_TRACKING

    # Human Escalation
    assert router.classify_intent("मला कॉल सेंटर प्रतिनिधीशी बोलायचे आहे", False) == IntentType.HUMAN_ESCALATION

    # Media presence overrides text
    assert router.classify_intent("pothole info", has_media=True) == IntentType.MEDIA_GRIEVANCE


@pytest.mark.asyncio
async def test_router_execution_safe_greeting(router):
    payload = {
        "text": "नमस्कार",
        "citizen_phone": "9822112233",
        "language": "mr",
    }
    result: RouterDispatchResponse = await router.execute(payload)
    assert result.success is True
    assert result.detected_intent == IntentType.GREETING
    assert result.routed_to_agent == "RouterAgent"
    assert "Sarathi AI" in result.response_message


@pytest.mark.asyncio
async def test_router_execution_with_pii_masking(router):
    payload = {
        "text": "माझे पाणी बिल सांगा, माझा फोन 9822334455 आहे",
        "citizen_phone": "9822334455",
        "language": "mr",
    }
    result: RouterDispatchResponse = await router.execute(payload)
    assert result.success is True
    assert result.detected_intent == IntentType.BILLING_TAX
    assert result.routed_to_agent == "BillingAgent"
    assert result.safety_status == SafetyStatus.SANITIZED_SAFE


@pytest.mark.asyncio
async def test_router_execution_blocked_abusive(router):
    payload = {
        "text": "are bhadvya lavdya kam kar",
        "citizen_phone": "9822000000",
        "language": "mr",
    }
    result: RouterDispatchResponse = await router.execute(payload)
    assert result.success is False
    assert result.routed_to_agent == "ModerationAgent"
    assert result.safety_status == SafetyStatus.UNSAFE
    assert "सभ्य भाषेत" in result.response_message


@pytest.mark.asyncio
async def test_router_multiturn_grievance_flow(router):
    from orchestration.session_context.session_manager import session_manager
    phone = "9822998877"
    session_manager.clear_session(phone)

    # Turn 1: Citizen reports a pothole without location
    payload_1 = {
        "text": "आमच्या रस्त्यावर खूप मोठा खड्डा पडला आहे",
        "citizen_phone": phone,
        "language": "mr",
    }
    res_1: RouterDispatchResponse = await router.execute(payload_1)
    assert res_1.success is True
    assert res_1.detected_intent == IntentType.TEXT_GRIEVANCE
    assert res_1.routed_to_agent == "GrievanceAgent"
    assert "परिसराचे नाव" in res_1.response_message

    # Turn 2: Citizen provides locality "Wakad"
    payload_2 = {
        "text": "Wakad chinchwad road",
        "citizen_phone": phone,
        "language": "mr",
    }
    res_2: RouterDispatchResponse = await router.execute(payload_2)
    assert res_2.success is True
    assert res_2.detected_intent == IntentType.TEXT_GRIEVANCE
    assert res_2.routed_to_agent == "GrievanceAgent"
    assert "तक्रार यशस्वीरित्या नोंदवली आहे" in res_2.response_message
    assert "PCMC-" in res_2.response_message
    assert res_2.metadata.get("ticket_id") is not None


@pytest.mark.asyncio
async def test_router_multiturn_billing_flow(router):
    from orchestration.session_context.session_manager import session_manager
    phone = "9822556677"
    session_manager.clear_session(phone)

    # Turn 1: Citizen asks for property tax
    payload_1 = {
        "text": "मला घरपट्टी भरायची आहे",
        "citizen_phone": phone,
        "language": "mr",
    }
    res_1: RouterDispatchResponse = await router.execute(payload_1)
    assert res_1.success is True
    assert res_1.detected_intent == IntentType.BILLING_TAX
    assert res_1.routed_to_agent == "BillingAgent"
    assert "मालमत्ता क्रमांक" in res_1.response_message

    # Turn 2: Citizen inputs property number
    payload_2 = {
        "text": "माझा नंबर PT-100234 आहे",
        "citizen_phone": phone,
        "language": "mr",
    }
    res_2: RouterDispatchResponse = await router.execute(payload_2)
    assert res_2.success is True
    assert res_2.routed_to_agent == "BillingAgent"
    assert "देयक तपशील" in res_2.response_message
    assert "PT100234" in res_2.response_message
    assert "epay" in res_2.response_message


@pytest.mark.asyncio
async def test_router_rts_and_escalation_flows(router):
    phone = "9822443322"

    # RTS Tracking
    rts_payload = {
        "text": "माझ्या जन्म दाखल्याच्या अर्जाची स्थिती RTS-889900 काय आहे?",
        "citizen_phone": phone,
        "language": "mr",
    }
    rts_res: RouterDispatchResponse = await router.execute(rts_payload)
    assert rts_res.success is True
    assert rts_res.detected_intent == IntentType.RTS_TRACKING
    assert rts_res.routed_to_agent == "RTSTrackingAgent"
    assert "मंजूर" in rts_res.response_message

    # Human Escalation
    esc_payload = {
        "text": "मला कॉल सेंटर प्रतिनिधीशी बोलायचे आहे",
        "citizen_phone": phone,
        "language": "mr",
    }
    esc_res: RouterDispatchResponse = await router.execute(esc_payload)
    assert esc_res.success is True
    assert esc_res.detected_intent == IntentType.HUMAN_ESCALATION
    assert esc_res.routed_to_agent == "HandoffAgent"
    assert "8888 00 6666" in esc_res.response_message

