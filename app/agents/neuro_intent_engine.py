"""
Neuro Intent Engine — NC-A1/A2
Klassifiziert User-Input in einen Intent mit Confidence, Risk-Class und Capability-Matching.
Dockt an die bestehende NeuroASSIST-Capability-Registry an.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RiskClass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IntentCategory(str, Enum):
    QUERY = "query"
    COMMAND = "command"
    NAVIGATION = "navigation"
    ANALYSIS = "analysis"
    APPROVAL = "approval"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    intent: str
    category: IntentCategory
    confidence_score: float
    risk_class: RiskClass
    explanation: str
    requested_action: Optional[str] = None
    matched_capability: Optional[str] = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "category": self.category.value,
            "confidence_score": self.confidence_score,
            "risk_class": self.risk_class.value,
            "explanation": self.explanation,
            "requested_action": self.requested_action,
            "matched_capability": self.matched_capability,
            "parameters": self.parameters,
        }


INTENT_PATTERNS: list[dict] = [
    {
        "intent": "bestellung_anlegen",
        "category": IntentCategory.COMMAND,
        "patterns": [
            re.compile(r"bestell(ung|en)?\s+(anlegen|erstellen|aufgeben)", re.IGNORECASE),
            re.compile(r"(neue[rn]?\s+)?bestellung", re.IGNORECASE),
            re.compile(r"nachbestell(ung|en)", re.IGNORECASE),
            re.compile(r"einkauf.*bestell", re.IGNORECASE),
        ],
        "capability": "bestellvorschlag_assistant",
        "risk_class": RiskClass.MEDIUM,
    },
    {
        "intent": "skonto_pruefen",
        "category": IntentCategory.ANALYSIS,
        "patterns": [
            re.compile(r"skonto", re.IGNORECASE),
            re.compile(r"zahlungsfrist", re.IGNORECASE),
            re.compile(r"fruehzahler", re.IGNORECASE),
        ],
        "capability": "finance_skonto_assistant",
        "risk_class": RiskClass.LOW,
    },
    {
        "intent": "compliance_pruefen",
        "category": IntentCategory.ANALYSIS,
        "patterns": [
            re.compile(r"compliance", re.IGNORECASE),
            re.compile(r"vorschrift", re.IGNORECASE),
            re.compile(r"pruef(ung|en)", re.IGNORECASE),
            re.compile(r"qs.?check", re.IGNORECASE),
            re.compile(r"zulassung", re.IGNORECASE),
        ],
        "capability": "compliance_copilot",
        "risk_class": RiskClass.LOW,
    },
    {
        "intent": "datenqualitaet_pruefen",
        "category": IntentCategory.ANALYSIS,
        "patterns": [
            re.compile(r"datenqualit", re.IGNORECASE),
            re.compile(r"duplikat", re.IGNORECASE),
            re.compile(r"bereinig(ung|en)", re.IGNORECASE),
            re.compile(r"stammdaten.*pr(ue|ü)f", re.IGNORECASE),
        ],
        "capability": "data_quality_assistant",
        "risk_class": RiskClass.LOW,
    },
    {
        "intent": "ausnahme_behandeln",
        "category": IntentCategory.COMMAND,
        "patterns": [
            re.compile(r"ausnahme", re.IGNORECASE),
            re.compile(r"fehler.*beheb", re.IGNORECASE),
            re.compile(r"st(oe|ö)rung", re.IGNORECASE),
            re.compile(r"eskalat", re.IGNORECASE),
        ],
        "capability": "operations_exception_assistant",
        "risk_class": RiskClass.HIGH,
    },
    {
        "intent": "system_optimieren",
        "category": IntentCategory.ANALYSIS,
        "patterns": [
            re.compile(r"optimier", re.IGNORECASE),
            re.compile(r"performance", re.IGNORECASE),
            re.compile(r"beschleunig", re.IGNORECASE),
        ],
        "capability": "system_optimizer",
        "risk_class": RiskClass.LOW,
    },
    {
        "intent": "auftrag_anlegen",
        "category": IntentCategory.COMMAND,
        "patterns": [
            re.compile(r"auftrag\s+(anlegen|erstellen)", re.IGNORECASE),
            re.compile(r"verkaufsauftrag", re.IGNORECASE),
            re.compile(r"kundenauftrag", re.IGNORECASE),
        ],
        "capability": None,
        "risk_class": RiskClass.MEDIUM,
    },
    {
        "intent": "rechnung_erstellen",
        "category": IntentCategory.COMMAND,
        "patterns": [
            re.compile(r"rechnung\s+(erstellen|anlegen|schreiben)", re.IGNORECASE),
            re.compile(r"faktur", re.IGNORECASE),
        ],
        "capability": None,
        "risk_class": RiskClass.HIGH,
    },
    {
        "intent": "lagerbestand_abfragen",
        "category": IntentCategory.QUERY,
        "patterns": [
            re.compile(r"lagerbestand", re.IGNORECASE),
            re.compile(r"bestand\s+(abfragen|pr(ue|ü)fen|anzeigen)", re.IGNORECASE),
            re.compile(r"vorrat", re.IGNORECASE),
            re.compile(r"wie\s+viel.*lager", re.IGNORECASE),
        ],
        "capability": None,
        "risk_class": RiskClass.LOW,
    },
    {
        "intent": "navigation",
        "category": IntentCategory.NAVIGATION,
        "patterns": [
            re.compile(r"(gehe?|navigiere?|oeffne|zeig)\s+(zu|mir|die|den|das)", re.IGNORECASE),
            re.compile(r"wo\s+(finde|ist|sind)", re.IGNORECASE),
        ],
        "capability": None,
        "risk_class": RiskClass.LOW,
    },
    {
        "intent": "freigabe_erteilen",
        "category": IntentCategory.APPROVAL,
        "patterns": [
            re.compile(r"freigabe", re.IGNORECASE),
            re.compile(r"genehmig", re.IGNORECASE),
            re.compile(r"approve", re.IGNORECASE),
        ],
        "capability": None,
        "risk_class": RiskClass.HIGH,
    },
]

RISK_KEYWORDS: dict[str, RiskClass] = {
    "loeschen": RiskClass.CRITICAL,
    "stornieren": RiskClass.HIGH,
    "freigeben": RiskClass.HIGH,
    "buchen": RiskClass.MEDIUM,
    "aendern": RiskClass.MEDIUM,
    "anlegen": RiskClass.MEDIUM,
    "anzeigen": RiskClass.LOW,
    "suchen": RiskClass.LOW,
    "abfragen": RiskClass.LOW,
}


def classify(user_input: str, context: Optional[dict] = None) -> IntentResult:
    if not user_input or not user_input.strip():
        return IntentResult(
            intent="unknown",
            category=IntentCategory.UNKNOWN,
            confidence_score=0.0,
            risk_class=RiskClass.LOW,
            explanation="Leerer Input",
        )

    text = user_input.strip()
    ctx = context or {}

    best_match: Optional[dict] = None
    best_score = 0.0

    for entry in INTENT_PATTERNS:
        for pattern in entry["patterns"]:
            match = pattern.search(text)
            if match:
                span_ratio = (match.end() - match.start()) / len(text)
                score = 0.6 + min(span_ratio * 0.4, 0.35)

                if ctx.get("current_page", "").startswith(entry.get("capability", "") or ""):
                    score = min(score + 0.1, 1.0)

                if score > best_score:
                    best_score = score
                    best_match = entry

    if best_match and best_score >= 0.5:
        risk = best_match["risk_class"]
        for keyword, keyword_risk in RISK_KEYWORDS.items():
            if keyword in text.lower() and keyword_risk.value > risk.value:
                risk = keyword_risk

        return IntentResult(
            intent=best_match["intent"],
            category=best_match["category"],
            confidence_score=round(best_score, 3),
            risk_class=risk,
            explanation=f"Pattern-Match fuer '{best_match['intent']}' mit Score {best_score:.3f}",
            matched_capability=best_match.get("capability"),
            requested_action=best_match["intent"],
            parameters=_extract_parameters(text, best_match["intent"]),
        )

    return IntentResult(
        intent="unknown",
        category=IntentCategory.UNKNOWN,
        confidence_score=0.1,
        risk_class=RiskClass.LOW,
        explanation="Kein Pattern-Match — Fallback auf unknown",
    )


def _extract_parameters(text: str, intent: str) -> dict:
    params: dict[str, Any] = {}

    amount_match = re.search(r"(\d+[\.,]?\d*)\s*(EUR|Euro|€)", text, re.IGNORECASE)
    if amount_match:
        params["amount"] = float(amount_match.group(1).replace(",", "."))
        params["currency"] = "EUR"

    qty_match = re.search(r"(\d+[\.,]?\d*)\s*(Stueck|St\.|Stk|kg|t|Tonnen?|Liter|l)\b", text, re.IGNORECASE)
    if qty_match:
        params["quantity"] = float(qty_match.group(1).replace(",", "."))
        params["unit"] = qty_match.group(2)

    article_match = re.search(r"Artikel\s+(\S+)", text, re.IGNORECASE)
    if article_match:
        params["article_ref"] = article_match.group(1)

    return params


def get_supported_intents() -> list[dict]:
    return [
        {
            "intent": entry["intent"],
            "category": entry["category"].value,
            "capability": entry.get("capability"),
            "risk_class": entry["risk_class"].value,
        }
        for entry in INTENT_PATTERNS
    ]
