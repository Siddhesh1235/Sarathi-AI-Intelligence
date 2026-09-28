"""Billing and Tax Agent for PCMC Sarathi AI.

Processes Property Tax (घरपट्टी) and Water Supply Bills (पाणीपट्टी),
generates secure payment links, and manages multi-turn billing inquiries.
"""

import re
import logging
from typing import Dict, Any

from orchestration.agents.base_agent import BaseAgent
from orchestration.session_context.session_manager import session_manager

logger = logging.getLogger(__name__)


class BillingAgent(BaseAgent):
    """Domain agent managing property tax, water billing inquiries, and payment links."""

    def __init__(self):
        super().__init__(
            name="BillingAgent",
            description="Queries property tax and water bills, checks dues, and generates PCMC payment links."
        )

    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Determines if the payload is a billing or tax inquiry."""
        return payload.get("intent") == "BILLING_TAX"

    def _extract_id(self, text: str) -> Dict[str, Any]:
        """Extracts Property ID or Water Consumer Number from citizen input."""
        # e.g., PT-123456 or 6-10 digit numbers
        match_pt = re.search(r"\b(PT[ -]?[0-9]{4,8}|[0-9]{6,10})\b", text, re.IGNORECASE)
        if match_pt:
            val = match_pt.group(1).replace(" ", "").replace("-", "")
            return {"found": True, "type": "property" if "PT" in match_pt.group(1).upper() else "consumer", "id": val}
        return {"found": False}

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes billing inquiry:
        1. Checks for property ID or consumer number in text or session.
        2. If missing, requests the identifier.
        3. If present, returns bill summary and payment gateway link.
        """
        text = payload.get("text", "")
        phone = payload.get("citizen_phone", "")
        lang = payload.get("language", "mr")

        extracted = self._extract_id(text)
        session = session_manager.get_session(phone) if phone else None

        billing_id = extracted.get("id") or (session.context_data.get("billing_id") if session else None)

        if billing_id:
            # Clear pending action in session
            if phone:
                session_manager.update_session(
                    phone,
                    active_intent=None,
                    pending_action=None,
                    context_updates={"billing_id": billing_id},
                )

            # Simulated PCMC portal response (will integrate with MCP Property Tax Server)
            due_amount = 4250.00
            discount_amount = 212.50
            net_payable = due_amount - discount_amount
            payment_url = f"https://www.pcmcindia.gov.in/epay?id={billing_id}"

            if lang == "mr":
                msg = (
                    f"💰 **PCMC कर व देयक तपशील:**\n\n"
                    f"• **ग्राहक/मालमत्ता क्रमांक**: `{billing_id}`\n"
                    f"• **एकूण देयक रक्कम**: ₹{due_amount:,.2f}\n"
                    f"• **सवलत (५% वेळेत भरणा)**: -₹{discount_amount:,.2f}\n"
                    f"• **निव्वळ देय रक्कम**: *₹{net_payable:,.2f}*\n"
                    f"• **अंतिम मुदत**: ३१ ऑक्टोबर २०२६\n\n"
                    f"💳 **सुरक्षित ऑनलाईन भरणा करा:**\n"
                    f"{payment_url}\n\n"
                    f"भरणा केल्यानंतर पावती त्वरित याच चॅटवर उपलब्ध होईल."
                )
            else:
                msg = (
                    f"💰 **PCMC Tax & Billing Details:**\n\n"
                    f"• **Property/Consumer ID**: `{billing_id}`\n"
                    f"• **Total Bill Amount**: ₹{due_amount:,.2f}\n"
                    f"• **Early Bird Rebate (5%)**: -₹{discount_amount:,.2f}\n"
                    f"• **Net Payable**: *₹{net_payable:,.2f}*\n"
                    f"• **Due Date**: 31 Oct 2026\n\n"
                    f"💳 **Pay Online Securely:**\n"
                    f"{payment_url}\n\n"
                    f"Receipt will be generated instantly upon payment confirmation."
                )

            return {
                "success": True,
                "billing_id": billing_id,
                "net_payable": net_payable,
                "payment_url": payment_url,
                "response_message": msg,
            }

        else:
            if phone:
                session_manager.update_session(
                    phone,
                    active_intent="BILLING_TAX",
                    pending_action="AWAITING_BILLING_ID",
                )

            if lang == "mr":
                msg = (
                    "💰 **PCMC कर व देयक सेवा:**\n\n"
                    "आपली थकबाकी जाणून घेण्यासाठी व सुरक्षित पेमेंट लिंक मिळवण्यासाठी कृपया आपला "
                    "**मालमत्ता क्रमांक (उदा. PT-123456)** किंवा **पाणी ग्राहक क्रमांक** पाठवा."
                )
            else:
                msg = (
                    "💰 **PCMC Tax & Billing Service:**\n\n"
                    "To fetch your current dues and generate a secure payment link, please enter your "
                    "**Property ID (e.g., PT-123456)** or **Water Consumer Number**."
                )

            return {
                "success": True,
                "billing_id": None,
                "response_message": msg,
            }


# Singleton instance
billing_agent = BillingAgent()
