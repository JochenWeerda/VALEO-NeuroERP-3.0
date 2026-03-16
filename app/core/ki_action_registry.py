"""
Kontextsensitive Action Registry fuer KI-Usability und Quick Actions.

Wave 25 zieht die bisher flache Action-Liste auf einen expliziten Contract:
- globale, domain- und maskenspezifische Actions
- priorisierte Surfacing-Hinweise fuer Toolbar, Overflow, Palette und Voice
- deterministische Aufloesung fuer Quick-Action-Consumer
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ActionSurface(str, Enum):
    TOOLBAR_PRIMARY = "toolbar-primary"
    TOOLBAR_OVERFLOW = "toolbar-overflow"
    PALETTE = "palette"
    VOICE = "voice"


class ActionContextScope(str, Enum):
    MASK = "mask"
    DOMAIN = "domain"
    GLOBAL = "global"


class ActionDefinition(BaseModel):
    id: str
    label: str
    label_en: str | None = None
    shortcut: str | None = None
    description: str | None = None
    category: str = "action"
    domain: str | None = None
    mask: str | None = None
    intent_phrases: list[str] = Field(default_factory=list)
    required_data: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    masks: list[str] = Field(default_factory=list)
    surfaces: list[ActionSurface] = Field(default_factory=lambda: [ActionSurface.PALETTE, ActionSurface.VOICE])
    priority: int = 100
    default_params: dict[str, Any] = Field(default_factory=dict)


class ResolvedAction(ActionDefinition):
    context_scope: ActionContextScope
    relevance_score: int


ACTION_DEFINITIONS: list[ActionDefinition] = [
    ActionDefinition(
        id="save-document",
        label="Speichern",
        shortcut="Strg+F4",
        description="Beleg speichern",
        category="Aktionen",
        intent_phrases=["Speichern", "Beleg speichern", "Speichern bitte", "Sichern"],
        masks=["order-editor", "invoice-editor", "invoice", "document", "ap_approval"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=5,
    ),
    ActionDefinition(
        id="print-document",
        label="Drucken",
        shortcut="Strg+F5",
        description="Beleg drucken",
        category="Aktionen",
        intent_phrases=["Drucken", "Beleg drucken"],
        masks=["order-editor", "invoice-editor", "invoice", "document", "ap_approval"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=20,
    ),
    ActionDefinition(
        id="cancel",
        label="Abbrechen",
        shortcut="Esc",
        category="Navigation",
        intent_phrases=["Abbrechen", "Stornieren", "Zurueck"],
        masks=["order-editor", "invoice-editor", "invoice", "document", "ap_approval"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=30,
    ),
    ActionDefinition(
        id="create-invoice",
        label="Sofort-Rechnung",
        shortcut="Strg+F9",
        description="Sofort-Rechnung aus Beleg erstellen",
        category="Aktionen",
        domains=["sales"],
        intent_phrases=["Sofort Rechnung", "Rechnung erstellen"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=15,
    ),
    ActionDefinition(
        id="action-new-order",
        label="Neuer Auftrag",
        shortcut="N A",
        category="Aktionen",
        domain="sales",
        domains=["sales"],
        intent_phrases=["Neuer Auftrag", "Auftrag anlegen"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=10,
    ),
    ActionDefinition(
        id="nav-orders",
        label="Auftraege",
        shortcut="G A",
        category="Navigation",
        domain="sales",
        domains=["sales"],
        intent_phrases=["Auftraege", "Auftragsliste", "Gehe zu Auftraege"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=40,
    ),
    ActionDefinition(
        id="action-new-invoice",
        label="Neue Rechnung",
        category="Aktionen",
        domain="finance",
        domains=["finance"],
        intent_phrases=["Neue Rechnung", "Rechnung anlegen"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=10,
    ),
    ActionDefinition(
        id="nav-fibu",
        label="Finanzbuchhaltung",
        category="Navigation",
        domain="finance",
        domains=["finance"],
        intent_phrases=["Buchhaltung", "Fibu", "Finanzbuchhaltung"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=35,
    ),
    ActionDefinition(
        id="action-new-customer",
        label="Neuer Kunde",
        shortcut="N K",
        category="Aktionen",
        domain="crm",
        domains=["crm"],
        intent_phrases=["Neuer Kunde", "Kunde anlegen"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=10,
    ),
    ActionDefinition(
        id="nav-customers",
        label="Kunden",
        shortcut="G K",
        category="Navigation",
        domain="crm",
        domains=["crm"],
        intent_phrases=["Kunden", "Kundenstamm", "Gehe zu Kunden"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=35,
    ),
    ActionDefinition(
        id="nav-inventory",
        label="Lagerbestand",
        shortcut="G L",
        category="Navigation",
        domain="inventory",
        domains=["inventory"],
        intent_phrases=["Lager", "Lagerbestand", "Gehe zu Lager"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=20,
    ),
    ActionDefinition(
        id="open-customer-selection",
        label="Kundenauswahl",
        shortcut="Strg+F1",
        description="Kundenauswahl-Dialog oeffnen",
        category="Navigation",
        intent_phrases=["Kundenauswahl", "Kunde waehlen", "Kundendialog"],
        masks=["order-editor", "document"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=12,
    ),
    ActionDefinition(
        id="open-article-selection",
        label="Artikelauswahl",
        shortcut="Strg+F2",
        description="Artikelauswahl-Dialog oeffnen",
        category="Navigation",
        intent_phrases=["Artikelauswahl", "Artikel waehlen"],
        masks=["order-editor", "document"],
        surfaces=[ActionSurface.TOOLBAR_PRIMARY, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=14,
    ),
    ActionDefinition(
        id="confirm-position",
        label="Position OK",
        shortcut="Strg+F3",
        description="Aktuelle Position uebernehmen",
        category="Aktionen",
        intent_phrases=["Position uebernehmen", "Position OK"],
        masks=["order-editor", "document"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=22,
    ),
    ActionDefinition(
        id="delete-document",
        label="Loeschen",
        shortcut="Strg+F6",
        description="Beleg loeschen",
        category="danger",
        intent_phrases=["Loeschen", "Beleg loeschen"],
        masks=["invoice", "document", "ap_approval"],
        surfaces=[ActionSurface.TOOLBAR_OVERFLOW, ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=90,
    ),
    ActionDefinition(
        id="nav-dashboard",
        label="Dashboard",
        shortcut="G D",
        category="navigation",
        intent_phrases=["Dashboard", "Startseite", "Uebersicht"],
        surfaces=[ActionSurface.PALETTE, ActionSurface.VOICE],
        priority=60,
    ),
]


_ACTION_BY_ID: dict[str, ActionDefinition] = {action.id: action for action in ACTION_DEFINITIONS}


def get_action_definition(action_id: str) -> ActionDefinition | None:
    return _ACTION_BY_ID.get(action_id)


def list_action_definitions() -> list[ActionDefinition]:
    return list(ACTION_DEFINITIONS)


def _matches_mask(action: ActionDefinition, mask: str | None) -> bool:
    if not mask:
        return False
    candidates = set(action.masks)
    if action.mask:
        candidates.add(action.mask)
    return mask in candidates


def _matches_domain(action: ActionDefinition, domain: str | None) -> bool:
    if not domain:
        return False
    candidates = set(action.domains)
    if action.domain:
        candidates.add(action.domain)
    return domain in candidates


def _compute_match(action: ActionDefinition, domain: str | None, mask: str | None) -> tuple[ActionContextScope, int] | None:
    if _matches_mask(action, mask):
        return (ActionContextScope.MASK, 300 - action.priority)
    if _matches_domain(action, domain):
        return (ActionContextScope.DOMAIN, 200 - action.priority)
    if not action.domains and not action.masks and action.domain is None and action.mask is None:
        return (ActionContextScope.GLOBAL, 100 - action.priority)
    return None


def resolve_actions_for_context(domain: str | None = None, mask: str | None = None) -> list[ResolvedAction]:
    resolved: list[ResolvedAction] = []
    for action in ACTION_DEFINITIONS:
        match = _compute_match(action, domain, mask)
        if match is None:
            continue
        scope, score = match
        resolved.append(
            ResolvedAction(
                **action.model_dump(),
                context_scope=scope,
                relevance_score=score,
            )
        )

    resolved.sort(key=lambda action: (-action.relevance_score, action.priority, action.label.lower()))
    return resolved
