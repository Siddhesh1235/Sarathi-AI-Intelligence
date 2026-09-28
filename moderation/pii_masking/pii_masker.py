"""PII Masking implementation for DPDP Act 2023 compliance."""

import re
from typing import Tuple, List
from moderation.schemas import MaskedEntity
from moderation.pii_masking.rules import (
    AADHAAR_REGEX,
    PAN_REGEX,
    PHONE_REGEX,
    EMAIL_REGEX,
    IFSC_REGEX,
    BANK_ACCOUNT_REGEX,
    validate_verhoeff_aadhaar,
)


class PIIMasker:
    """Detects and masks sensitive personal identifiable information."""

    def __init__(self, preserve_last_digits: bool = True):
        self.preserve_last_digits = preserve_last_digits

    def mask_text(self, text: str) -> Tuple[str, List[MaskedEntity]]:
        """Scans and masks Aadhaar, PAN, Phone, Email, Bank Details."""
        if not text:
            return "", []

        masked_entities: List[MaskedEntity] = []
        result = text

        # 1. Mask Aadhaar Numbers
        def _mask_aadhaar(match: re.Match) -> str:
            raw = match.group(1)
            clean_digits = re.sub(r"\D", "", raw)
            # Check Verhoeff checksum
            if validate_verhoeff_aadhaar(clean_digits):
                last4 = clean_digits[-4:] if self.preserve_last_digits else "XXXX"
                masked = f"XXXX-XXXX-{last4}"
                masked_entities.append(MaskedEntity(entity_type="AADHAAR", masked_text=masked))
                return masked
            return raw

        result = AADHAAR_REGEX.sub(_mask_aadhaar, result)

        # 2. Mask PAN Card
        def _mask_pan(match: re.Match) -> str:
            raw = match.group(1).upper()
            masked = f"{raw[:2]}XXXXX{raw[-2:]}" if self.preserve_last_digits else "XXXXXXXXXX"
            masked_entities.append(MaskedEntity(entity_type="PAN", masked_text=masked))
            return masked

        result = PAN_REGEX.sub(_mask_pan, result)

        # 3. Mask Phone Numbers
        def _mask_phone(match: re.Match) -> str:
            raw = match.group(1)
            last4 = raw[-4:] if self.preserve_last_digits else "XXXX"
            masked = f"XXXXXX{last4}"
            masked_entities.append(MaskedEntity(entity_type="PHONE", masked_text=masked))
            return masked

        result = PHONE_REGEX.sub(_mask_phone, result)

        # 4. Mask Email
        def _mask_email(match: re.Match) -> str:
            raw = match.group(1)
            parts = raw.split("@")
            user, domain = parts[0], parts[1]
            masked_user = user[0] + "***" if len(user) > 1 else "***"
            masked = f"{masked_user}@{domain}"
            masked_entities.append(MaskedEntity(entity_type="EMAIL", masked_text=masked))
            return masked

        result = EMAIL_REGEX.sub(_mask_email, result)

        # 5. Mask Bank Account Numbers
        def _mask_bank_acc(match: re.Match) -> str:
            full_match = match.group(0)
            acc_num = match.group(1)
            last3 = acc_num[-3:] if self.preserve_last_digits else "XXX"
            masked_acc = f"XXXXXX{last3}"
            masked_entities.append(MaskedEntity(entity_type="BANK_ACC", masked_text=masked_acc))
            return full_match.replace(acc_num, masked_acc)

        result = BANK_ACCOUNT_REGEX.sub(_mask_bank_acc, result)

        # 6. Mask IFSC Code
        def _mask_ifsc(match: re.Match) -> str:
            raw = match.group(1).upper()
            masked = f"{raw[:4]}XXXXXXX"
            masked_entities.append(MaskedEntity(entity_type="IFSC", masked_text=masked))
            return masked

        result = IFSC_REGEX.sub(_mask_ifsc, result)

        return result, masked_entities
