"""Vision Agent for Civic Defect Verification and Grievance Processing."""

import logging
from typing import Optional, Union, Dict, Any
from pathlib import Path
from PIL import Image

from document_ai.image_understanding.yolo_classifier import (
    YOLO11CivicClassifier,
    ImageClassificationResult,
)

logger = logging.getLogger(__name__)


class VisionAgent:
    """
    Autonomous Vision Agent.
    Validates civic grievance photos, classifies defects into PCMC departments,
    and returns structured responses.
    """

    def __init__(self, classifier: Optional[YOLO11CivicClassifier] = None):
        self.classifier = classifier or YOLO11CivicClassifier()

    async def process_image(
        self,
        image_input: Union[str, Path, bytes, Image.Image],
        citizen_text: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Analyzes the uploaded photo and generates a structured grievance vision report.
        """
        try:
            result: ImageClassificationResult = self.classifier.predict(image_input)

            if result.is_valid_grievance:
                response_text = (
                    f"{result.icon} **Civic Defect Identified:**\n\n"
                    f"• **Category**: {result.display_name}\n"
                    f"• **Department**: {result.department}\n"
                    f"• **Resolution SLA**: {result.sla_hours} hours\n"
                    f"• **Confidence**: {round(result.confidence * 100, 1)}%\n\n"
                    f"To forward this issue to the assigned Ward Engineer, please share your area name or GPS location pin."
                )
            else:
                response_text = (
                    f"⚠️ **Image Unclear:**\n"
                    f"Could not identify a municipal defect with sufficient confidence. "
                    f"Please upload a clearer, closer photo of the issue."
                )

            return {
                "success": True,
                "is_defect_detected": result.is_valid_grievance,
                "category": result.predicted_class,
                "display_name": result.display_name,
                "display_name_mr": result.display_name_mr,
                "department": result.department,
                "department_mr": result.department_mr,
                "sla_hours": result.sla_hours,
                "confidence": result.confidence,
                "needs_review": result.needs_manual_review,
                "top_candidates": [c.model_dump() for c in result.top_candidates],
                "response_message": response_text,
            }

        except Exception as e:
            logger.error(f"Error in VisionAgent processing: {str(e)}", exc_info=True)
            return {
                "success": False,
                "is_defect_detected": False,
                "error": str(e),
                "response_message": "An error occurred while analyzing the image. Please try again shortly.",
            }


# Vision agent singleton
vision_agent = VisionAgent()
