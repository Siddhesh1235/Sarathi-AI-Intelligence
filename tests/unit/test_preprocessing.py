"""Unit tests for Stage 4.2 Preprocessing Layer."""

import io
from PIL import Image
from preprocessing.text_normalizer import TextNormalizer
from preprocessing.image_preprocessor import ImagePreprocessor
from preprocessing.pipeline import PreprocessingPipeline


def test_text_normalization():
    # Evasion with zero-width spaces and HTML tags
    dirty_text = "  <script>alert(1)</script> Hello\u200b \ufeffWorld!   Multiple   spaces \n\n "
    clean_text = TextNormalizer.normalize(dirty_text)

    assert "<script>" not in clean_text
    assert "\u200b" not in clean_text
    assert "\ufeff" not in clean_text
    assert "  " not in clean_text
    assert "Hello World! Multiple spaces" in clean_text


def test_gps_dms_conversion():
    preprocessor = ImagePreprocessor()
    # 18° 37' 12.0" N
    lat_dms = ((18, 1), (37, 1), (120, 10))
    lat_dec = preprocessor._convert_dms_to_decimal(lat_dms, "N")
    assert lat_dec is not None
    assert round(lat_dec, 2) == 18.62

    # 73° 48' 36.0" E
    lon_dms = ((73, 1), (48, 1), (360, 10))
    lon_dec = preprocessor._convert_dms_to_decimal(lon_dms, "E")
    assert lon_dec is not None
    assert round(lon_dec, 2) == 73.81


def test_image_preprocessing_auto_rgb():
    preprocessor = ImagePreprocessor()
    # Create RGBA palette image
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_png = buf.getvalue()

    processed_bytes, exif_info = preprocessor.process(raw_png)
    assert processed_bytes is not None
    assert len(processed_bytes) > 0

    # Ensure output is valid JPEG
    with Image.open(io.BytesIO(processed_bytes)) as out_img:
        assert out_img.mode == "RGB"
        assert out_img.format == "JPEG"


def test_preprocessing_pipeline_end_to_end():
    pipeline = PreprocessingPipeline()
    raw_payload = {
        "text": "  खड्डा \u200bदुरुस्ती  करा  ",
        "citizen_phone": "9822112233",
        "language": "mr",
    }
    success, payload, error = pipeline.process(raw_payload)

    assert success is True
    assert error is None
    assert payload is not None
    assert payload.request_id.startswith("REQ-")
    assert payload.normalized_text == "खड्डा दुरुस्ती करा"
    assert payload.citizen_phone == "9822112233"
