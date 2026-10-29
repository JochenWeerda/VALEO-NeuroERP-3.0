"""StammListenParent — gemeinsame Shell fuer Stammdaten-Listen (UIX-P1).

Taxonomie: ``docs/architecture/uix/maskenfamilien-taxonomie.md`` §2.3.
Children liefern Spalten, Endpoint und ``row_route`` zur nativen Detailmaske;
Neuanlage bleibt oft Legacy bis Create-Paritaet (UIX-057).
"""
from __future__ import annotations

import re
from typing import Any

_FINANCIAL_LIST_SCREEN = re.compile(r"(^finance/|^fibu/)")
_INVENTORY_LIST_SCREEN = re.compile(r"^lager/")


def stamm_list_export_action() -> dict[str, Any]:
    """CSV-Export der Liste (NativeListPage, ohne Serverwirkung)."""
    return {
        "key": "export",
        "label": "CSV-Export",
        "kind": "secondary",
        "dangerLevel": "safe",
        "zone": "header",
        "command": "list.exportCsv",
        "localEffect": "download",
        "stubReason": "Exportiert die Liste mit ihren Spalten; keine Serverwirkung.",
    }


def stamm_list_neu_action(label: str, route: str) -> dict[str, Any]:
    """Anlage oeffnen; Rechte prueft der Anlageweg der Zielmaske (oft Legacy)."""
    return {
        "key": "neu",
        "label": label,
        "kind": "primary",
        "dangerLevel": "safe",
        "zone": "header",
        "navigationRoute": route,
        "localEffect": "navigation",
        "stubReason": "Oeffnet die Anlage; Rechte prueft deren Anlageweg.",
    }


def stamm_list_status_visible(*werte: str) -> dict[str, Any]:
    """Sichtbarkeit nach Status; Altdaten fuehren Status teils klein geschrieben."""
    return {"field": "status", "values": [*werte, *(w.lower() for w in werte)]}


def build_stamm_list_screen(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    endpoint: str,
    row_route: str | None,
    columns: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    row_actions: list[dict[str, Any]],
    purpose: str,
    prompts: list[str],
    bundle: str,
    no_workflow: str,
    dangerous: list[dict[str, str]] | None = None,
    fetch_limit: int = 100,
    table_profile: str = "standard",
    table_page_size: int = 50,
    row_height: int = 40,
    server_pagination: bool = False,
) -> dict[str, Any]:
    """Worklist; fetch_limit bounds one source page, never the complete result.

    The shared read collector follows source pagination before client filtering,
    totals and exports. A source page must respect the registered API bounds.
    """
    if table_profile == "standard":
        if domain == "finance" or screen_id.startswith("fibu/"):
            table_profile = "financial"
        elif domain in {"lager", "inventory"} or screen_id.startswith("lager/"):
            table_profile = "inventory"
        elif domain in {"compliance", "qualitaet"}:
            table_profile = "audit"
    if not columns:
        raise ValueError(f"{screen_id}: StammListenParent erwartet mindestens eine Spalte")
    if not no_workflow.strip():
        raise ValueError(f"{screen_id}: StammListenParent erwartet no_workflow")
    if row_route is not None and "{" not in row_route:
        raise ValueError(f"{screen_id}: row_route braucht einen Platzhalter (z. B. {{id}})")

    if table_profile == "standard":
        if domain == "finance" or _FINANCIAL_LIST_SCREEN.search(screen_id):
            table_profile = "financial"
        elif domain in ("inventory", "lager") or _INVENTORY_LIST_SCREEN.search(screen_id):
            table_profile = "inventory"

    agent: dict[str, Any] = {
        "businessPurpose": purpose,
        "examplePrompts": prompts,
        "sensitiveFields": [],
        "testSelectors": {"screenRoot": f"[data-testid='screen-{screen_id}']"},
    }
    if dangerous:
        agent["dangerousActions"] = dangerous

    table: dict[str, Any] = {
        "key": "list",
        "label": title,
        "dataSourceKey": "list",
        "serverPagination": server_pagination,
        "pageSize": table_page_size,
        "virtualized": True,
        "rowHeight": row_height,
        "columns": columns,
        "rowActions": row_actions,
    }
    if row_route:
        table["rowRouteTemplate"] = row_route

    layout: dict[str, Any] = {
        "floorplan": "worklist",
        "density": "compact",
        "contextRail": "none",
        "preferredMode": "desktopDense",
        "mobileMode": "mobileStack",
        "touchTargetPx": 44,
        "tableProfile": table_profile,
    }

    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "list",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "dataSources": [{"key": "list", "endpoint": endpoint, "pageSize": fetch_limit}],
        "actions": actions,
        "tables": [table],
        "noWorkflowReason": no_workflow,
        "agentContract": agent,
        "layout": layout,
        "performance": {
            "initialPayloadBudgetKb": 60,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": bundle,
        },
    }
