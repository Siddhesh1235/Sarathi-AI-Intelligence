"""Multilingual Profanity & Abuse Detector with Civic Grievance Protection."""

import re
from typing import Tuple, List, Set
from moderation.profanity_filter.wordlists.profanity_list import (
    ALL_PROFANITY,
    CIVIC_GRIEVANCE_ALLOWLIST,
)


class ProfanityDetector:
    """Detects abusive language across Marathi, Hindi, English, and Roman Marathi."""

    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = sensitivity
        self.profane_set: Set[str] = {w.lower() for w in ALL_PROFANITY}
        self.allowlist_set: Set[str] = {w.lower() for w in CIVIC_GRIEVANCE_ALLOWLIST}

    def _normalize(self, text: str) -> str:
        """Normalizes text by removing repeated characters and standardizing symbols."""
        # Replace common leetspeak substitutions
        substitutions = {
            "@": "a",
            "$": "s",
            "1": "i",
            "0": "o",
            "3": "e",
            "*": "",
            "_": " ",
            "-": " ",
        }
        normalized = text.lower()
        for char, sub in substitutions.items():
            normalized = normalized.replace(char, sub)

        # Collapse repeated characters (e.g., fuuuuck -> fuck, chuuutya -> chutya)
        normalized = re.sub(r"(.)\1{2,}", r"\1", normalized)
        return normalized

    def check(self, text: str) -> Tuple[bool, List[str], float]:
        """
        Analyzes text for profanity and abuse.
        
        Returns:
            (is_profane: bool, matched_terms: List[str], severity_score: float)
        """
        if not text or not text.strip():
            return False, [], 0.0

        normalized = self._normalize(text)
        # Tokenize by non-alphanumeric (keeping Devanagari Unicode characters)
        tokens = re.findall(r"[\w\u0900-\u097F]+", normalized)

        matched_terms: List[str] = []

        # Check single words
        for token in tokens:
            if token in self.allowlist_set:
                continue  # Never flag legitimate civic anger/complaint words
            if token in self.profane_set:
                matched_terms.append(token)

        # Check multi-word phrases (bigrams)
        for i in range(len(tokens) - 1):
            phrase = f"{tokens[i]} {tokens[i+1]}"
            if phrase in self.profane_set and phrase not in self.allowlist_set:
                matched_terms.append(phrase)

        if not matched_terms:
            return False, [], 0.0

        # Calculate severity score based on number of hits
        severity_score = min(1.0, 0.5 + (0.25 * len(matched_terms)))
        is_profane = severity_score >= (1.0 - self.sensitivity)

        return is_profane, list(set(matched_terms)), severity_score
