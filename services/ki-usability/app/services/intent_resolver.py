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


def _extract_verkauf_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"kunde\s+([a-z0-9\s\-]+?)(?:\s+angebot|\s+auftrag|$)", text, re.I)
    if match:
        params["customer_name"] = match.group(1).strip()
    match = re.search(r"artikel\s+([a-z0-9\-./]+)", text, re.I)
    if match:
        params["article_number"] = match.group(1).strip()
    match = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
    if match:
        params["amount"] = match.group(1).replace(",", ".")
    return params


def _extract_crm_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"kontakt\s+([a-z0-9\s\-]+?)(?:\s+suchen|\s+finden|$)", text, re.I)
    if match:
        params["contact_name"] = match.group(1).strip()
    match = re.search(r"lead\s+([a-z0-9\s\-]+?)(?:\s+anlegen|\s+erfassen|$)", text, re.I)
    if match:
        params["lead_name"] = match.group(1).strip()
    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
    if match:
        params["date"] = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
    return params


def _extract_finance_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
    if match:
        params["amount"] = match.group(1).replace(",", ".")
    match = re.search(r"konto\s+([0-9]{3,8})", text, re.I)
    if match:
        params["account_number"] = match.group(1)
    match = re.search(r"periode\s+(\d{4}[-/]?\d{0,2})", text, re.I)
    if match:
        params["period"] = match.group(1).replace("/", "-")
    return params


def _extract_compliance_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"art\.?\s*(\d{1,2})", text, re.I)
    if match:
        params["gdpr_article"] = match.group(1)
    return params


def _extract_agrar_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"(\d+(?:[,.]\d+)?)\s*(?:t|tonnen|dt|dt\/ha)\b", text, re.I)
    if match:
        params["quantity"] = match.group(1).replace(",", ".")
    match = re.search(r"kultur\s+([a-zäöüß]+)", text, re.I)
    if match:
        params["crop"] = match.group(1).strip()
    match = re.search(r"schlag\s+([a-z0-9\-]+)", text, re.I)
    if match:
        params["field_id"] = match.group(1).upper()
    return params


def _extract_logistik_params(text: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    match = re.search(r"tour\s+([a-z0-9\-]+)", text, re.I)
    if match:
        params["tour_id"] = match.group(1).strip()
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

    if any(word in normalized for word in ["neues angebot", "angebot anlegen", "verkaufsangebot"]):
        return _voice_out("verkauf-angebot-neu", text, _extract_verkauf_params(text), 0.88)
    if any(word in normalized for word in ["neuer lieferschein", "lieferschein anlegen", "lieferung erfassen"]):
        return _voice_out("verkauf-lieferschein-neu", text, _extract_verkauf_params(text), 0.88)
    if "angebotsliste" in normalized or ("angebote" in normalized and any(word in normalized for word in ["zeigen", "oeffnen", "gehe"])):
        return _voice_out("nav-angebote", text)
    if "lieferscheinliste" in normalized or ("lieferschein" in normalized and any(word in normalized for word in ["zeigen", "oeffnen", "gehe"])):
        return _voice_out("nav-lieferscheine", text)
    if any(word in normalized for word in ["verkauf", "vertrieb"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-verkauf", text)
    if "kundenstamm suchen" in normalized or "verkaufskunde finden" in normalized:
        return _voice_out("verkauf-kunde-suche", text, _extract_verkauf_params(text))
    if "verkaufsartikel suchen" in normalized or "artikelstamm oeffnen" in normalized:
        return _voice_out("verkauf-artikel-suche", text, _extract_verkauf_params(text))

    if any(word in normalized for word in ["neuer lead", "lead anlegen", "verkaufschance anlegen"]):
        return _voice_out("crm-lead-neu", text, _extract_crm_params(text), 0.88)
    if any(word in normalized for word in ["neue aktivitaet", "aktivitaet anlegen", "termin erfassen crm"]):
        return _voice_out("crm-aktivitaet-neu", text, _extract_crm_params(text), 0.88)
    if any(word in normalized for word in ["kontakt suchen", "kontaktsuche crm", "kontakt finden"]):
        return _voice_out("crm-kontakt-suche", text, _extract_crm_params(text))
    if "leadliste" in normalized or ("leads" in normalized and any(word in normalized for word in ["zeigen", "oeffnen", "gehe"])):
        return _voice_out("nav-crm-leads", text)
    if "aktivitaetenliste" in normalized or ("aktivitaeten" in normalized and any(word in normalized for word in ["zeigen", "oeffnen", "gehe"])):
        return _voice_out("nav-crm-aktivitaeten", text)
    if "betriebsprofile" in normalized and any(word in normalized for word in ["zeigen", "oeffnen", "gehe"]):
        return _voice_out("nav-crm-betriebsprofile", text)
    if "kontaktliste" in normalized or ("kontakte" in normalized and any(word in normalized for word in ["zeigen", "oeffnen", "gehe"])):
        return _voice_out("nav-crm-kontakte", text)
    if any(word in normalized for word in ["crm", "marketing"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-crm", text)

    if any(word in normalized for word in ["buchung erfassen", "neue buchung", "fibu buchen"]):
        return _voice_out("finance-booking", text, _extract_finance_params(text), 0.88)
    if "op debitoren" in normalized or "offene posten debitoren" in normalized:
        return _voice_out("nav-op-debitoren", text)
    if "op kreditoren" in normalized or "offene posten kreditoren" in normalized:
        return _voice_out("nav-op-kreditoren", text)
    if "zahlungslauf" in normalized or "zahlungslaeufe" in normalized:
        return _voice_out("nav-zahlungslaeufe", text)
    if "buchungsjournal" in normalized or "journal oeffnen" in normalized:
        return _voice_out("nav-buchungsjournal", text)
    if "ustva" in normalized or "umsatzsteuer voranmeldung" in normalized:
        return _voice_out("nav-ustva", text)
    if "bilanz oeffnen" in normalized or "gehe zur bilanz" in normalized:
        return _voice_out("nav-bilanz", text)
    if "hauptbuch" in normalized and any(word in normalized for word in ["oeffnen", "zeigen", "gehe"]):
        return _voice_out("nav-fibu-hauptbuch", text)

    if "verarbeitungsverzeichnis" in normalized or "ropa oeffnen" in normalized:
        return _voice_out("nav-verarbeitungsverzeichnis", text, _extract_compliance_params(text))
    if "datenpanne" in normalized or "breach meldung" in normalized:
        return _voice_out("nav-datenpannen", text, _extract_compliance_params(text))
    if "dsgvo anfragen" in normalized or "betroffenenanfrage" in normalized:
        return _voice_out("compliance-dsgvo-anfragen", text)
    if "sanktionspruefung" in normalized or "sanktionsliste pruefen" in normalized:
        return _voice_out("nav-sanktionspruefung", text)
    if "compliance dashboard" in normalized or ("compliance" in normalized and any(word in normalized for word in ["oeffnen", "zeigen", "gehe"])):
        return _voice_out("nav-compliance-dashboard", text)

    if any(word in normalized for word in ["ernte erfassen", "ernte annehmen", "harvest erfassen"]):
        return _voice_out("agrar-ernte-erfassen", text, _extract_agrar_params(text), 0.88)
    if "ernte annahme" in normalized or "ernteannahme" in normalized:
        return _voice_out("nav-ernte-annahme", text, _extract_agrar_params(text))
    if "rohware annahme" in normalized or "rohstoff annahme" in normalized:
        return _voice_out("nav-rohware-annahme", text, _extract_agrar_params(text))
    if "agrar vertraege" in normalized or "agrarvertraegen" in normalized:
        return _voice_out("nav-agrar-vertraege", text)
    if "schlagkartei" in normalized or ("schlaege" in normalized and any(word in normalized for word in ["oeffnen", "zeigen", "gehe"])):
        return _voice_out("nav-schlaege", text, _extract_agrar_params(text))
    if "feldbuch" in normalized and any(word in normalized for word in ["oeffnen", "zeigen", "gehe"]):
        return _voice_out("nav-feldbuch", text)
    if "silo status" in normalized or ("silos" in normalized and any(word in normalized for word in ["oeffnen", "zeigen", "gehe"])):
        return _voice_out("nav-silos", text)
    if any(word in normalized for word in ["agrar", "warenwirtschaft agrar"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-agrar", text)

    if any(word in normalized for word in ["tour planen", "neue tour", "lieferung planen"]):
        return _voice_out("logistik-tour-planen", text, _extract_logistik_params(text), 0.88)
    if "tourenplanung" in normalized or "tourplanung" in normalized:
        return _voice_out("nav-tourenplanung", text, _extract_logistik_params(text))
    if "frachtbrief" in normalized:
        return _voice_out("nav-frachtbriefe", text)
    if "versandprofil" in normalized:
        return _voice_out("nav-versandprofile", text)
    if any(word in normalized for word in ["logistik", "disposition logistik"]) and any(
        word in normalized for word in ["oeffnen", "zeigen", "gehe", "geh"]
    ):
        return _voice_out("nav-logistik", text)
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
                elif action_id.startswith("verkauf-"):
                    params.update(_extract_verkauf_params(text))
                elif action_id.startswith("crm-"):
                    params.update(_extract_crm_params(text))
                elif action_id.startswith("nav-crm"):
                    params.update(_extract_crm_params(text))
                elif action_id.startswith("finance-") or action_id.startswith("nav-op-") or action_id.startswith("nav-zahlungs") or action_id.startswith("nav-buchungs") or action_id.startswith("nav-ustva") or action_id.startswith("nav-bilanz") or action_id.startswith("nav-fibu-"):
                    params.update(_extract_finance_params(text))
                elif action_id.startswith("compliance-") or action_id.startswith("nav-verarbeitungs") or action_id.startswith("nav-datenpannen") or action_id.startswith("nav-sanktions") or action_id.startswith("nav-compliance"):
                    params.update(_extract_compliance_params(text))
                elif action_id.startswith("agrar-") or action_id.startswith("nav-ernte") or action_id.startswith("nav-agrar") or action_id.startswith("nav-schlaege") or action_id.startswith("nav-silos") or action_id.startswith("nav-rohware") or action_id.startswith("nav-feldbuch"):
                    params.update(_extract_agrar_params(text))
                elif action_id.startswith("logistik-") or action_id.startswith("nav-logistik") or action_id.startswith("nav-touren") or action_id.startswith("nav-fracht") or action_id.startswith("nav-versand"):
                    params.update(_extract_logistik_params(text))
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
