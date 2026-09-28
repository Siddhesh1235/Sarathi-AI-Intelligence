"""PCMC 12-Class Civic Grievance Category Mapping."""

from typing import Dict, Optional
from pydantic import BaseModel


class CivicCategoryInfo(BaseModel):
    """Metadata for a PCMC civic grievance category."""
    class_id: str
    display_name: str
    display_name_en: Optional[str] = None
    display_name_mr: Optional[str] = None
    department: str
    department_en: Optional[str] = None
    department_mr: Optional[str] = None
    default_sla_hours: int
    icon: str
    description: str

    def model_post_init(self, __context):
        if not self.display_name_en:
            self.display_name_en = self.display_name
        if not self.display_name_mr:
            self.display_name_mr = self.display_name
        if not self.department_en:
            self.department_en = self.department
        if not self.department_mr:
            self.department_mr = self.department


# -------------------------------------------------------------------------
# The 12 Trained PCMC Civic Grievance Classes
# Mapped to Pimpri Chinchwad Municipal Corporation Departments
# -------------------------------------------------------------------------
PCMC_CIVIC_CATEGORIES: Dict[str, CivicCategoryInfo] = {
    "PotHoles": CivicCategoryInfo(
        class_id="PotHoles",
        display_name="Road Potholes & Surface Damage",
        display_name_en="Road Potholes & Surface Damage",
        display_name_mr="रस्त्यावरील खड्डे व नुकसान",
        department="Civil & Road Engineering (PWD)",
        department_en="Civil & Road Engineering (PWD)",
        department_mr="स्थापत्य व रस्ते विभाग",
        default_sla_hours=48,
        icon="🕳️",
        description="Hazardous potholes on roads, damaged tar surface, or road subsidence.",
    ),
    "Garbage": CivicCategoryInfo(
        class_id="Garbage",
        display_name="Unattended Garbage & Waste Dump",
        display_name_en="Unattended Garbage & Waste Dump",
        display_name_mr="कचरा व अस्वच्छता",
        department="Solid Waste Management (SWM)",
        department_en="Solid Waste Management (SWM)",
        department_mr="आरोग्य व घनकचरा व्यवस्थापन विभाग",
        default_sla_hours=24,
        icon="🗑️",
        description="Overflowing garbage bins, scattered roadside trash, or unattended waste piles.",
    ),
    "StreetLight": CivicCategoryInfo(
        class_id="StreetLight",
        display_name="Defective / Broken Street Light",
        display_name_en="Defective / Broken Street Light",
        display_name_mr="नादुरुस्त पथदिवे / स्ट्रीटलाईट",
        department="Electrical Department",
        department_en="Electrical Department",
        department_mr="विद्युत विभाग",
        default_sla_hours=24,
        icon="💡",
        description="Streetlights off at night, glowing during daytime, or damaged electric poles.",
    ),
    "Drainage": CivicCategoryInfo(
        class_id="Drainage",
        display_name="Drainage Overflow & Clogged Gutter",
        display_name_en="Drainage Overflow & Clogged Gutter",
        display_name_mr="गटार व ड्रेनेज ओव्हरफ्लो",
        department="Drainage & Sewage Department",
        department_en="Drainage & Sewage Department",
        department_mr="जलनिस्सारण व मलनिस्सारण विभाग",
        default_sla_hours=24,
        icon="🌊",
        description="Clogged drainage lines, uncovered manholes, or overflowing sewage on streets.",
    ),
    "PipelineDefects": CivicCategoryInfo(
        class_id="PipelineDefects",
        display_name="Water Pipeline Leakage / Burst",
        display_name_en="Water Pipeline Leakage / Burst",
        display_name_mr="पाणी पाईपलाईन गळती",
        department="Water Supply Department",
        department_en="Water Supply Department",
        department_mr="पाणीपुरवठा विभाग",
        default_sla_hours=24,
        icon="🚰",
        description="Burst drinking water mains, line leakages, or malfunctioning pipeline valves.",
    ),
    "Encroachment": CivicCategoryInfo(
        class_id="Encroachment",
        display_name="Illegal Footpath / Road Encroachment",
        display_name_en="Illegal Footpath / Road Encroachment",
        display_name_mr="बेकायदेशीर अतिक्रमण",
        department="Encroachment Removal Department",
        department_en="Encroachment Removal Department",
        department_mr="अतिक्रमण निर्मूलन विभाग",
        default_sla_hours=72,
        icon="🚫",
        description="Unauthorized shops, carts, or construction materials blocking footpaths and roads.",
    ),
    "Banners_Flex": CivicCategoryInfo(
        class_id="Banners_Flex",
        display_name="Illegal Banners, Posters & Hoardings",
        display_name_en="Illegal Banners, Posters & Hoardings",
        display_name_mr="अनधिकृत बॅनर्स व फ्लेक्स",
        department="Sky Signs & Licensing Department",
        department_en="Sky Signs & Licensing Department",
        department_mr="आकाशचिन्ह व परवाना विभाग",
        default_sla_hours=24,
        icon="🪧",
        description="Unauthorized political, commercial banners, flex boards, or hoardings.",
    ),
    "Trees": CivicCategoryInfo(
        class_id="Trees",
        display_name="Fallen Trees / Dangerous Tree Branches",
        display_name_en="Fallen Trees / Dangerous Tree Branches",
        display_name_mr="पडलेली झाडे / धोकादायक फांद्या",
        department="Garden & Tree Authority",
        department_en="Garden & Tree Authority",
        department_mr="उद्यान व वृक्ष प्राधिकरण विभाग",
        default_sla_hours=24,
        icon="🌳",
        description="Trees fallen across roadways or hazardous tree branches near power lines.",
    ),
    "Health_Sanitation": CivicCategoryInfo(
        class_id="Health_Sanitation",
        display_name="Public Health & Sanitation Hazards",
        display_name_en="Public Health & Sanitation Hazards",
        display_name_mr="सार्वजनिक आरोग्य व स्वच्छता",
        department="Public Health Department",
        department_en="Public Health Department",
        department_mr="सार्वजनिक आरोग्य विभाग",
        default_sla_hours=48,
        icon="🏥",
        description="Mosquito breeding spots, foul odors, dead animals, or unhygienic public restrooms.",
    ),
    "Electricity": CivicCategoryInfo(
        class_id="Electricity",
        display_name="Exposed Electric Wires & Hazard DP",
        display_name_en="Exposed Electric Wires & Hazard DP",
        display_name_mr="उघड्या वीज तारा व डीपी धोका",
        department="Electrical Department (MSEDCL/PCMC)",
        department_en="Electrical Department (MSEDCL/PCMC)",
        department_mr="विद्युत विभाग",
        default_sla_hours=12,
        icon="⚡",
        description="Exposed live wires, open DP junction boxes, or short-circuit hazards.",
    ),
    "Noise_Pollution": CivicCategoryInfo(
        class_id="Noise_Pollution",
        display_name="Noise Pollution / Loudspeakers",
        display_name_en="Noise Pollution / Loudspeakers",
        display_name_mr="ध्वनी प्रदूषण",
        department="Environment Department",
        department_en="Environment Department",
        department_mr="पर्यावरण विभाग",
        default_sla_hours=12,
        icon="📢",
        description="Unauthorized loudspeaker usage in silence zones or late at night.",
    ),
    "Road_Incidents_Traffic": CivicCategoryInfo(
        class_id="Road_Incidents_Traffic",
        display_name="Traffic Obstructions & Accidents",
        display_name_en="Traffic Obstructions & Accidents",
        display_name_mr="वाहतूक अडथळा व रस्ता अपघात",
        department="Traffic & Security Management",
        department_en="Traffic & Security Management",
        department_mr="वाहतूक व सुरक्षा विभाग",
        default_sla_hours=12,
        icon="🚗",
        description="Abandoned broken-down vehicles, road hazards, or traffic obstacles.",
    ),
}


def get_category_info(class_name: str) -> Optional[CivicCategoryInfo]:
    """Retrieves civic category metadata with case-insensitive matching."""
    if not class_name:
        return None
    if class_name in PCMC_CIVIC_CATEGORIES:
        return PCMC_CIVIC_CATEGORIES[class_name]
    lower_map = {k.lower(): v for k, v in PCMC_CIVIC_CATEGORIES.items()}
    return lower_map.get(class_name.lower())
