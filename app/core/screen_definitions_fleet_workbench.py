"""Fuhrpark-Fachoberflaechen (Fahrzeug-Vertiefung) im Universal-Runtime."""
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
        "surfaceOnly": True,
    }
    if fields:
        action["inputFields"] = fields
    return action


def build_fuhrpark_fahrzeug_vertiefung() -> dict[str, Any]:
    """Fahrzeug-Vertiefung — Status, Schaeden, Bussgelder, Wartung, Leasing-Rueckgabe."""
    base = "/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}"
    perm = "logistik.fuhrpark.write"
    return {
        "schemaVersion": 1,
        "id": "fuhrpark/fahrzeug-vertiefung",
        "domain": "logistik",
        "mode": "cockpit",
        "title": "Fahrzeug-Vertiefung",
        "subtitle": "Statushistorie · Schaeden · Bussgelder · Wartung · Leasing-Rueckgabe",
        "adapter": {"type": "native", "sourceId": "fuhrpark/fahrzeug-vertiefung", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "fleet",
        },
        "dataSources": [
            {"key": "historie", "endpoint": f"{base}/status-historie", "pageSize": 50, "staleTimeMs": 10_000},
            {"key": "schaeden", "endpoint": f"{base}/schaeden", "pageSize": 50, "staleTimeMs": 10_000},
            {"key": "bussgeld", "endpoint": f"{base}/bussgeld", "pageSize": 50, "staleTimeMs": 10_000},
            {"key": "wartung", "endpoint": f"{base}/wartung-vorhersage", "pageSize": 1, "staleTimeMs": 30_000},
        ],
        "fields": [
            {"key": "fahrzeug_id", "label": "Fahrzeug-ID", "type": "text", "required": True},
            {"key": "status", "label": "Status", "type": "text", "readOnly": True},
            {"key": "schaden_offen", "label": "Offene Schaeden", "type": "number", "readOnly": True},
            {"key": "bussgeld_offen", "label": "Offene Bussgelder", "type": "number", "readOnly": True},
        ],
        "actions": [
            _cmd(
                "status_wechseln",
                "Status wechseln",
                endpoint=f"{base}/status",
                permission=perm,
                primary=True,
                fields=[
                    {"key": "zu_status", "label": "Neuer Status", "type": "text", "required": True},
                    {"key": "grund", "label": "Grund", "type": "text", "required": False},
                    {"key": "km_stand", "label": "Km-Stand", "type": "number", "required": False},
                ],
            ),
            _cmd(
                "schaden_anlegen",
                "Schaden anlegen",
                endpoint=f"{base}/schaeden",
                permission=perm,
                fields=[
                    {"key": "datum", "label": "Datum", "type": "text", "required": True},
                    {"key": "ort", "label": "Ort", "type": "text", "required": True},
                    {"key": "beschreibung", "label": "Beschreibung", "type": "text", "required": True},
                    {"key": "schadenhoehe_eur", "label": "Hoehe EUR", "type": "number", "required": False},
                    {"key": "versicherung_gemeldet", "label": "Versicherung gemeldet", "type": "boolean", "required": False},
                ],
            ),
            _cmd(
                "schaden_abschliessen",
                "Schaden abschliessen",
                endpoint=f"{base}/schaeden/{{schaden_id}}",
                method="PATCH",
                permission=perm,
                fields=[
                    {"key": "schaden_id", "label": "Schaden-ID", "type": "text", "required": True},
                    {"key": "status", "label": "Status", "type": "text", "required": True, "defaultValue": "abgeschlossen"},
                ],
            ),
            _cmd(
                "bussgeld_anlegen",
                "Bussgeld anlegen",
                endpoint=f"{base}/bussgeld",
                permission=perm,
                fields=[
                    {"key": "datum", "label": "Datum", "type": "text", "required": True},
                    {"key": "tatbestand", "label": "Tatbestand", "type": "text", "required": True},
                    {"key": "betrag_eur", "label": "Betrag EUR", "type": "number", "required": True},
                    {"key": "ort", "label": "Ort", "type": "text", "required": False},
                    {"key": "faellig_am", "label": "Faellig am", "type": "text", "required": False},
                ],
            ),
            _cmd(
                "bussgeld_bezahlt",
                "Bussgeld bezahlt",
                endpoint=f"{base}/bussgeld/{{bg_id}}",
                method="PATCH",
                permission=perm,
                fields=[
                    {"key": "bg_id", "label": "Bussgeld-ID", "type": "text", "required": True},
                    {"key": "status", "label": "Status", "type": "text", "required": True, "defaultValue": "bezahlt"},
                    {"key": "bezahlt_am", "label": "Bezahlt am", "type": "text", "required": False},
                ],
            ),
            _cmd(
                "leasing_rueckgabe",
                "Leasing-Rueckgabe",
                endpoint=f"{base}/leasing-rueckgabe",
                permission=perm,
                fields=[
                    {"key": "rueckgabedatum", "label": "Rueckgabedatum", "type": "text", "required": True},
                    {"key": "km_stand_bei_rueckgabe", "label": "Km-Stand", "type": "number", "required": True},
                    {"key": "zustand_bemerkung", "label": "Zustand", "type": "text", "required": False},
                ],
            ),
        ],
        "specialized": {"type": "fleet_workbench", "id": "fuhrpark/fahrzeug-vertiefung"},
        "noWorkflowReason": "Fuhrpark-Arbeitsplatz; Mutationen laufen ueber Fahrzeug-Commands.",
        "noProcessChainReason": "Fahrzeug-Vertiefung ohne eigene Belegkette in dieser Maske.",
        "performance": {
            "initialPayloadBudgetKb": 160,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "fleet",
        },
        "agentContract": {
            "businessPurpose": "Fahrzeugstatus, Schaeden, Bussgelder und Leasing-Rueckgabe pflegen.",
            "examplePrompts": ["Wechsle den Fahrzeugstatus.", "Melde ein Bussgeld als bezahlt."],
            "sensitiveFields": [],
            "forbiddenAgentTasks": ["Leasing-Rueckgabe ohne menschliche Bestaetigung"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-fuhrpark-fahrzeug-vertiefung']"},
        },
    }


FLEET_WORKBENCH_BUILDERS = {
    "fuhrpark/fahrzeug-vertiefung": build_fuhrpark_fahrzeug_vertiefung,
}
