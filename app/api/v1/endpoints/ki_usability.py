"""
KI-Usability API — im Haupt-Backend integriert.
Ermöglicht Single-Process-Dev ohne separaten ki-usability-Service.
Frontend: /api/ki-usability → Proxy oder direkter Aufruf /api/ki-usability/api/v1/*
"""

from typing import Any, Dict, List, Optional

import re
from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field

# Schemas (abgestimmt mit packages/frontend-web und services/ki-usability)
class ActionOut(BaseModel):
    id: str
    label: str
    label_en: Optional[str] = None
    shortcut: Optional[str] = None
    description: Optional[str] = None
    category: str = "action"
    domain: Optional[str] = None
    mask: Optional[str] = None
    intent_phrases: List[str] = Field(default_factory=list)
    required_data: List[str] = Field(default_factory=list)


class ActionListResponse(BaseModel):
    actions: List[ActionOut]
    total: int


class VoiceResolveIn(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None


class VoiceResolveOut(BaseModel):
    action_id: str
    params: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    raw_text: str


# Action Registry (gleiche IDs wie Frontend)
ACTIONS: List[ActionOut] = [
    ActionOut(id="open-customer-selection", label="Kundenauswahl", shortcut="Strg+F1", description="Kundenauswahl-Dialog öffnen", category="Navigation", intent_phrases=["Kundenauswahl", "Kunde wählen", "Kundendialog"]),
    ActionOut(id="open-article-selection", label="Artikelauswahl", shortcut="Strg+F2", description="Artikelauswahl-Dialog öffnen", category="Navigation", intent_phrases=["Artikelauswahl", "Artikel wählen"]),
    ActionOut(id="confirm-position", label="Position OK", shortcut="Strg+F3", description="Aktuelle Position übernehmen", category="Aktionen", intent_phrases=["Position übernehmen", "Position OK"]),
    ActionOut(id="save-document", label="Speichern", shortcut="Strg+F4", description="Beleg speichern", category="Aktionen", intent_phrases=["Speichern", "Beleg speichern", "Speichern bitte", "Sichern"]),
    ActionOut(id="print-document", label="Drucken", shortcut="Strg+F5", description="Beleg drucken", category="Aktionen", intent_phrases=["Drucken", "Beleg drucken"]),
    ActionOut(id="delete-document", label="Löschen", shortcut="Strg+F6", description="Beleg löschen", category="Aktionen", intent_phrases=["Löschen", "Beleg löschen"]),
    ActionOut(id="close-document", label="Schließen", shortcut="Strg+F7", description="Beleg schließen", category="Navigation", intent_phrases=["Schließen", "Beleg schließen"]),
    ActionOut(id="copy-previous-positions", label="Wie vorheriger (nur Positionen)", shortcut="Strg+F8", category="Aktionen", intent_phrases=["Wie vorherige Positionen"]),
    ActionOut(id="create-invoice", label="Sofort-Rechnung", shortcut="Strg+F9", description="Sofort-Rechnung aus Beleg erstellen", category="Aktionen", intent_phrases=["Sofort Rechnung", "Rechnung erstellen"]),
    ActionOut(id="open-attachments", label="Unterlagen", shortcut="Strg+F10", category="Navigation", intent_phrases=["Unterlagen", "Anhänge"]),
    ActionOut(id="copy-previous-full", label="Wie vorheriger Beleg", shortcut="F11", category="Aktionen", intent_phrases=["Wie vorheriger Beleg"]),
    ActionOut(id="show-information", label="Information", shortcut="Strg+F12", category="Navigation", intent_phrases=["Information", "Info"]),
    ActionOut(id="cancel", label="Abbrechen", shortcut="Esc", category="Navigation", intent_phrases=["Abbrechen", "Stornieren", "Zurück"]),
    ActionOut(id="nav-dashboard", label="Dashboard", shortcut="G D", category="navigation", intent_phrases=["Dashboard", "Startseite", "Übersicht"]),
    ActionOut(id="nav-customers", label="Kunden", shortcut="G K", domain="crm", intent_phrases=["Kunden", "Kundenstamm", "Gehe zu Kunden"]),
    ActionOut(id="nav-orders", label="Aufträge", shortcut="G A", domain="sales", intent_phrases=["Aufträge", "Auftragsliste", "Gehe zu Aufträge"]),
    ActionOut(id="nav-invoices", label="Rechnungen", shortcut="G R", domain="sales", intent_phrases=["Rechnungen", "Rechnungsliste"]),
    ActionOut(id="nav-inventory", label="Lagerbestand", shortcut="G L", domain="inventory", intent_phrases=["Lager", "Lagerbestand", "Gehe zu Lager"]),
    ActionOut(id="nav-fibu", label="Finanzbuchhaltung", domain="finance", intent_phrases=["Buchhaltung", "Fibu", "Finanzbuchhaltung"]),
    ActionOut(id="action-new-order", label="Neuer Auftrag", shortcut="N A", domain="sales", intent_phrases=["Neuer Auftrag", "Auftrag anlegen"]),
    ActionOut(id="action-new-invoice", label="Neue Rechnung", domain="finance", intent_phrases=["Neue Rechnung", "Rechnung anlegen"]),
    ActionOut(id="action-new-customer", label="Neuer Kunde", shortcut="N K", domain="crm", intent_phrases=["Neuer Kunde", "Kunde anlegen"]),
]

_ACTION_BY_ID = {a.id: a for a in ACTIONS}


def _norm(t: str) -> str:
    return " ".join((t or "").lower().strip().split())


def _match_phrases(text: str, phrases: List[str]) -> bool:
    n = _norm(text)
    for p in phrases:
        if _norm(p) in n or n in _norm(p):
            return True
    return False


def _resolve_intent(text: str) -> Optional[VoiceResolveOut]:
    if not (text and text.strip()):
        return None
    norm_text = _norm(text)
    for action_id, a in _ACTION_BY_ID.items():
        if _match_phrases(norm_text, a.intent_phrases):
            params: Dict[str, Any] = {}
            m = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
            if m:
                params["amount"] = m.group(1).replace(",", ".")
            return VoiceResolveOut(action_id=action_id, params=params, confidence=0.9, raw_text=text.strip())
    if any(w in norm_text for w in ["speichern", "sichern"]):
        return VoiceResolveOut(action_id="save-document", params={}, confidence=0.85, raw_text=text.strip())
    if any(w in norm_text for w in ["abbrechen", "zurück", "schließen"]):
        return VoiceResolveOut(action_id="cancel", params={}, confidence=0.8, raw_text=text.strip())
    return None


# Routers
actions_router = APIRouter()
voice_router = APIRouter()


@actions_router.get("", response_model=ActionListResponse)
def list_actions(domain: Optional[str] = None, mask: Optional[str] = None) -> ActionListResponse:
    result = list(ACTIONS)
    if domain:
        result = [a for a in result if a.domain is None or a.domain == domain]
    if mask:
        result = [a for a in result if a.mask is None or a.mask == mask]
    return ActionListResponse(actions=result, total=len(result))


@actions_router.get("/{action_id}", response_model=ActionOut)
def get_action(action_id: str) -> ActionOut:
    a = _ACTION_BY_ID.get(action_id)
    if not a:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    return a


@voice_router.post("/resolve", response_model=VoiceResolveOut | None)
def resolve_voice(body: VoiceResolveIn) -> VoiceResolveOut | None:
    return _resolve_intent(body.text)


router = APIRouter(tags=["ki-usability"])
router.include_router(actions_router, prefix="/actions")
router.include_router(voice_router, prefix="/voice")
