"""
Resolve voice text to action_id + params. Rule-based first; optional LLM later.
"""

import re
from typing import Dict, List, Optional

from app.schemas.voice import VoiceResolveOut
from app.services.action_registry import action_registry


def _norm(text: str) -> str:
    value = " ".join((text or "").lower().strip().split())
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "Ã¤": "ae",
        "Ã¶": "oe",
        "Ã¼": "ue",
        "ÃŸ": "ss",
        "ÃƒÂ¤": "ae",
        "ÃƒÂ¶": "oe",
        "ÃƒÂ¼": "ue",
        "ÃƒÅ¸": "ss",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value


def _match_phrases(text: str, phrases: List[str]) -> bool:
    normalized = _norm(text)
    for phrase in phrases:
        normalized_phrase = _norm(phrase)
        if not normalized_phrase:
            continue
        if len(normalized_phrase.split()) == 1:
            if normalized == normalized_phrase:
                return True
            continue
        if normalized_phrase in normalized or normalized in normalized_phrase:
            return True
    return False


def _extract_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
    if match:
        params["amount"] = match.group(1).replace(",", ".")
    match = re.search(r"rechnung\s+([a-z0-9\-./]+)", text, re.I)
    if match:
        params["invoice_number"] = match.group(1).strip()
    return params


def _extract_lager_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"\b(\d{8,14})\b", text)
    if match:
        params["ean"] = match.group(1)
    match = re.search(
        r"(\d+(?:[,.]\d+)?)\s*(?:stueck|stück|stk|kg|kilogramm|liter|l|t(?:onnen?)?)\b",
        text,
        re.I,
    )
    if match:
        params["quantity"] = match.group(1).replace(",", ".")
    match = re.search(r"stellplatz\s+([a-z0-9\-]+)", text, re.I)
    if match:
        params["location"] = match.group(1).upper()
    return params


def _extract_einkauf_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
    if match:
        params["amount"] = match.group(1).replace(",", ".")
    match = re.search(r"lieferant\s+([a-z0-9\s]+?)(?:\s+bestellung|\s+rechnung|$)", text, re.I)
    if match:
        params["supplier_name"] = match.group(1).strip()
    return params


def _extract_hr_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    normalized = _norm(text)
    if "urlaub" in normalized:
        params["absence_type"] = "URLAUB"
    elif "krank" in normalized or "krankheit" in normalized:
        params["absence_type"] = "KRANKHEIT"
    elif "fehlzeit" in normalized:
        params["absence_type"] = "FEHLZEIT"
    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
    if match:
        params["date"] = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
    return params


def _voice_out(action_id: str, text: str, params: Optional[Dict[str, str]] = None, confidence: float = 0.85) -> VoiceResolveOut:
    return VoiceResolveOut(
        action_id=action_id,
        params=params or {},
        confidence=confidence,
        raw_text=text.strip(),
    )


def _domain_specific(text: str, normalized: str) -> Optional[VoiceResolveOut]:
    if any(word in normalized for word in ["wareneingang", "ware einbuchen", "eingang buchen"]):
        return _voice_out("lager-wareneingang", text, _extract_lager_params(text), 0.88)
    if any(word in normalized for word in ["inventur", "bestand zaehlen", "zaehlung"]):
        return _voice_out("lager-inventur", text, {}, 0.88)
    if any(word in normalized for word in ["umlagerung", "umlagern", "umbuchen", "stellplatz"]):
        return _voice_out("lager-umlagerung", text, _extract_lager_params(text), 0.85)
    if "artikel im lager suchen" in normalized or "ean suchen" in normalized or (
        "artikel" in normalized and any(word in normalized for word in ["suchen", "finden", "lager", "wo"])
    ):
        return _voice_out("lager-artikel-suche", text, _extract_lager_params(text), 0.85)
    if any(word in normalized for word in ["lager", "lagerverwaltung"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-lager", text)

    if any(word in normalized for word in ["neue bestellung", "bestellung anlegen", "bestellung aufgeben", "bestellen"]):
        return _voice_out("einkauf-bestellung-neu", text, _extract_einkauf_params(text), 0.88)
    if any(word in normalized for word in ["lieferantenrechnung", "eingangsrechnung"]):
        return _voice_out("einkauf-lieferantenrechnung", text, _extract_einkauf_params(text), 0.88)
    if any(word in normalized for word in ["angebot anfragen", "angebotsanfrage", "preisanfrage"]):
        return _voice_out("einkauf-angebot", text, _extract_einkauf_params(text))
    if any(word in normalized for word in ["lieferant suchen", "lieferantensuche", "lieferantenstamm"]):
        return _voice_out("einkauf-lieferant-suche", text)
    if any(word in normalized for word in ["einkauf", "beschaffung", "bestellwesen"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-einkauf", text)

    if any(word in normalized for word in ["abwesenheit", "urlaub eintragen", "krankmeldung", "fehlzeit", "krankheit erfassen"]):
        return _voice_out("hr-abwesenheit", text, _extract_hr_params(text), 0.88)
    if any(word in normalized for word in ["neuer mitarbeiter", "mitarbeiter anlegen", "mitarbeiter aufnehmen"]):
        return _voice_out("hr-mitarbeiter-neu", text, {}, 0.88)
    if any(word in normalized for word in ["lohnlauf", "gehaltsabrechnung", "lohnabrechnung", "loehne berechnen"]):
        return _voice_out("hr-lohnlauf", text, {}, 0.88)
    if any(word in normalized for word in ["mitarbeiter suchen", "mitarbeitersuche"]):
        return _voice_out("hr-mitarbeiter-suche", text)
    if any(word in normalized for word in ["personal", "personalverwaltung", "human resources"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-hr", text)
    return None


class IntentResolver:
    """Resolve transcribed text to action_id and optional params."""

    def resolve(self, text: str, context: Optional[Dict] = None) -> Optional[VoiceResolveOut]:
        if not (text and text.strip()):
            return None

        normalized = _norm(text)
        domain_result = _domain_specific(text, normalized)
        if domain_result:
            return domain_result

        if any(word in normalized for word in ["rechnung", "rechnungen"]) and any(
            word in normalized for word in ["neu", "anlegen", "erstellen"]
        ):
            return _voice_out("action-new-invoice", text)

        for action_id in action_registry.all_ids():
            phrases = action_registry.intent_phrases_for_action(action_id)
            if _match_phrases(normalized, phrases):
                params = _extract_params(text)
                if action_id.startswith("lager-"):
                    params.update(_extract_lager_params(text))
                elif action_id.startswith("einkauf-"):
                    params.update(_extract_einkauf_params(text))
                elif action_id.startswith("hr-"):
                    params.update(_extract_hr_params(text))
                return _voice_out(action_id, text, params, 0.9)

        if any(word in normalized for word in ["speichern", "sichern"]):
            return _voice_out("save-document", text)
        if any(word in normalized for word in ["abbrechen", "zurueck", "schliessen"]):
            return _voice_out("cancel", text, {}, 0.8)
        if any(word in normalized for word in ["auftrag", "auftraege"]) and any(
            word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
        ):
            return _voice_out("nav-orders", text)
        if any(word in normalized for word in ["kunden", "kunde"]) and any(
            word in normalized for word in ["oeffnen", "zeigen", "gehe", "stamm"]
        ):
            return _voice_out("nav-customers", text)
        if any(word in normalized for word in ["dashboard", "start", "uebersicht", "hauptseite"]):
            return _voice_out("nav-dashboard", text)

        return None


intent_resolver = IntentResolver()
