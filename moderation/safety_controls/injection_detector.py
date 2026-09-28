"""Prompt Injection, Jailbreak, and System Prompt Leakage Protection."""

import re
from typing import Tuple, List

# Patterns frequently used in prompt injection / jailbreak attacks
INJECTION_PATTERNS = [
    # Direct instruction overrides
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
    r"(?i)\bdisregard\s+(all\s+)?(previous|prior)\s+(instructions|directives)",
    r"(?i)\bforget\s+(everything\s+)?(you\s+(were|have\s+been)\s+told|prior\s+instructions)",
    r"(?i)\boverride\s+(all\s+)?(system|safety|security)\s+(rules|guidelines)",
    # Persona hijacking / DAN
    r"(?i)\byou\s+are\s+now\s+(DAN|unrestricted|jailbroken|an\s+AI\s+without\s+rules)",
    r"(?i)\bact\s+as\s+(DAN|an?\s+unfiltered|an?\s+evil|an?\s+anarchist)",
    r"(?i)\bpretend\s+(there\s+are\s+no\s+rules|you\s+have\s+no\s+restrictions)",
    r"(?i)\bdo\s+anything\s+now\b",
    # System prompt extraction
    r"(?i)\b(print|show|display|reveal|leak|repeat|output)\s+(your\s+)?(system\s+prompt|initial\s+instructions|secret\s+key|internal\s+rules)",
    r"(?i)\bwhat\s+(is|are)\s+your\s+(original|system|hidden)\s+(prompt|instructions)\b",
    # Delimiter injection
    r"(?i)(<\s*\|\s*im_start\s*\|>|<\s*\|\s*system\s*\|>|\[\s*SYSTEM\s*\]|<<SYS>>)",
    r"(?i)---+\s*start\s+of\s+system\s+prompt\s*---+",
]


class InjectionDetector:
    """Heuristic detector for prompt injection, jailbreaking, and prompt extraction."""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.compiled_patterns = [re.compile(p) for p in INJECTION_PATTERNS]

    def check(self, text: str) -> Tuple[bool, List[str], float]:
        """
        Scans text for prompt injection / jailbreak patterns.
        
        Returns:
            (is_injection: bool, matched_patterns: List[str], risk_score: float)
        """
        if not text:
            return False, [], 0.0

        matches: List[str] = []
        for regex in self.compiled_patterns:
            found = regex.findall(text)
            if found:
                matches.append(regex.pattern)

        if not matches:
            return False, [], 0.0

        # Each match increases risk score
        risk_score = min(1.0, 0.6 + (0.2 * len(matches)))
        is_injection = risk_score >= self.threshold

        return is_injection, matches, risk_score
