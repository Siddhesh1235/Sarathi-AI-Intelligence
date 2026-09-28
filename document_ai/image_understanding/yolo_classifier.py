"""YOLO11s-cls Inference Engine for PCMC Civic Grievance Images."""

import io
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from PIL import Image

from document_ai.image_understanding.category_mapping import (
    get_category_info,
    CivicCategoryInfo,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "vision" / "yolo11s-cls.pt"


class CandidatePrediction(BaseModel):
    """Top-K candidate class with confidence score."""
    class_id: str
    confidence: float
    display_name: str = ""
    display_name_en: str = ""
    display_name_mr: str = ""
    department: str = ""
    department_mr: str = ""
    icon: str

    def model_post_init(self, __context):
        if not self.display_name:
            self.display_name = self.display_name_en or self.class_id
        if not self.display_name_en:
            self.display_name_en = self.display_name
        if not self.department:
            self.department = self.department_mr


class ImageClassificationResult(BaseModel):
    """Structured result of YOLO11 civic image classification."""
    is_valid_grievance: bool = Field(description="True if confidence exceeds threshold")
    predicted_class: str
    confidence: float
    display_name: str = ""
    display_name_en: str = ""
    display_name_mr: str = ""
    department: str = ""
    department_en: str = ""
    department_mr: str = ""
    sla_hours: int
    icon: str
    top_candidates: List[CandidatePrediction] = Field(default_factory=list)
    confidence_message: str = ""
    confidence_message_mr: str = ""
    needs_manual_review: bool = False

    def model_post_init(self, __context):
        if not self.display_name:
            self.display_name = self.display_name_en or self.predicted_class
        if not self.display_name_en:
            self.display_name_en = self.display_name
        if not self.department:
            self.department = self.department_en or self.department_mr
        if not self.department_en:
            self.department_en = self.department
        if not self.confidence_message:
            self.confidence_message = self.confidence_message_mr


class YOLO11CivicClassifier:
    """Wrapper around fine-tuned Ultralytics YOLO11s-cls model."""

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        confidence_threshold: float = 0.40,
    ):
        self.model_path = Path(model_path or os.getenv("YOLO_MODEL_PATH", str(DEFAULT_MODEL_PATH)))
        self.confidence_threshold = confidence_threshold
        self._model = None

    def _load_model(self):
        """Lazy load the YOLO model."""
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"YOLO model weights not found at: {self.model_path}")
            from ultralytics import YOLO
            logger.info(f"Loading YOLO11 weights from {self.model_path}...")
            self._model = YOLO(str(self.model_path))
        return self._model

    def predict(
        self,
        image_input: Union[str, Path, bytes, Image.Image],
        top_k: int = 3,
    ) -> ImageClassificationResult:
        """
        Classifies an input image into one of the 12 PCMC civic categories.
        
        Args:
            image_input: File path, raw bytes, or PIL Image object.
            top_k: Number of top candidate classes to return.
        """
        # 1. Convert input to PIL Image
        if isinstance(image_input, (str, Path)):
            pil_image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            pil_image = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, Image.Image):
            pil_image = image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        # 2. Run Inference
        model = self._load_model()
        results = model.predict(source=pil_image, verbose=False)
        first_result = results[0]

        # 3. Extract Top Predictions
        names_dict = first_result.names  # {0: 'PotHoles', 1: 'Garbage', ...}
        probs = first_result.probs

        # Top-1
        top1_idx = int(probs.top1)
        top1_conf = float(probs.top1conf)
        top1_class = names_dict[top1_idx]

        # Top-K candidates
        top_candidates: List[CandidatePrediction] = []
        topk_indices = probs.top5[:top_k] if hasattr(probs, "top5") else [top1_idx]

        for idx in topk_indices:
            cls_name = names_dict[int(idx)]
            cls_conf = float(probs.data[idx])
            cat_info = get_category_info(cls_name)
            if cat_info:
                top_candidates.append(
                    CandidatePrediction(
                        class_id=cat_info.class_id,
                        confidence=round(cls_conf, 3),
                        display_name_en=cat_info.display_name_en,
                        display_name_mr=cat_info.display_name_mr,
                        department_mr=cat_info.department_mr,
                        icon=cat_info.icon,
                    )
                )

        # 4. Map Metadata for Top-1
        top_cat = get_category_info(top1_class)
        if not top_cat:
            top_cat = CivicCategoryInfo(
                class_id=top1_class,
                display_name_en=top1_class,
                display_name_mr=top1_class,
                department_en="General Municipal Administration",
                department_mr="महानगरपालिका सामान्य प्रशासन",
                default_sla_hours=48,
                icon="📋",
                description_mr="नागरी तक्रार",
            )

        # 5. Threshold Evaluation
        is_confident = top1_conf >= self.confidence_threshold
        needs_review = top1_conf < 0.60

        if is_confident:
            msg_mr = f"{top_cat.icon} फोटोमध्ये '{top_cat.display_name_mr}' आढळले आहे (अचूकता: {round(top1_conf * 100, 1)}%)."
        else:
            msg_mr = f"⚠️ फोटो स्पष्ट नाही किंवा तक्रार निश्चित करता आली नाही. कृपया जवळून व स्पष्ट फोटो काढावा."

        return ImageClassificationResult(
            is_valid_grievance=is_confident,
            predicted_class=top_cat.class_id,
            confidence=round(top1_conf, 3),
            display_name_en=top_cat.display_name_en,
            display_name_mr=top_cat.display_name_mr,
            department_en=top_cat.department_en,
            department_mr=top_cat.department_mr,
            sla_hours=top_cat.default_sla_hours,
            icon=top_cat.icon,
            top_candidates=top_candidates,
            confidence_message_mr=msg_mr,
            needs_manual_review=needs_review,
        )
