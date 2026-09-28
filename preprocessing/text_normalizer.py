"""Stage 4.2: Text Normalization and Sanitization.

Cleans citizen text by removing zero-width characters, normalizing unicode,
and collapsing redundant whitespaces to improve downstream NLP and moderation accuracy.
"""

import re
import unicodedata

# Zero-width spaces and control characters often used to evade moderation
ZERO_WIDTH_CHARS = re.compile(r"[\u200B-\u200D\uFEFF\u200E\u200F\u00AD]")

# HTML tags stripper
HTML_TAG_REGEX = re.compile(r"<[^>]+>")


class TextNormalizer:
    """Sanitizes and normalizes incoming citizen text."""

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalizes input text:
        1. Strips HTML markup.
        2. Removes zero-width evasion characters.
        3. Standardizes Unicode representation (NFKC).
        4. Collapses redundant spaces and tabs.
        """
        if not text:
            return ""

        # 1. Strip HTML tags
        cleaned = HTML_TAG_REGEX.sub(" ", text)

        # 2. Remove zero-width characters
        cleaned = ZERO_WIDTH_CHARS.sub("", cleaned)

        # 3. Standardize Unicode (NFKC handles composite characters gracefully)
        cleaned = unicodedata.normalize("NFKC", cleaned)

        # 4. Remove control characters (except newline \n and tab \t)
        cleaned = "".join(ch for ch in cleaned if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C")

        # 5. Collapse multiple spaces into a single space
        cleaned = re.sub(r"[^\S\r\n]+", " ", cleaned)

        # 6. Trim leading/trailing whitespace
        return cleaned.strip()
