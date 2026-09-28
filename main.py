"""Sarathi AI — FastAPI Entry Point: Moderation, Vision Defect AI & Master Intent Router."""

from typing import Optional
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from moderation.pipeline import moderation_pipeline
from moderation.schemas import (
    CitizenInputPayload,
    ModerationCheckResponse,
    OutputModerationPayload,
    OutputModerationResponse,
)
from orchestration.agents.router_agent import (
    router_agent,
    RouterDispatchResponse,
)
from document_ai.image_understanding.vision_agent import vision_agent
from preprocessing.pipeline import preprocessing_pipeline
from shared.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="PCMC Sarathi AI — Input Validation, Preprocessing, Content Moderation, YOLO11 Vision & Multimodal Agent Router",
)

# CORS setup for web portals
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Health check and platform status."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "active_modules": [
            "Input Validator (Stage 4.1)",
            "Preprocessing Layer (Stage 4.2)",
            "Content Moderation Gatekeeper (Stage 4.3)",
            "YOLO11 Civic Image Classifier (12 PCMC Classes)",
            "Master Multimodal Intent Router",
        ],
        "supported_languages": ["mr", "hi", "en"],
        "compliance": ["DPDP Act 2023", "CERT-In Guidelines"],
    }


# -------------------------------------------------------------------------
# 1. Content Moderation Endpoints
# -------------------------------------------------------------------------

@app.post(
    "/api/v1/moderation/input",
    response_model=ModerationCheckResponse,
    tags=["Content Moderation"],
    summary="In-flight Citizen Input Moderation",
)
async def check_input_moderation(payload: CitizenInputPayload):
    """
    Scans citizen messages before forwarding to AI Orchestrator / Agents:
    - DPDP PII Masking (Aadhaar, PAN, Phone, Email, Bank)
    - Multilingual Profanity & Abuse Filter (Marathi, Hindi, English, Roman)
    - Prompt Injection & Jailbreak Defense
    - File size & MIME type validation
    - Polite citizen warning generation if blocked
    """
    try:
        result = await moderation_pipeline.moderate_input(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Moderation processing error: {str(e)}",
        )


@app.post(
    "/api/v1/moderation/output",
    response_model=OutputModerationResponse,
    tags=["Content Moderation"],
    summary="Outgoing LLM Response Moderation",
)
async def check_output_moderation(payload: OutputModerationPayload):
    """
    Scans LLM generated response before transmission to WhatsApp:
    - Prevents accidental PII / credential leaks
    - Sanitizes formatting for WhatsApp markdown
    """
    try:
        result = moderation_pipeline.moderate_output(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output moderation error: {str(e)}",
        )


# -------------------------------------------------------------------------
# 2. Computer Vision & Grievance Defect Classification (YOLO11)
# -------------------------------------------------------------------------

@app.post(
    "/api/v1/vision/classify",
    tags=["Computer Vision"],
    summary="Classify Civic Defect Image (12 PCMC Classes)",
)
async def classify_grievance_image(
    file: UploadFile = File(..., description="Uploaded citizen photo (Pothole, Garbage, StreetLight, etc.)"),
    citizen_text: Optional[str] = Form(None, description="Optional accompanying citizen description"),
    language: str = Form("mr", description="Response language: mr, hi, en"),
):
    """
    Analyzes an uploaded civic defect photo using the fine-tuned YOLO11s model:
    - Identifies defect category (PotHoles, Garbage, StreetLight, Drainage, etc.)
    - Returns Marathi/English department mapping, SLA hours, and confidence score.
    """
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        result = await vision_agent.process_image(
            image_input=image_bytes,
            citizen_text=citizen_text,
            language=language,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vision classification error: {str(e)}",
        )


# -------------------------------------------------------------------------
# 3. Master Intent Router (Unified Dispatcher)
# -------------------------------------------------------------------------

@app.post(
    "/api/v1/router/process",
    response_model=RouterDispatchResponse,
    tags=["Master Router"],
    summary="Multimodal Triage & Agent Execution",
)
async def process_with_router(
    text: Optional[str] = Form(None, description="Citizen text message"),
    citizen_phone: Optional[str] = Form(None, description="Citizen WhatsApp phone number"),
    language: str = Form("mr", description="Citizen language code (mr, hi, en)"),
    file: Optional[UploadFile] = File(None, description="Optional photo or attachment"),
):
    """
    Master Router entry point for WhatsApp & Webhooks:
    1. Synchronous Content Moderation check (PII Masking & Safety)
    2. Intent Classification (Media, Grievance, Billing, RTS, FAQ, Greeting)
    3. Multimodal Execution (YOLO11 Vision for photos, Domain Agents for text)
    4. Delivers formatted localized response
    """
    try:
        media_bytes = None
        media_filename = None
        media_mime = None
        media_size = None

        if file:
            media_bytes = await file.read()
            media_filename = file.filename
            media_mime = file.content_type
            media_size = len(media_bytes)

        payload = {
            "text": text or "",
            "citizen_phone": citizen_phone,
            "language": language,
            "media_bytes": media_bytes,
            "media_filename": media_filename,
            "media_mime_type": media_mime,
            "media_size_bytes": media_size,
        }

        # Stage 4.1: Input Validation & Stage 4.2: Preprocessing
        success, preprocessed, err_msg = preprocessing_pipeline.process(payload)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg,
            )

        # Update payload with sanitized and normalized attributes
        payload["text"] = preprocessed.normalized_text
        payload["media_bytes"] = preprocessed.image_bytes
        payload["request_id"] = preprocessed.request_id
        if preprocessed.exif_data:
            payload["exif_data"] = preprocessed.exif_data.model_dump()

        # Stage 4.3: Gatekeeper Content Moderation & Stage 4.4: Master Intent Router
        response = await router_agent.execute(payload)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Router processing error: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.py:app", host="0.0.0.0", port=8000, reload=True)
