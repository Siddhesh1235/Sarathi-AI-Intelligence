"""Master Intent Router Agent for PCMC Sarathi AI.

Orchestrates incoming citizen requests across Vision, Grievance, Billing, RTS, and FAQ domain agents.
Manages multi-turn conversation states and session tracking.
"""

import re
import logging
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from orchestration.agents.base_agent import BaseAgent
from orchestration.agents.agent_registry import AgentRegistry
from orchestration.agents.grievance_agent import grievance_agent
from orchestration.agents.billing_agent import billing_agent
from orchestration.agents.rts_agent import rts_agent
from orchestration.agents.knowledge_agent import knowledge_agent
from orchestration.agents.handoff_agent import handoff_agent
from orchestration.session_context.session_manager import session_manager

from moderation.pipeline import moderation_pipeline
from moderation.schemas import CitizenInputPayload, SafetyStatus, OutputModerationPayload
from document_ai.image_understanding.vision_agent import vision_agent

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Core citizen intent categories."""
    MEDIA_GRIEVANCE = "MEDIA_GRIEVANCE"           # Citizen uploaded a grievance photo/video
    TEXT_GRIEVANCE = "TEXT_GRIEVANCE"             # Citizen describing a pothole/garbage in text
    BILLING_TAX = "BILLING_TAX"                   # Property tax, water bill, payment links
    RTS_TRACKING = "RTS_TRACKING"                 # Application / Certificate status check
    CIVIC_INFO_FAQ = "CIVIC_INFO_FAQ"             # Schemes, ward offices, timings, rules
    GREETING = "GREETING"                         # Hi, Hello, नमस्कार, शुभ सकाळ
    HUMAN_ESCALATION = "HUMAN_ESCALATION"         # Talk to agent, कॉल सेंटर प्रतिनिधीशी बोला


class RouterDispatchResponse(BaseModel):
    """Result of Master Router triage and agent execution."""
    success: bool
    detected_intent: IntentType
    routed_to_agent: str
    is_moderated: bool
    safety_status: SafetyStatus
    response_message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RouterAgent(BaseAgent):
    """
    Central Triage and Multi-turn Dispatcher.
    Inspects multimodal input, tracks session context, and orchestrates downstream domain agents.
    """

    def __init__(self):
        super().__init__(
            name="RouterAgent",
            description="Triage agent routing inputs to Vision, Grievance, Billing, and FAQ agents."
        )
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        """Initializes domain agent registry mappings."""
        AgentRegistry.register(IntentType.TEXT_GRIEVANCE.value, grievance_agent)
        AgentRegistry.register(IntentType.BILLING_TAX.value, billing_agent)
        AgentRegistry.register(IntentType.RTS_TRACKING.value, rts_agent)
        AgentRegistry.register(IntentType.CIVIC_INFO_FAQ.value, knowledge_agent)
        AgentRegistry.register(IntentType.HUMAN_ESCALATION.value, handoff_agent)

    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """The Router is the master entrypoint and handles all incoming requests."""
        return True

    def classify_intent(self, text: str, has_media: bool) -> IntentType:
        """
        Classifies citizen intent using multimodal signals and semantic regex rules.
        """
        if has_media:
            return IntentType.MEDIA_GRIEVANCE

        clean = (text or "").lower().strip()

        # 1. Greetings
        if re.search(r"^(hi|hello|hey|namaskar|namaste|नमस्कार|प्रणाम|शुभ सकाळ|शुभ प्रभात)\b", clean):
            return IntentType.GREETING

        # 2. Human Escalation
        if re.search(r"(operator|human|officer|call center|प्रतिनिधी|माणसाशी बोला|अधिकारी|कॉल सेंटर)", clean):
            return IntentType.HUMAN_ESCALATION

        # 3. Billing & Taxes (Property tax, Water bill, receipts)
        if re.search(r"(tax|bill|water|property|घरपट्टी|पाणीपट्टी|कर|बिल|पावती|भरणा|रक्कम|meter)", clean):
            return IntentType.BILLING_TAX

        # 4. RTS Application / Certificate Tracking
        if re.search(r"(status|track|application|certificate|दाखला|जन्म|मृत्यू|विवाह|अर्जाची स्थिती|टोकन)", clean):
            return IntentType.RTS_TRACKING

        # 5. Text Grievance (Potholes, Garbage, Drainage, Streetlights, etc.)
        if re.search(r"(complaint|takrar|pothole|khadda|garbage|kachra|gutter|gatar|streetlight|street light|light band|drainage|water leakage|leakage|खड्डा|कचरा|गटार|लाईट|लाईट बंद|ड्रेनेज|तक्रार|पाणी येत नाही|दुर्गंधी|अस्वच्छता|घाण)", clean):
            return IntentType.TEXT_GRIEVANCE

        # 6. Default to Civic Info & FAQ
        return IntentType.CIVIC_INFO_FAQ

    async def execute(self, payload: Dict[str, Any]) -> RouterDispatchResponse:
        """
        Complete processing:
        1. Content Moderation Check (Gatekeeper 4.3)
        2. Session & Multi-turn Context Resolution
        3. Multimodal Routing (Image vs Text)
        4. Domain Agent Execution
        5. Output Moderation & Formatting
        """
        raw_text = payload.get("text", "")
        media_bytes = payload.get("media_bytes")
        media_path = payload.get("media_path")
        has_media = bool(media_bytes or media_path)
        citizen_phone = payload.get("citizen_phone", "")
        lang = payload.get("language", "mr")

        # -------------------------------------------------------------
        # Step 1: Content Moderation (Gatekeeper)
        # -------------------------------------------------------------
        mod_input = CitizenInputPayload(
            citizen_phone=citizen_phone,
            text=raw_text,
            language=lang,
            channel=payload.get("channel", "whatsapp"),
            media_filename=payload.get("media_filename"),
            media_mime_type=payload.get("media_mime_type"),
            media_size_bytes=payload.get("media_size_bytes"),
        )
        mod_result = await moderation_pipeline.moderate_input(mod_input)

        if not mod_result.is_safe:
            return RouterDispatchResponse(
                success=False,
                detected_intent=IntentType.TEXT_GRIEVANCE,
                routed_to_agent="ModerationAgent",
                is_moderated=True,
                safety_status=mod_result.status,
                response_message=mod_result.polite_warning or "संदेश नियमांचे उल्लंघन करत आहे.",
                metadata={"violations": [v.value for v in mod_result.violations]},
            )

        sanitized_text = mod_result.cleaned_text
        payload["text"] = sanitized_text

        # -------------------------------------------------------------
        # Step 2: Multi-turn Session & Intent Classification
        # -------------------------------------------------------------
        session = session_manager.get_or_create_session(citizen_phone, language=lang) if citizen_phone else None
        
        # Check if citizen's message is a direct switch or intent
        detected_intent = self.classify_intent(sanitized_text, has_media=has_media)

        # Handle pending multi-turn flow if user doesn't switch to greeting/billing
        if session and session.pending_action:
            # If user explicitly greets or switches topic, reset pending action
            if detected_intent in (IntentType.GREETING, IntentType.BILLING_TAX, IntentType.HUMAN_ESCALATION):
                session_manager.update_session(citizen_phone, pending_action=None)
            elif session.pending_action == "AWAITING_LOCATION" and not has_media:
                detected_intent = IntentType.TEXT_GRIEVANCE
            elif session.pending_action == "AWAITING_BILLING_ID":
                detected_intent = IntentType.BILLING_TAX
            elif session.pending_action == "AWAITING_APP_ID":
                detected_intent = IntentType.RTS_TRACKING

        # Record incoming citizen turn
        if citizen_phone:
            session_manager.add_turn(
                citizen_phone=citizen_phone,
                role="citizen",
                text=sanitized_text,
                intent=detected_intent.value,
                media_attached=has_media,
            )

        payload["intent"] = detected_intent.value

        # -------------------------------------------------------------
        # Step 3: Domain Agent Execution
        # -------------------------------------------------------------
        routed_agent_name = "RouterAgent"
        response_msg = ""
        meta_result: Dict[str, Any] = {}
        is_success = True

        # CASE A: Media / Photo Grievance ➔ VisionAgent (YOLO11s)
        if detected_intent == IntentType.MEDIA_GRIEVANCE:
            routed_agent_name = "VisionAgent"
            img_input = media_bytes if media_bytes is not None else media_path
            vision_result = await vision_agent.process_image(
                image_input=img_input,
                citizen_text=sanitized_text,
                language=lang,
            )
            is_success = vision_result.get("success", False)
            response_msg = vision_result.get("response_message", "")
            meta_result = vision_result

            # If defect detected, save into session context for seamless ticket creation
            if session and vision_result.get("is_defect_detected"):
                session_manager.update_session(
                    citizen_phone,
                    active_intent=IntentType.TEXT_GRIEVANCE.value,
                    pending_action="AWAITING_LOCATION",
                    context_updates={
                        "category": vision_result.get("display_name"),
                        "department": vision_result.get("department"),
                        "sla_hours": vision_result.get("sla_hours"),
                    }
                )

        # CASE B: Greeting
        elif detected_intent == IntentType.GREETING:
            routed_agent_name = "RouterAgent"
            if lang == "mr":
                response_msg = (
                    "🙏 **नमस्कार! मी PCMC Sarathi AI.**\n"
                    "पिंपरी चिंचवड महानगरपालिकेच्या नागरिक सेवेत आपले स्वागत आहे.\n\n"
                    "मी खालील सेवांमध्ये आपली मदत करू शकतो:\n"
                    "1️⃣ 🕳️ नागरी तक्रार नोंदवणे (खड्डे, कचरा, पथदिवे - फोटो पाठवू शकता)\n"
                    "2️⃣ 💰 घरपट्टी व पाणी बिल भरणे\n"
                    "3️⃣ 📜 दाखले व अर्जांची स्थिती तपासणे\n"
                    "4️⃣ 🏛️ पालिकेच्या कल्याणकारी योजनांची माहिती\n\n"
                    "कृपया आपली समस्या किंवा प्रश्न लिहा."
                )
            else:
                response_msg = (
                    "🙏 **Welcome to PCMC Sarathi AI!**\n"
                    "Pimpri Chinchwad Municipal Corporation Citizen Assistance.\n\n"
                    "How may I assist you today?\n"
                    "1️⃣ 🕳️ Civic Grievance (Potholes, Garbage, Lights - upload photo)\n"
                    "2️⃣ 💰 Property Tax & Water Bill Payment\n"
                    "3️⃣ 📜 RTS Certificate / Application Status Tracking\n"
                    "4️⃣ 🏛️ Municipal Schemes & Information\n\n"
                    "Please describe your query or upload an issue photo."
                )

        # CASE C: Registered Domain Agents (Grievance, Billing, RTS, Knowledge, Handoff)
        else:
            agent = AgentRegistry.get_agent(detected_intent.value)
            if agent:
                routed_agent_name = agent.name
                agent_outcome = await agent.execute(payload)
                is_success = agent_outcome.get("success", True)
                response_msg = agent_outcome.get("response_message", "")
                meta_result = agent_outcome
            else:
                routed_agent_name = "RouterAgent"
                response_msg = "आपला संदेश प्राप्त झाला आहे. संबंधित विभागाशी संपर्क साधला जात आहे."

        # -------------------------------------------------------------
        # Step 4: Output Moderation Check
        # -------------------------------------------------------------
        out_mod = moderation_pipeline.moderate_output(
            OutputModerationPayload(
                raw_response=response_msg,
                target_language=lang,
                citizen_phone=citizen_phone,
            )
        )
        final_response_text = out_mod.safe_response

        # Record assistant turn in session
        if citizen_phone:
            session_manager.add_turn(
                citizen_phone=citizen_phone,
                role="assistant",
                text=final_response_text,
                intent=detected_intent.value,
                metadata={"routed_to": routed_agent_name},
            )

        return RouterDispatchResponse(
            success=is_success,
            detected_intent=detected_intent,
            routed_to_agent=routed_agent_name,
            is_moderated=True,
            safety_status=mod_result.status,
            response_message=final_response_text,
            metadata=meta_result,
        )


# Router singleton instance
router_agent = RouterAgent()
