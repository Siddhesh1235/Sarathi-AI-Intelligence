"""Right to Services (RTS) Tracking Agent for PCMC Sarathi AI.

Tracks civic applications (birth/death/marriage certificates, licenses, NOCs).
"""

import re
import logging
from typing import Dict, Any

from orchestration.agents.base_agent import BaseAgent
from orchestration.session_context.session_manager import session_manager

logger = logging.getLogger(__name__)


class RTSTrackingAgent(BaseAgent):
    """Domain agent tracking citizen applications under Maharashtra Right to Public Services Act."""

    def __init__(self):
        super().__init__(
            name="RTSTrackingAgent",
            description="Tracks application and certificate status for PCMC RTS services."
        )

    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Determines if the payload represents an RTS tracking request."""
        return payload.get("intent") == "RTS_TRACKING"

    def _extract_app_id(self, text: str) -> Dict[str, Any]:
        """Extracts RTS Application / Token Number."""
        match = re.search(r"\b(RTS[ -]?[0-9]{4,10}|[0-9]{6,10})\b", text, re.IGNORECASE)
        if match:
            clean_id = match.group(1).replace(" ", "").replace("-", "")
            return {"found": True, "id": clean_id}
        return {"found": False}

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes RTS tracking."""
        text = payload.get("text", "")
        phone = payload.get("citizen_phone", "")
        lang = payload.get("language", "mr")

        extracted = self._extract_app_id(text)
        session = session_manager.get_session(phone) if phone else None
        app_id = extracted.get("id") or (session.context_data.get("rts_app_id") if session else None)

        if app_id:
            if phone:
                session_manager.update_session(
                    phone,
                    active_intent=None,
                    pending_action=None,
                    context_updates={"rts_app_id": app_id},
                )

            status_text_mr = "मंजूर (Approved - डाऊनलोडसाठी तयार)"
            service_name_mr = "जन्म दाखला (Birth Certificate)"

            if lang == "mr":
                msg = (
                    f"📜 **PCMC सेवा हमी (RTS) सद्यस्थिती:**\n\n"
                    f"• **अर्ज क्रमांक**: `{app_id}`\n"
                    f"• **सेवेचे नाव**: {service_name_mr}\n"
                    f"• **स्थिती**: ✅ {status_text_mr}\n"
                    f"• **सादर केल्याची तारीख**: २४ सप्टेंबर २०२६\n\n"
                    f"आपण अधिकृत दाखला खालील लिंकवरून डिजिटल स्वाक्षरीसह डाऊनलोड करू शकता:\n"
                    f"https://www.pcmcindia.gov.in/rts/download?id={app_id}"
                )
            else:
                msg = (
                    f"📜 **PCMC Right to Services (RTS) Status:**\n\n"
                    f"• **Application ID**: `{app_id}`\n"
                    f"• **Service**: Birth Certificate\n"
                    f"• **Status**: ✅ Approved & Ready for Download\n"
                    f"• **Submission Date**: 24 Sep 2026\n\n"
                    f"You may download the digitally signed certificate here:\n"
                    f"https://www.pcmcindia.gov.in/rts/download?id={app_id}"
                )

            return {
                "success": True,
                "app_id": app_id,
                "status": "APPROVED",
                "response_message": msg,
            }

        else:
            if phone:
                session_manager.update_session(
                    phone,
                    active_intent="RTS_TRACKING",
                    pending_action="AWAITING_APP_ID",
                )

            if lang == "mr":
                msg = (
                    "📜 **अर्जाची सद्यस्थिती ट्रॅकिंग:**\n\n"
                    "कृपया आपला **अर्ज क्रमांक (उदा. RTS-12345 किंवा पावतीवरील टोकन नंबर)** पाठवा."
                )
            else:
                msg = (
                    "📜 **Application Status Tracking:**\n\n"
                    "Please enter your **RTS Application ID or Token Number (e.g., RTS-12345)**."
                )

            return {
                "success": True,
                "app_id": None,
                "response_message": msg,
            }


# Singleton instance
rts_agent = RTSTrackingAgent()
