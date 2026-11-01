"""Fixed feed domain surfaces inside ScreenDefinition and the universal runtime."""
from __future__ import annotations

from typing import Any


_FIELDS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "futtermittel/rationseditor": (
        ("ration_id", "Ration", "text"), ("group_id", "Tiergruppe", "text"),
        ("version_no", "Version", "number"), ("status", "Status", "text"),
    ),
    "futtermittel/rationsoptimierung": (
        ("feed_id", "Futtermittel", "text"), ("cow_profile", "Tierprofil", "text"),
        ("optimization_result", "Optimierungsergebnis", "text"), ("review_status", "Prüfstatus", "text"),
    ),
    "portal/rationsoptimierung": (
        ("view", "Arbeitsbereich", "text"), ("ration_id", "Ration", "text"),
        ("group_id", "Tiergruppe", "text"), ("plan_status", "Planstatus", "text"),
    ),
    "futtermittel/fuetterungsdokumentation-mobil": (
        ("plan_version_id", "Planversion", "text"), ("group_id", "Tiergruppe", "text"),
        ("actual_kg", "Istmenge", "number"), ("rest_kg", "Restmenge", "number"),
        ("tm_pct", "Trockenmasse", "number"),
    ),
}


def _surface_action(key: str, label: str, *, primary: bool = False) -> dict[str, Any]:
    return {
        "key": key, "label": label, "kind": "primary" if primary else "secondary",
        "dangerLevel": "safe", "permission": "futtermittel.rations.update",
        "forbiddenForAgents": True, "surfaceOnly": True,
    }


_ACTIONS: dict[str, list[dict[str, Any]]] = {
    "futtermittel/rationseditor": [
        _surface_action("open_ration", "Ration öffnen", primary=True),
        _surface_action("evaluate", "Ration bewerten"),
        _surface_action("save_ration", "Ration speichern"),
    ],
    "futtermittel/rationsoptimierung": [
        _surface_action("optimize", "Ration optimieren", primary=True),
        _surface_action("review", "Ergebnis prüfen"),
        _surface_action("submit", "Ration einreichen"),
    ],
    "portal/rationsoptimierung": [
        _surface_action("open_workspace", "Planungswerkzeug öffnen", primary=True),
    ],
    "futtermittel/fuetterungsdokumentation-mobil": [
        _surface_action("record_actual", "Fütterung erfassen", primary=True),
        _surface_action("replay_pending", "Ausstehende Meldungen senden"),
    ],
}


def build_feed_workbench(screen_id: str) -> dict[str, Any]:
    if screen_id not in _FIELDS:
        raise ValueError("Unbekannter Feed-Arbeitsplatz")
    title = {
        "futtermittel/rationseditor": "Rationseditor",
        "futtermittel/rationsoptimierung": "Rationsoptimierung",
        "portal/rationsoptimierung": "Fütterungsberatung",
        "futtermittel/fuetterungsdokumentation-mobil": "Fütterungsdokumentation mobil",
    }[screen_id]
    return {
        "schemaVersion": 1, "id": screen_id, "domain": "futtermittel", "mode": "cockpit",
        "title": title, "subtitle": "Fütterungsplanung und Nachweis",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "compact", "contextRail": "workflow", "tableProfile": "standard"},
        "fields": [{"key": key, "label": label, "type": kind, "readOnly": key not in {"actual_kg", "rest_kg", "tm_pct"}}
                   for key, label, kind in _FIELDS[screen_id]],
        "actions": _ACTIONS[screen_id],
        "specialized": {"type": "feed_workbench", "id": screen_id},
        "noWorkflowReason": "Fachliche Rations- und Fütterungsabläufe werden im spezialisierten Arbeitsbereich geführt.",
        "noProcessChainReason": "Die Fachabläufe besitzen eigene versionierte Rations- und Fütterungsverträge.",
        "performance": {"initialPayloadBudgetKb": 100, "requiresLazyTabs": True,
                        "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "futtermittel"},
        "agentContract": {"businessPurpose": title, "examplePrompts": [f"Zeige {title}."],
                          "sensitiveFields": [key for key, _, _ in _FIELDS[screen_id]],
                          "forbiddenAgentTasks": ["Fachliche Mutationen ausführen"],
                          "testSelectors": {"screenRoot": f"[data-testid='native-cockpit-{screen_id.replace('/', '-')}']"}},
    }
