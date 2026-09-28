"""Grievance Agent for PCMC Sarathi AI.

Handles civic complaints, ticket generation, SLA assignment, and multi-turn location collection.
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, Any

from orchestration.agents.base_agent import BaseAgent
from orchestration.session_context.session_manager import session_manager

logger = logging.getLogger(__name__)


class GrievanceAgent(BaseAgent):
    """Domain agent managing civic grievances (potholes, garbage, streetlights, drainage)."""

    def __init__(self):
        super().__init__(
            name="GrievanceAgent",
            description="Processes citizen civic grievances, generates PCMC tickets, and tracks resolution SLAs."
        )

    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Determines if the payload represents a civic grievance."""
        intent = payload.get("intent")
        return intent in ("TEXT_GRIEVANCE", "MEDIA_GRIEVANCE")

    def _generate_ticket_id(self) -> str:
        """Generates standard PCMC grievance ticket ID: PCMC-YYYYMMDD-XXXX."""
        date_str = datetime.now().strftime("%Y%m%d")
        rand_suffix = f"{random.randint(1000, 9999)}"
        return f"PCMC-{date_str}-{rand_suffix}"

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes grievance handling:
        1. Checks if GPS or locality is present.
        2. If missing, requests location/photo and saves pending state in session.
        3. If present or confirmed, registers ticket with SLA.
        """
        text = payload.get("text", "")
        phone = payload.get("citizen_phone", "")
        lang = payload.get("language", "mr")
        exif_data = payload.get("exif_data") or {}
        has_media = bool(payload.get("media_bytes") or payload.get("media_path"))

        # Retrieve session context
        session = session_manager.get_session(phone) if phone else None
        context_data = session.context_data if session else {}

        # Extract GPS if available
        gps_lat = exif_data.get("gps_latitude") or context_data.get("gps_latitude")
        gps_lon = exif_data.get("gps_longitude") or context_data.get("gps_longitude")

        # Determine category
        category = context_data.get("category") or "General Civic Issue"
        department = context_data.get("department") or "Engineering / PWD"
        sla_hours = context_data.get("sla_hours") or 48

        # If citizen has not provided enough location context and no GPS is attached
        has_location = bool(gps_lat and gps_lon) or any(
            loc in text.lower()
            for loc in ["pimpri", "chinchwad", "bhosari", "wakad", "nigdi", "thergaon", "sangvi", "moshi", "dighi", "akaluj", "pradhikaran"]
        )

        # Check if we should register the ticket
        if has_location or has_media or (session and session.pending_action == "AWAITING_LOCATION"):
            ticket_id = self._generate_ticket_id()

            # Clear pending action in session
            if phone:
                session_manager.update_session(
                    phone,
                    active_intent=None,
                    pending_action=None,
                    context_updates={"last_ticket_id": ticket_id},
                )

            location_desc = f"GPS: ({gps_lat:.4f}, {gps_lon:.4f})" if (gps_lat and gps_lon) else "Citizen locality"

            if lang == "mr":
                msg = (
                    f"✅ **तक्रार यशस्वीरित्या नोंदवली आहे!**\n\n"
                    f"• **तक्रार क्रमांक (Ticket ID)**: `{ticket_id}`\n"
                    f"• **विषय**: {category}\n"
                    f"• **संबंधित विभाग**: {department}\n"
                    f"• **ठिकाण**: {location_desc}\n"
                    f"• **निवारण कालावधी (SLA)**: {sla_hours} तास\n\n"
                    f"आपल्या तक्रारीचे काम प्रभाग अभियंत्याकडे वर्ग केले आहे. कामाची सद्यस्थिती याच व्हॉट्सअ‍ॅपवर अपडेट केली जाईल. धन्यवाद!"
                )
            else:
                msg = (
                    f"✅ **Grievance Registered Successfully!**\n\n"
                    f"• **Ticket ID**: `{ticket_id}`\n"
                    f"• **Category**: {category}\n"
                    f"• **Department**: {department}\n"
                    f"• **Location**: {location_desc}\n"
                    f"• **Resolution SLA**: {sla_hours} hours\n\n"
                    f"Assigned to the Ward Engineering field officer. Progress will be tracked on this WhatsApp number."
                )

            return {
                "success": True,
                "ticket_id": ticket_id,
                "status": "REGISTERED",
                "category": category,
                "department": department,
                "sla_hours": sla_hours,
                "response_message": msg,
            }

        else:
            # Need location / photo details from citizen
            if phone:
                session_manager.update_session(
                    phone,
                    active_intent="TEXT_GRIEVANCE",
                    pending_action="AWAITING_LOCATION",
                    context_updates={"complaint_text": text},
                )

            if lang == "mr":
                msg = (
                    f"📝 **तक्रार नोंदणीसाठी माहिती मिळाली आहे.**\n\n"
                    f"तक्रार योग्य प्रभागातील अभियंत्याकडे अचूक पाठवण्यासाठी, कृपया समस्येचे **परिसराचे नाव (उदा. वाकड, भोसरी, निगडी) किंवा समस्येचा फोटो / GPS लोकेशन** पाठवा."
                )
            else:
                msg = (
                    f"📝 **Grievance Details Received.**\n\n"
                    f"To accurately dispatch this issue to the correct Ward Engineer, please share your **area name (e.g., Wakad, Bhosari, Nigdi) or upload a photo / GPS location pin**."
                )

            return {
                "success": True,
                "ticket_id": None,
                "status": "AWAITING_LOCATION",
                "response_message": msg,
            }


# Singleton instance
grievance_agent = GrievanceAgent()
