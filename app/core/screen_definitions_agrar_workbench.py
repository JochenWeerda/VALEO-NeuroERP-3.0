"""Agrar-Fachoberflaechen (Schlagkartei, Milchvieh-Karte) im Universal-Runtime."""
from __future__ import annotations

from typing import Any


def _cmd(
    key: str,
    label: str,
    *,
    endpoint: str,
    method: str = "POST",
    permission: str,
    fields: list[dict[str, Any]] | None = None,
    primary: bool = False,
) -> dict[str, Any]:
    action: dict[str, Any] = {
        "key": key,
        "label": label,
        "kind": "primary" if primary else "secondary",
        "zone": "header",
        "dangerLevel": "moderate" if method in ("POST", "PUT", "PATCH", "DELETE") else "safe",
        "permission": permission,
        "commandEndpoint": endpoint,
        "method": method,
        "forbiddenForAgents": True,
    }
    if fields:
        action["inputFields"] = fields
    return action


def build_agrar_kunden_schlagkartei() -> dict[str, Any]:
    """Innendienst-Kundenschlagkartei — PortalKontoGate + Lohndienst/Ankauf (Feldparitaet)."""
    return {
        "schemaVersion": 1,
        "id": "agrar/kunden-schlagkartei",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Kundenschlagkartei",
        "subtitle": "Schlaege und Massnahmen je Kundenkonto; Lohndienst und Ankaufsangebote",
        "adapter": {"type": "native", "sourceId": "agrar/kunden-schlagkartei", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "standard",
        },
        "fields": [
            {"key": "kunden_nr", "label": "Kunden-Nr.", "type": "text", "readOnly": True},
            {"key": "schlag_count", "label": "Schlaege", "type": "number", "readOnly": True},
            {"key": "massnahme_count", "label": "Massnahmen", "type": "number", "readOnly": True},
            {"key": "gesamt_flaeche_ha", "label": "Flaeche ha", "type": "number", "readOnly": True},
        ],
        "actions": [
            _cmd(
                "lohn_spritz",
                "Lohnspritz-Auftrag",
                endpoint="/api/v1/portal/lohndienste",
                permission="agrar.schlagkartei.write",
                primary=True,
                fields=[
                    {"key": "typ", "label": "Typ", "type": "text", "required": True, "defaultValue": "lohn_spritz"},
                    {"key": "schlag_beschreibung", "label": "Schlag", "type": "text", "required": False},
                    {"key": "flaeche_ha", "label": "Flaeche ha", "type": "number", "required": False},
                    {"key": "wunsch_datum", "label": "Wunschdatum", "type": "date", "required": False},
                    {"key": "kultur", "label": "Kultur", "type": "text", "required": False},
                    {"key": "menge_dt", "label": "Menge dt", "type": "number", "required": False},
                    {"key": "anmerkung", "label": "Anmerkung", "type": "textarea", "required": False},
                ],
            ),
            _cmd(
                "mahl_misch",
                "Mahl+Misch-Termin",
                endpoint="/api/v1/portal/lohndienste",
                permission="agrar.schlagkartei.write",
                fields=[
                    {"key": "typ", "label": "Typ", "type": "text", "required": True, "defaultValue": "mahl_misch"},
                    {"key": "schlag_beschreibung", "label": "Schlag", "type": "text", "required": False},
                    {"key": "flaeche_ha", "label": "Flaeche ha", "type": "number", "required": False},
                    {"key": "wunsch_datum", "label": "Wunschdatum", "type": "date", "required": False},
                    {"key": "tierart", "label": "Tierart", "type": "text", "required": False},
                    {"key": "tiere_anzahl", "label": "Tiere", "type": "number", "required": False},
                    {"key": "getreide_art", "label": "Getreide", "type": "text", "required": False},
                    {"key": "menge_dt", "label": "Menge dt", "type": "number", "required": False},
                    {"key": "anmerkung", "label": "Anmerkung", "type": "textarea", "required": False},
                ],
            ),
            _cmd(
                "ankaufsangebot",
                "Ankaufsangebot erstellen",
                endpoint="/api/v1/portal/empfehlungen/generieren/schlagkartei",
                permission="agrar.schlagkartei.write",
                fields=[
                    {"key": "kunden_nr", "label": "Kunden-Nr.", "type": "text", "required": True},
                    {"key": "ernte_jahr", "label": "Erntejahr", "type": "number", "required": True},
                    {"key": "flaeche_ha", "label": "Flaeche ha", "type": "number", "required": False},
                ],
            ),
        ],
        "specialized": {"type": "agrar_workbench", "id": "agrar/kunden-schlagkartei"},
        "noWorkflowReason": "Innendienst-Arbeitsplatz ohne eigenen Beleg-Lebenszyklus; Auftraege laufen ueber Portal-Endpunkte.",
        "noProcessChainReason": "Schlagkartei ist Konto-Arbeitsplatz, keine Belegkette.",
        "performance": {
            "initialPayloadBudgetKb": 120,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
        "agentContract": {
            "businessPurpose": "Kundenschlaege und Massnahmen einsehen; Lohndienst und Ankaufsangebote ausloesen.",
            "examplePrompts": [
                "Lege einen Lohnspritz-Auftrag an.",
                "Erstelle Ankaufsangebote fuer die Schlagkartei.",
            ],
            "sensitiveFields": ["kunden_nr"],
            "forbiddenAgentTasks": ["Portal-Konto ohne menschliche Wahl setzen"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-agrar-kunden-schlagkartei']"},
        },
    }


def build_agrar_milchvieh_karte() -> dict[str, Any]:
    """CRM-Karte Milchvieh — MapLibre-Surface + Cross-Sell-Map-API."""
    return {
        "schemaVersion": 1,
        "id": "agrar/milchvieh-karte",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Milchvieh-Karte",
        "subtitle": "POIs nach Hygiene-Bedarf; Hover zeigt Betriebskennzahlen",
        "adapter": {"type": "native", "sourceId": "agrar/milchvieh-karte", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "standard",
        },
        "dataSources": [
            {
                "key": "entity",
                "endpoint": "/api/v1/agrar/milchvieh-crosssell/map",
                "staleTimeMs": 30_000,
            },
        ],
        "fields": [
            {"key": "feature_count", "label": "Betriebe", "type": "number", "readOnly": True},
        ],
        "actions": [
            {
                "key": "refresh",
                "label": "Aktualisieren",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "safe",
                "permission": "agrar.milchvieh.read",
                "localEffect": "refetch",
            },
        ],
        "specialized": {"type": "agrar_workbench", "id": "agrar/milchvieh-karte"},
        "noWorkflowReason": "Karten-Arbeitsplatz ohne eigenen Objekt-Lebenszyklus.",
        "noProcessChainReason": "Geodaten-Visualisierung ohne Belegkette.",
        "performance": {
            "initialPayloadBudgetKb": 200,
            "requiresLazyTabs": False,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
        "agentContract": {
            "businessPurpose": "Milchvieh-Betriebe geografisch nach Hygiene- und Cross-Sell-Signalen einsehen.",
            "examplePrompts": ["Zeig die Milchvieh-Karte mit Hygiene-Filter."],
            "sensitiveFields": [],
            "forbiddenAgentTasks": [],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-agrar-milchvieh-karte']"},
        },
    }


AGRAR_WORKBENCH_BUILDERS = {
    "agrar/kunden-schlagkartei": build_agrar_kunden_schlagkartei,
    "agrar/milchvieh-karte": build_agrar_milchvieh_karte,
}
