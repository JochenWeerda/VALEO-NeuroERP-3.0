"""Lager-Fachoberflaechen (Materialfluss ReactFlow) im Universal-Runtime."""
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


def build_lager_materialfluss() -> dict[str, Any]:
    """Agrar-Materialfluss — ReactFlow-Surface + WMS-Agri-Commands."""
    agri = "/api/v1/lager/wms/agri"
    perm = "lager.materialfluss.write"
    return {
        "schemaVersion": 1,
        "id": "lager/materialfluss",
        "domain": "lager",
        "mode": "cockpit",
        "title": "Agrar-Materialfluss",
        "subtitle": "Silo-Zellen, Flow-Knoten/Kanten, Transfer und Lot-Link (WM-AGRI-SILO-001)",
        "adapter": {"type": "native", "sourceId": "lager/materialfluss", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "inventory",
        },
        "dataSources": [
            {"key": "nodes", "endpoint": f"{agri}/material-flow/nodes", "pageSize": 200, "staleTimeMs": 10_000},
            {"key": "edges", "endpoint": f"{agri}/material-flow/edges", "pageSize": 200, "staleTimeMs": 10_000},
            {"key": "silo_cells", "endpoint": f"{agri}/silo-cells", "pageSize": 200, "staleTimeMs": 10_000},
        ],
        "fields": [
            {"key": "warehouse_id", "label": "Lager", "type": "text", "readOnly": True},
            {"key": "node_count", "label": "Knoten", "type": "number", "readOnly": True},
            {"key": "edge_count", "label": "Kanten", "type": "number", "readOnly": True},
        ],
        "actions": [
            _cmd(
                "node_anlegen",
                "Knoten anlegen",
                endpoint=f"{agri}/material-flow/nodes",
                permission=perm,
                primary=True,
                fields=[
                    {"key": "code", "label": "Code", "type": "text", "required": True},
                    {"key": "node_type", "label": "Typ", "type": "text", "required": True},
                    {"key": "label", "label": "Bezeichnung", "type": "text", "required": False},
                    {"key": "status", "label": "Status", "type": "text", "required": False, "defaultValue": "active"},
                ],
            ),
            _cmd(
                "edge_anlegen",
                "Kante anlegen",
                endpoint=f"{agri}/material-flow/edges",
                permission=perm,
                fields=[
                    {"key": "from_node_id", "label": "Von-Knoten", "type": "text", "required": True},
                    {"key": "to_node_id", "label": "Nach-Knoten", "type": "text", "required": True},
                    {"key": "status", "label": "Status", "type": "text", "required": False, "defaultValue": "open"},
                ],
            ),
            _cmd(
                "zelle_anlegen",
                "Silo-Zelle anlegen",
                endpoint=f"{agri}/silo-cells",
                permission=perm,
                fields=[
                    {"key": "code", "label": "Code", "type": "text", "required": True},
                    {"key": "capacity_t", "label": "Kapazitaet t", "type": "number", "required": False},
                ],
            ),
            _cmd(
                "route_pruefen",
                "Route pruefen",
                endpoint=f"{agri}/material-flow/validate-route",
                permission=perm,
                fields=[
                    {"key": "from_node_id", "label": "Von", "type": "text", "required": True},
                    {"key": "to_node_id", "label": "Nach", "type": "text", "required": True},
                    {"key": "warehouse_id", "label": "Lager-ID", "type": "text", "required": True},
                ],
            ),
            _cmd(
                "transfer",
                "Material transferieren",
                endpoint=f"{agri}/material-flow/transfer",
                permission=perm,
                fields=[
                    {"key": "from_node_id", "label": "Von", "type": "text", "required": True},
                    {"key": "to_node_id", "label": "Nach", "type": "text", "required": True},
                    {"key": "quantity_kg", "label": "Menge kg", "type": "number", "required": True},
                    {"key": "warehouse_id", "label": "Lager-ID", "type": "text", "required": True},
                ],
            ),
            _cmd(
                "lot_link",
                "Charge verknuepfen",
                endpoint=f"{agri}/material-flow/lot-link",
                permission=perm,
                fields=[
                    {"key": "lot_id", "label": "Charge-ID", "type": "text", "required": True},
                    {"key": "cell_id", "label": "Zellen-ID", "type": "text", "required": True},
                    {"key": "warehouse_id", "label": "Lager-ID", "type": "text", "required": True},
                ],
            ),
        ],
        "specialized": {"type": "lager_workbench", "id": "lager/materialfluss"},
        "noWorkflowReason": "Materialfluss-Arbeitsplatz; Mutationen laufen ueber WMS-Agri-Commands.",
        "noProcessChainReason": "Lagerfluesse ohne eigene Belegkette in dieser Maske.",
        "performance": {
            "initialPayloadBudgetKb": 220,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "lager",
        },
        "agentContract": {
            "businessPurpose": "Agrar-Materialflussknoten und -kanten pflegen sowie Transfers buchen.",
            "examplePrompts": ["Lege einen Flow-Knoten an.", "Transferiere Material zwischen zwei Knoten."],
            "sensitiveFields": [],
            "forbiddenAgentTasks": ["Transfer ohne menschliche Bestaetigung"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-lager-materialfluss']"},
        },
    }


LAGER_WORKBENCH_BUILDERS = {
    "lager/materialfluss": build_lager_materialfluss,
}
