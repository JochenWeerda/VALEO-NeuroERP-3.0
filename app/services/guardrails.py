"""
Guardrails Service — NC-C3
Input-Filterung (Prompt Injection Detection) und Output-Filterung (PII in AI-Antworten).
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.services.pii_detector import detect_pii, mask_irreversible, PIIMatch

logger = logging.getLogger(__name__)


class GuardrailAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


@dataclass
class GuardrailResult:
    action: GuardrailAction = GuardrailAction.ALLOW
    reasons: list[str] = field(default_factory=list)
    pii_found: list[PIIMatch] = field(default_factory=list)
    sanitized_text: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "reasons": self.reasons,
            "pii_count": len(self.pii_found),
            "pii_types": list({m.type for m in self.pii_found}),
            "sanitized": self.sanitized_text is not None,
        }


INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"```\s*system", re.IGNORECASE),
    re.compile(r"ADMIN\s+OVERRIDE", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all)", re.IGNORECASE),
    re.compile(r"do\s+not\s+follow\s+your\s+rules", re.IGNORECASE),
]


def check_input(text: str) -> GuardrailResult:
    result = GuardrailResult()

    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            result.action = GuardrailAction.BLOCK
            result.reasons.append(f"Prompt Injection erkannt: {pattern.pattern}")

    pii = detect_pii(text)
    if pii:
        result.pii_found = pii
        if result.action != GuardrailAction.BLOCK:
            result.action = GuardrailAction.WARN
        result.reasons.append(f"{len(pii)} PII-Elemente im Input erkannt")

    if len(text) > 50000:
        result.action = GuardrailAction.BLOCK
        result.reasons.append("Input ueberschreitet Maximallaenge (50.000 Zeichen)")

    return result


def sanitize_output(text: str) -> GuardrailResult:
    result = GuardrailResult()

    pii = detect_pii(text)
    if pii:
        result.pii_found = pii
        result.sanitized_text = mask_irreversible(text, pii)
        result.action = GuardrailAction.WARN
        result.reasons.append(f"{len(pii)} PII-Elemente in AI-Antwort maskiert")
    else:
        result.sanitized_text = text

    return result


def check_and_sanitize(input_text: str) -> tuple[GuardrailResult, Optional[str]]:
    input_check = check_input(input_text)
    if input_check.action == GuardrailAction.BLOCK:
        return input_check, None
    return input_check, input_text
