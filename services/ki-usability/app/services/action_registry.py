"""
Central action registry: same IDs as frontend PageToolbar, Command Palette, global-shortcuts.
Used for GET /actions and for voice-to-intent resolution.
"""

from typing import Dict, List, Optional

from app.schemas.actions import ActionOut

# Built-in actions: aligned with packages/frontend-web GLOBAL_SHORTCUTS + CommandPalette
ACTIONS: List[ActionOut] = [
    # Global shortcuts (Belegaktionen)
    ActionOut(
        id="open-customer-selection",
        label="Kundenauswahl",
        shortcut="Strg+F1",
        description="Kundenauswahl-Dialog öffnen",
        category="Navigation",
        domain=None,
        intent_phrases=["Kundenauswahl", "Kunde wählen", "Kundendialog", "Kunde suchen"],
    ),
    ActionOut(
        id="open-article-selection",
        label="Artikelauswahl",
        shortcut="Strg+F2",
        description="Artikelauswahl-Dialog öffnen",
        category="Navigation",
        domain=None,
        intent_phrases=["Artikelauswahl", "Artikel wählen", "Artikel suchen"],
    ),
    ActionOut(
        id="confirm-position",
        label="Position OK",
        shortcut="Strg+F3",
        description="Aktuelle Position übernehmen",
        category="Aktionen",
        domain=None,
        intent_phrases=["Position übernehmen", "Position OK", "Position bestätigen"],
    ),
    ActionOut(
        id="save-document",
        label="Speichern",
        shortcut="Strg+F4",
        description="Beleg speichern",
        category="Aktionen",
        domain=None,
        intent_phrases=["Speichern", "Beleg speichern", "Speichern bitte", "Sichern"],
    ),
    ActionOut(
        id="print-document",
        label="Drucken",
        shortcut="Strg+F5",
        description="Beleg drucken",
        category="Aktionen",
        domain=None,
        intent_phrases=["Drucken", "Beleg drucken", "Druck"],
    ),
    ActionOut(
        id="delete-document",
        label="Löschen",
        shortcut="Strg+F6",
        description="Beleg löschen",
        category="Aktionen",
        domain=None,
        intent_phrases=["Löschen", "Beleg löschen", "Entfernen"],
    ),
    ActionOut(
        id="close-document",
        label="Schließen",
        shortcut="Strg+F7",
        description="Beleg schließen",
        category="Navigation",
        domain=None,
        intent_phrases=["Schließen", "Beleg schließen", "Fenster schließen"],
    ),
    ActionOut(
        id="copy-previous-positions",
        label="Wie vorheriger (nur Positionen)",
        shortcut="Strg+F8",
        description="Nur Positionen vom vorherigen Beleg übernehmen",
        category="Aktionen",
        domain=None,
        intent_phrases=["Wie vorherige Positionen", "Positionen übernehmen"],
    ),
    ActionOut(
        id="create-invoice",
        label="Sofort-Rechnung",
        shortcut="Strg+F9",
        description="Sofort-Rechnung aus Beleg erstellen",
        category="Aktionen",
        domain=None,
        intent_phrases=["Sofort Rechnung", "Rechnung erstellen", "Rechnung aus Beleg"],
    ),
    ActionOut(
        id="open-attachments",
        label="Unterlagen",
        shortcut="Strg+F10",
        description="Unterlagen-Dialog öffnen",
        category="Navigation",
        domain=None,
        intent_phrases=["Unterlagen", "Anhänge", "Dokumente"],
    ),
    ActionOut(
        id="copy-previous-full",
        label="Wie vorheriger Beleg",
        shortcut="F11",
        description="Alle Daten vom vorherigen Beleg übernehmen",
        category="Aktionen",
        domain=None,
        intent_phrases=["Wie vorheriger Beleg", "Vorherigen Beleg übernehmen"],
    ),
    ActionOut(
        id="show-information",
        label="Information",
        shortcut="Strg+F12",
        description="Informationen anzeigen",
        category="Navigation",
        domain=None,
        intent_phrases=["Information", "Info", "Informationen anzeigen"],
    ),
    ActionOut(
        id="cancel",
        label="Abbrechen",
        shortcut="Esc",
        description="Aktuelle Aktion abbrechen",
        category="Navigation",
        domain=None,
        intent_phrases=["Abbrechen", "Stornieren", "Zurück"],
    ),
    # Navigation (Command Palette style)
    ActionOut(
        id="nav-dashboard",
        label="Dashboard",
        shortcut="G D",
        description="Zur Startseite",
        category="navigation",
        domain=None,
        intent_phrases=["Dashboard", "Startseite", "Übersicht", "Hauptseite"],
    ),
    ActionOut(
        id="nav-customers",
        label="Kunden",
        shortcut="G K",
        description="Kundenstamm öffnen",
        category="navigation",
        domain="crm",
        intent_phrases=["Kunden", "Kundenstamm", "Kundenliste", "Gehe zu Kunden"],
    ),
    ActionOut(
        id="nav-orders",
        label="Aufträge",
        shortcut="G A",
        description="Auftragsliste öffnen",
        category="navigation",
        domain="sales",
        intent_phrases=["Aufträge", "Auftragsliste", "Gehe zu Aufträge", "Aufträge öffnen"],
    ),
    ActionOut(
        id="nav-invoices",
        label="Rechnungen",
        shortcut="G R",
        description="Rechnungsliste öffnen",
        category="navigation",
        domain="sales",
        intent_phrases=["Rechnungen", "Rechnungsliste", "Gehe zu Rechnungen"],
    ),
    ActionOut(
        id="nav-inventory",
        label="Lagerbestand",
        shortcut="G L",
        description="Bestandsübersicht öffnen",
        category="navigation",
        domain="inventory",
        intent_phrases=["Lager", "Lagerbestand", "Bestand", "Gehe zu Lager"],
    ),
    ActionOut(
        id="nav-fibu",
        label="Finanzbuchhaltung",
        description="FiBu / Buchhaltung öffnen",
        category="navigation",
        domain="finance",
        intent_phrases=["Buchhaltung", "Fibu", "Finanzbuchhaltung", "Hauptbuch"],
    ),
    ActionOut(
        id="action-new-order",
        label="Neuer Auftrag",
        shortcut="N A",
        description="Auftrag erstellen",
        category="action",
        domain="sales",
        intent_phrases=["Neuer Auftrag", "Auftrag anlegen", "Auftrag erstellen"],
    ),
    ActionOut(
        id="action-new-invoice",
        label="Neue Rechnung",
        description="Rechnung erstellen",
        category="action",
        domain="finance",
        intent_phrases=["Neue Rechnung", "Rechnung anlegen", "Rechnung erstellen"],
    ),
    ActionOut(
        id="action-new-customer",
        label="Neuer Kunde",
        shortcut="N K",
        description="Kunde anlegen",
        category="action",
        domain="crm",
        intent_phrases=["Neuer Kunde", "Kunde anlegen", "Kunde erstellen"],
    ),
]

_action_by_id: Dict[str, ActionOut] = {a.id: a for a in ACTIONS}


class ActionRegistry:
    """Read-only action registry."""

    def get(self, action_id: str) -> Optional[ActionOut]:
        return _action_by_id.get(action_id)

    def list_actions(
        self,
        domain: Optional[str] = None,
        mask: Optional[str] = None,
    ) -> List[ActionOut]:
        result = list(ACTIONS)
        if domain:
            result = [a for a in result if a.domain is None or a.domain == domain]
        if mask:
            result = [a for a in result if a.mask is None or a.mask == mask]
        return result

    def all_ids(self) -> List[str]:
        return list(_action_by_id.keys())

    def intent_phrases_for_action(self, action_id: str) -> List[str]:
        a = _action_by_id.get(action_id)
        return list(a.intent_phrases) if a else []


action_registry = ActionRegistry()
