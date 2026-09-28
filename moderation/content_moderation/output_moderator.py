"""Output Moderation: Inspects LLM generated responses before transmission to citizen."""

import re
from typing import Tuple
from moderation.schemas import OutputModerationResponse
from moderation.pii_masking.pii_masker import PIIMasker


class OutputModerator:
    """Verifies outgoing LLM text against PII leakage, system credentials, and formatting."""

    def __init__(self):
        self.pii_masker = PIIMasker(preserve_last_digits=False)  # Completely redact in output
        self.secret_patterns = [
            re.compile(r"(?i)\b(api[_\-\s]?key|bearer\s+[a-z0-9_\-\.]{20,}|password\s*[:=])", re.IGNORECASE),
            re.compile(r"(?i)\b(postgres://|mysql://|sqlite:///)", re.IGNORECASE),
        ]

    def moderate_output(self, raw_response: str) -> OutputModerationResponse:
        """
        Validates and sanitizes outgoing LLM responses.
        """
        if not raw_response:
            return OutputModerationResponse(is_safe=True, safe_response="")

        sanitized = raw_response
        pii_count = 0

        # 1. Mask any leaked citizen or system PII
        masked_text, masked_entities = self.pii_masker.mask_text(sanitized)
        if masked_entities:
            sanitized = masked_text
            pii_count = len(masked_entities)

        # 2. Block system secrets or connection strings
        for secret_regex in self.secret_patterns:
            if secret_regex.search(sanitized):
                sanitized = secret_regex.sub("[CONFIDENTIAL_CREDENTIAL]", sanitized)
                pii_count += 1

        # 3. Clean up formatting for WhatsApp (strip raw HTML tags like <b> or <div>)
        sanitized = re.sub(r"<[^>]+>", "", sanitized)

        return OutputModerationResponse(
            is_safe=True,
            safe_response=sanitized.strip(),
            pii_redacted_count=pii_count,
            formatted_for_whatsapp=True,
        )
