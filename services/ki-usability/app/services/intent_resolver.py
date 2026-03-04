"""
Resolve voice text to action_id + params. Rule-based first; optional LLM later.
"""

import re
from typing import Dict, List, Optional

from app.schemas.voice import VoiceResolveOut
from app.services.action_registry import action_registry

# Normalize: lowercase, strip, collapse spaces
def _norm(t: str) -> str:
    return " ".join((t or "").lower().strip().split())


def _match_phrases(text: str, phrases: List[str]) -> bool:
    n = _norm(text)
    for p in phrases:
        if _norm(p) in n or n in _norm(p):
            return True
    return False


def _extract_params(text: str) -> Dict[str, str]:
    """Simple entity extraction (e.g. numbers, quoted strings)."""
    params: Dict[str, str] = {}
    # Betrag X Euro
    m = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
    if m:
        params["amount"] = m.group(1).replace(",", ".")
    # Rechnung XY
    m = re.search(r"rechnung\s+([a-z0-9\-./]+)", text, re.I)
    if m:
        params["invoice_number"] = m.group(1).strip()
    return params


class IntentResolver:
    """Resolve transcribed text to action_id and optional params."""

    def resolve(self, text: str, context: Optional[Dict] = None) -> Optional[VoiceResolveOut]:
        if not (text and text.strip()):
            return None
        norm_text = _norm(text)

        # 1) Try exact phrase match on all actions
        for action_id in action_registry.all_ids():
            phrases = action_registry.intent_phrases_for_action(action_id)
            if _match_phrases(norm_text, phrases):
                params = _extract_params(text)
                return VoiceResolveOut(
                    action_id=action_id,
                    params=params,
                    confidence=0.9,
                    raw_text=text.strip(),
                )

        # 2) Keyword fallbacks
        if any(w in norm_text for w in ["speichern", "sichern"]):
            return VoiceResolveOut(
                action_id="save-document",
                params={},
                confidence=0.85,
                raw_text=text.strip(),
            )
        if any(w in norm_text for w in ["abbrechen", "zurück", "schließen"]):
            return VoiceResolveOut(
                action_id="cancel",
                params={},
                confidence=0.8,
                raw_text=text.strip(),
            )
        if any(w in norm_text for w in ["auftrag", "aufträge"]) and any(
            w in norm_text for w in ["öffnen", "zeigen", "gehe", "geh"]
        ):
            return VoiceResolveOut(
                action_id="nav-orders",
                params={},
                confidence=0.85,
                raw_text=text.strip(),
            )
        if any(w in norm_text for w in ["rechnung", "rechnungen"]) and any(
            w in norm_text for w in ["neu", "anlegen", "erstellen"]
        ):
            return VoiceResolveOut(
                action_id="action-new-invoice",
                params={},
                confidence=0.85,
                raw_text=text.strip(),
            )
        if any(w in norm_text for w in ["kunden", "kunde"]) and any(
            w in norm_text for w in ["öffnen", "zeigen", "gehe", "stamm"]
        ):
            return VoiceResolveOut(
                action_id="nav-customers",
                params={},
                confidence=0.85,
                raw_text=text.strip(),
            )
        if any(w in norm_text for w in ["dashboard", "start", "übersicht", "hauptseite"]):
            return VoiceResolveOut(
                action_id="nav-dashboard",
                params={},
                confidence=0.85,
                raw_text=text.strip(),
            )

        return None


intent_resolver = IntentResolver()
