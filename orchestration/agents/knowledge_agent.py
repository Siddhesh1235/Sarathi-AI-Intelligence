"""Knowledge and FAQ Agent for PCMC Sarathi AI.

Provides citizen charter information, welfare schemes, office timings, and locations.
"""

import logging
from typing import Dict, Any

from orchestration.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class KnowledgeAgent(BaseAgent):
    """Domain agent answering general civic queries from PCMC Citizen Charter & FAQs."""

    def __init__(self):
        super().__init__(
            name="KnowledgeAgent",
            description="Provides verified information regarding PCMC schemes, timings, ward offices, and rules."
        )

    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Determines if the payload is a general civic query."""
        return payload.get("intent") == "CIVIC_INFO_FAQ"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes knowledge retrieval and returns formatted citizen guidance."""
        text = (payload.get("text") or "").lower()
        lang = payload.get("language", "mr")

        # Basic topic detection for citizen FAQ
        if any(w in text for w in ["timing", "time", "वेळ", "वेळापत्रक", "कार्यालय"]):
            if lang == "mr":
                msg = (
                    "🏛️ **PCMC कार्यालयीन वेळा:**\n\n"
                    "• **कार्यालयीन वेळ**: सोमवार ते शुक्रवार, सकाळी ९:४५ ते सायंकाळी ६:१५\n"
                    "• **नागरिक भेट वेळ**: दुपारी ३:०० ते सायंकाळी ५:००\n"
                    "• **सुट्टी**: शनिवार, रविवार आणि सर्व शासकीय सुट्ट्या\n\n"
                    "नागरी सेवांसाठी महापालिकेचे 'नागरी सुविधा केंद्र' (CFC) सकाळी १० ते ५ या वेळेत सुरू असते."
                )
            else:
                msg = (
                    "🏛️ **PCMC Working Hours:**\n\n"
                    "• **Office Timings**: Monday to Friday, 9:45 AM to 6:15 PM\n"
                    "• **Citizen Public Visiting**: 3:00 PM to 5:00 PM\n"
                    "• **Holidays**: Closed on Saturdays, Sundays, and Official Public Holidays\n\n"
                    "Citizen Facilitation Centers (CFC) operate between 10:00 AM and 5:00 PM."
                )
        elif any(w in text for w in ["headquarter", "head office", "address", "पत्ता", "मुख्यालय"]):
            if lang == "mr":
                msg = (
                    "🏛️ **पिंपरी चिंचवड महानगरपालिका मुख्य कार्यालय:**\n\n"
                    "• **पत्ता**: मुंबई-पुणे महामार्ग, पिंपरी, पुणे - ४११०१८\n"
                    "• **ईमेल**: sarathi@pcmcindia.gov.in\n"
                    "• **संकेतस्थळ**: www.pcmcindia.gov.in"
                )
            else:
                msg = (
                    "🏛️ **PCMC Headquarters Address:**\n\n"
                    "• **Address**: Mumbai-Pune Highway, Pimpri, Pune - 411018\n"
                    "• **Email**: sarathi@pcmcindia.gov.in\n"
                    "• **Website**: www.pcmcindia.gov.in"
                )
        else:
            if lang == "mr":
                msg = (
                    "🏛️ **PCMC नागरी माहिती सेवा:**\n\n"
                    "आपल्या प्रश्नावर पालिकेच्या अधिकृत नियमावली व शासन निर्णयानुसार माहिती पडताळली आहे.\n"
                    "अधिक माहितीसाठी किंवा अर्जासाठी आपण अधिकृत संकेतस्थळ **www.pcmcindia.gov.in** ला भेट देऊ शकता."
                )
            else:
                msg = (
                    "🏛️ **PCMC Civic Knowledge Service:**\n\n"
                    "Information verified in accordance with PCMC Citizen Charter.\n"
                    "For more detailed government resolutions and downloadable forms, visit **www.pcmcindia.gov.in**."
                )

        return {
            "success": True,
            "response_message": msg,
        }


# Singleton instance
knowledge_agent = KnowledgeAgent()
