"""ScreenDefinition des Pruefkorbs (FIN-CONTROL-002).

Eine Arbeitsliste nach dem Muster der Beleg-Kontrolle: Kennzahlen aus dem Lagebild, darunter die Befunde der
Kontroll-Engine. Die Maske zeigt Bezeichnungen, keine internen Schluessel; bewertet wird ueber den Kommandoweg
``POST /api/v1/kontrolle/befunde/{id}/pruefung``.
"""
from __future__ import annotations

from typing import Any

SCREEN_ID = "finance/pruefkorb"


def build_pruefkorb_screen_definition() -> dict[str, Any]:
    """Native Arbeitsliste des Controllers ueber die Befunde der Kontroll-Engine."""
    nur_offen = {"field": "status", "values": ["offen"]}
    return {
        "schemaVersion": 1,
        "id": SCREEN_ID,
        "domain": "finance",
        "mode": "list",
        "title": "Prüfkorb",
        "subtitle": "Auffälligkeiten an gebuchten Vorgängen: Warnungen und freigegebene kritische Befunde",
        "adapter": {"type": "native", "sourceId": SCREEN_ID, "temporary": False},
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/kontrolle/lagebild", "staleTimeMs": 10_000},
            {"key": "befunde", "endpoint": "/api/v1/kontrolle/pruefkorb", "pageSize": 50, "staleTimeMs": 10_000},
        ],
        "summary": [
            {"key": "offen", "label": "Offen", "tone": "warning"},
            {"key": "kritisch_offen", "label": "Kritisch, noch nicht bewertet", "tone": "danger"},
            {"key": "warnung_offen", "label": "Warnungen", "tone": "warning"},
            {"key": "wartend", "label": "Älter als 7 Tage", "tone": "danger"},
            {"key": "geprueft_30_tage", "label": "Geprüft in 30 Tagen", "tone": "info"},
            {"key": "lage", "label": "Lage", "tone": "info"},
        ],
        "tables": [{
            "key": "befunde",
            "label": "Befunde",
            "dataSourceKey": "befunde",
            "serverPagination": True,
            "pageSize": 50,
            "virtualized": True,
            "rowHeight": 44,
            "columns": [
                {"key": "erfasst", "label": "Erfasst", "renderKind": "datetime", "sortable": True, "width": 150},
                {"key": "schwere", "label": "Schwere", "renderKind": "status", "sortable": True, "filterable": True, "width": 110},
                {"key": "art", "label": "Art", "sortable": True, "filterable": True, "width": 220},
                {"key": "vorgang", "label": "Vorgang", "width": 170},
                {"key": "aktion", "label": "Aktion", "width": 100},
                {"key": "beleg", "label": "Beleg", "width": 140},
                {"key": "betrag", "label": "Betrag", "renderKind": "currency", "sortable": True, "width": 120},
                {"key": "hinweis", "label": "Hinweis", "width": 320},
                {"key": "ausgeloest_von", "label": "Ausgelöst von", "sortable": True, "filterable": True, "width": 140},
                {"key": "status", "label": "Stand", "renderKind": "status", "sortable": True, "filterable": True, "width": 110},
                {"key": "geprueft_von", "label": "Geprüft von", "width": 140},
                {"key": "bewertung", "label": "Bewertung", "width": 260},
            ],
            "rowRouteTemplate": "{source_route}",
            "rowActions": [
                {"key": "pruefen", "label": "Bewerten", "visibleWhen": nur_offen, "commandEndpoint": "/api/v1/kontrolle/befunde/{entity_id}/actions/pruefen", "method": "POST", "humanApprovalRequired": True},
                {"key": "open_source", "label": "Zum Beleg", "localEffect": "navigation"},
            ],
        }],
        "noWorkflowReason": "Ein Befund hat nur zwei Stände (offen, geprüft); die Bewertung wird am Befund festgehalten.",
        "layout": {"floorplan": "worklist", "density": "expertDense", "contextRail": "audit", "tableProfile": "financial"},
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "finance",
        },
        "agentContract": {
            "businessPurpose": "Auffälligkeiten an Buchungen, Stornos und Importen für den Controller priorisieren.",
            "examplePrompts": [
                "Welche Befunde sind im Prüfkorb offen?",
                "Zeige die kritischen Befunde.",
                "Welche Auffälligkeiten warten seit mehr als einer Woche?",
            ],
            "sensitiveFields": ["ausgeloest_von", "geprueft_von", "bewertung", "betrag"],
            "forbiddenAgentTasks": ["Befunde bewerten oder als geprüft kennzeichnen"],
            "testSelectors": {"screenRoot": "[data-testid='finanz-pruefkorb']"},
        },
    }


KONTROLLE_SCREEN_BUILDERS = {SCREEN_ID: build_pruefkorb_screen_definition}
KONTROLLE_SYNONYME = {
    SCREEN_ID: ["prüfkorb", "pruefkorb", "kontrollbefunde", "auffälligkeiten", "controller", "dubletten",
                "unregelmäßigkeiten"],
}
KONTROLLE_ROUTEN = {SCREEN_ID: "/finance/pruefkorb"}
