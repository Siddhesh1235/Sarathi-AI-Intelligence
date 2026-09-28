"""Stage 4.2: Image Preprocessing, Auto-Orientation, and EXIF GPS Extraction."""

import io
import logging
from typing import Tuple, Optional, Any, Dict
from PIL import Image, ImageOps, ExifTags

from preprocessing.schemas import ExtractedEXIF

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocesses citizen uploaded photos: auto-rotation, RGB standardization, and EXIF extraction."""

    @staticmethod
    def _convert_dms_to_decimal(dms_values: Any, ref: str) -> Optional[float]:
        """Converts Degrees, Minutes, Seconds tuple to decimal float degrees."""
        try:
            def _to_float(v: Any) -> float:
                if isinstance(v, (tuple, list)) and len(v) == 2:
                    return float(v[0]) / float(v[1]) if float(v[1]) != 0 else float(v[0])
                return float(v)

            degrees = _to_float(dms_values[0])
            minutes = _to_float(dms_values[1])
            seconds = _to_float(dms_values[2])

            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            if ref in ("S", "W"):
                decimal = -decimal
            return round(decimal, 6)
        except Exception as e:
            logger.debug(f"Failed to convert GPS coordinates: {e}")
            return None

    def extract_exif(self, pil_image: Image.Image) -> ExtractedEXIF:
        """Extracts camera metadata and GPS coordinates from PIL image EXIF."""
        exif_info = ExtractedEXIF()

        try:
            exif = pil_image.getexif()
            if not exif:
                return exif_info

            # Map tag IDs to tag names
            named_exif: Dict[str, Any] = {}
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                named_exif[tag_name] = value

            # Camera details
            exif_info.camera_make = str(named_exif.get("Make", "")).strip() or None
            exif_info.camera_model = str(named_exif.get("Model", "")).strip() or None
            exif_info.capture_time = str(named_exif.get("DateTimeOriginal", named_exif.get("DateTime", ""))).strip() or None

            # Extract GPS Data if available
            gps_tag_id = 0x8825  # GPSInfo
            gps_data = exif.get_ifd(gps_tag_id) if hasattr(exif, "get_ifd") else None

            if gps_data:
                gps_tags = {}
                for key, val in gps_data.items():
                    gps_tag_name = ExifTags.GPSTAGS.get(key, str(key))
                    gps_tags[gps_tag_name] = val

                lat_dms = gps_tags.get("GPSLatitude")
                lat_ref = gps_tags.get("GPSLatitudeRef")
                lon_dms = gps_tags.get("GPSLongitude")
                lon_ref = gps_tags.get("GPSLongitudeRef")

                if lat_dms and lat_ref and lon_dms and lon_ref:
                    lat = self._convert_dms_to_decimal(lat_dms, lat_ref)
                    lon = self._convert_dms_to_decimal(lon_dms, lon_ref)
                    if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
                        exif_info.has_gps = True
                        exif_info.latitude = lat
                        exif_info.longitude = lon

        except Exception as e:
            logger.debug(f"EXIF extraction error (non-fatal): {e}")

        return exif_info

    def process(self, raw_bytes: bytes) -> Tuple[bytes, ExtractedEXIF]:
        """
        Normalizes image:
        1. Auto-rotates image according to EXIF orientation.
        2. Converts color palette to standard 3-channel RGB.
        3. Extracts camera metadata and GPS coordinates.
        4. Re-encodes to clean JPEG bytes.
        """
        with Image.open(io.BytesIO(raw_bytes)) as img:
            # 1. Extract EXIF before rotation
            exif_info = self.extract_exif(img)

            # 2. Auto-rotate image (fixes mobile orientation)
            oriented_img = ImageOps.exif_transpose(img)
            if oriented_img is None:
                oriented_img = img
 
            # 3. Convert to RGB
            rgb_img = oriented_img.convert("RGB")

            # 4. Save normalized JPEG bytes
            output_buffer = io.BytesIO()
            rgb_img.save(output_buffer, format="JPEG", quality=90, optimize=True)
            return output_buffer.getvalue(), exif_info
