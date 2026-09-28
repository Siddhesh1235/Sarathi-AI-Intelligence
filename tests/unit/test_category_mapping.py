"""Unit tests for PCMC category mapping."""

from document_ai.image_understanding.category_mapping import (
    PCMC_CIVIC_CATEGORIES,
    get_category_info,
)


def test_12_classes_exist():
    expected_classes = {
        "PotHoles", "Garbage", "StreetLight", "Drainage",
        "PipelineDefects", "Encroachment", "Banners_Flex",
        "Trees", "Health_Sanitation", "Electricity",
        "Noise_Pollution", "Road_Incidents_Traffic"
    }
    assert set(PCMC_CIVIC_CATEGORIES.keys()) == expected_classes


def test_category_info_retrieval():
    pothole = get_category_info("PotHoles")
    assert pothole is not None
    assert pothole.class_id == "PotHoles"
    assert "खड्डे" in pothole.display_name_mr
    assert "स्थापत्य" in pothole.department_mr
    assert pothole.default_sla_hours == 48

    # Case insensitive
    garbage = get_category_info("garbage")
    assert garbage is not None
    assert garbage.class_id == "Garbage"
    assert "कचरा" in garbage.display_name_mr

    # Non-existent
    assert get_category_info("RandomClass") is None
