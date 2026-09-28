"""Human Handoff and Call Center Escalation Agent for PCMC Sarathi AI."""

import logging
from typing import Dict, Any

from orchestration.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HandoffAgent(BaseAgent):
    """Domain agent managing citizen handoff to human officers and Sarathi Call Center."""

    def __init__(self):
        super().__init__(
            name="HandoffAgent",
            description="Manages escalation to PCMC Sarathi Call Center representatives (8888 00 6666)."
        )

    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Determines if the payload represents human escalation."""
        return payload.get("intent") == "HUMAN_ESCALATION"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Provides direct connection guidance to PCMC Sarathi Call Center."""
        lang = payload.get("language", "mr")

        if lang == "mr":
            msg = (
                "🎧 **PCMC सारथी कॉल सेंटर संपर्क:**\n\n"
                "आपल्याला महानगरपालिकेच्या थेट प्रतिनिधीशी बोलायचे असल्यास:\n\n"
                "• 📞 **टोल-फ्री हेल्पलाईन**: `8888 00 6666`\n"
                "• ⏰ **कॉल सेंटर वेळ**: दररोज सकाळी ७:०० ते रात्री ११:००\n"
                "• 📧 **ईमेल सहाय्य**: sarathi@pcmcindia.gov.in\n\n"
                "आपण वरील क्रमांकावर थेट डायल करून आमच्या ग्राहक प्रतिनिधीशी बोलू शकता."
            )
        else:
            msg = (
                "🎧 **PCMC Sarathi Call Center Escalation:**\n\n"
                "To speak directly with a municipal customer service representative:\n\n"
                "• 📞 **Toll-Free Helpline**: `8888 00 6666`\n"
                "• ⏰ **Operating Hours**: Daily from 7:00 AM to 11:00 PM\n"
                "• 📧 **Email Support**: sarathi@pcmcindia.gov.in\n\n"
                "Please dial the toll-free number to connect immediately."
            )

        return {
            "success": True,
            "escalated": True,
            "helpline": "8888 00 6666",
            "response_message": msg,
        }


# Singleton instance
handoff_agent = HandoffAgent()
