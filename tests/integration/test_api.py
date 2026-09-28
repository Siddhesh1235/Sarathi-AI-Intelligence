"""Integration tests for FastAPI endpoints."""

import io
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "DPDP Act 2023" in data["compliance"]
        assert len(data["active_modules"]) >= 3


@pytest.mark.asyncio
async def test_input_moderation_api_clean():
    payload = {
        "text": "माझे नाव सचिन आहे, मोबाईल 9822112233, वॉर्ड क्रमांक ५ चे कार्यालय कुठे आहे?",
        "language": "mr",
        "channel": "whatsapp",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/moderation/input", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is True
        assert data["status"] == "SANITIZED_SAFE"
        assert "XXXXXX2233" in data["cleaned_text"]
        assert "9822112233" not in data["cleaned_text"]


@pytest.mark.asyncio
async def test_input_moderation_api_blocked_profanity():
    payload = {
        "text": "are bhadwa faltu service",
        "language": "mr",
        "channel": "whatsapp",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/moderation/input", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is False
        assert data["status"] == "UNSAFE"
        assert data["polite_warning"] is not None
        assert "सभ्य भाषेत" in data["polite_warning"]


@pytest.mark.asyncio
async def test_vision_classification_api():
    # Create an in-memory test image
    img = Image.new("RGB", (224, 224), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    files = {"file": ("test_defect.jpg", img_bytes, "image/jpeg")}
    data = {"citizen_text": "खड्डा पडला आहे", "language": "mr"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/vision/classify", files=files, data=data)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert "category" in res
        assert "department_mr" in res
        assert "confidence" in res


@pytest.mark.asyncio
async def test_router_process_api_text_greeting():
    data = {"text": "नमस्कार, मदत हवी आहे", "language": "mr"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/router/process", data=data)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["detected_intent"] == "GREETING"
        assert res["routed_to_agent"] == "RouterAgent"
        assert "Sarathi AI" in res["response_message"]


@pytest.mark.asyncio
async def test_router_process_api_with_image():
    img = Image.new("RGB", (224, 224), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    files = {"file": ("wakad_pothole.jpg", img_bytes, "image/jpeg")}
    data = {"text": "रस्ता खराब झालाय", "citizen_phone": "9822998877", "language": "mr"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/router/process", files=files, data=data)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["detected_intent"] == "MEDIA_GRIEVANCE"
        assert res["routed_to_agent"] == "VisionAgent"
        assert "Defect" in res["response_message"] or "Ward Engineer" in res["response_message"]
