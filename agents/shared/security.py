"""Rutinas básicas de seguridad y sanitización para prompts."""

from __future__ import annotations

import re
from typing import Tuple


class SecurityValidator:
    """Detecta PII básica y ataques de prompt injection."""

    PHI_PATTERNS = (
        r"\bSSN\b",
        r"\bdiagnos(?:is|ed)\b",
        r"\bprescription\b",
        r"\bmedical history\b",
        r"\bpatient\b",
    )

    PROMPT_INJECTION_PATTERNS = (
        r"ignore all previous",
        r"disregard previous",
        r"developer mode",
        r"system prompt",
        r"repeat the system instructions",
    )

    def validate(self, text: str) -> Tuple[bool, str]:
        normalized = text.lower()

        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, normalized):
                return False, "PROMPT_INJECTION"

        for pattern in self.PHI_PATTERNS:
            if re.search(pattern, normalized):
                return False, "PHI_DETECTED"

        return True, "OK"
