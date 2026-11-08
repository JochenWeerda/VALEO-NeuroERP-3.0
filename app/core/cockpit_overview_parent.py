"""CockpitOverviewParent — gemeinsame Shell fuer Dashboard-/Cockpit-/Analytics-Masken (UIX-061).

Taxonomie: overviewPage / floorplan ``cockpit`` — KPI-Summary, Kacheln, Kalender,
Twin-Panel oder optionale Tabellen; kein Entity-Stammdaten-Lebenszyklus.
"""
from __future__ import annotations

from typing import Any

COCKPIT_OVERVIEW_LAYOUT_KEYS = {
    "floorplan": "cockpit",
    "density": "expertDense",
}

DEFAULT_NO_WORKFLOW = (
    "Cockpit ist ein Read-Model- oder Navigations-Workspace ohne eigenen Objekt-Lebenszyklus; "
    "Statuswechsel erfolgen in den verlinkten Prozessmasken."
)

DEFAULT_NO_PROCESS_CHAIN = (
    "Aggregations-Cockpit ohne ERP-Belegkette; KPIs und Spruenge sind orientierend."
)


def cockpit_refresh_action(*, permission: str, label: str = "Aktualisieren") -> dict[str, Any]:
    return {
        "key": "refresh",
        "label": label,
        "kind": "secondary",
        "zone": "header",
        "dangerLevel": "safe",
        "permission": permission,
        "localEffect": "refetch",
    }


def cockpit_nav_tile(
    key: str,
    label: str,
    *,
    target_route: str | None = None,
    target_screen_id: str | None = None,
    tone: str = "neutral",
) -> dict[str, Any]:
    tile: dict[str, Any] = {"key": key, "label": label, "tone": tone}
    if target_screen_id:
        tile["targetScreenId"] = target_screen_id
    if target_route:
        tile["targetRoute"] = target_route
    return tile


def cockpit_entity_source(endpoint: str, *, stale_time_ms: int = 15_000) -> dict[str, Any]:
    return {"key": "entity", "endpoint": endpoint, "staleTimeMs": stale_time_ms}


def cockpit_list_source(
    key: str,
    endpoint: str,
    *,
    page_size: int = 50,
    stale_time_ms: int = 10_000,
) -> dict[str, Any]:
    return {"key": key, "endpoint": endpoint, "pageSize": page_size, "staleTimeMs": stale_time_ms}


def cockpit_summary_table(
    *,
    table_key: str,
    label: str,
    columns: list[dict[str, Any]],
    data_source_key: str | None = None,
    page_size: int = 50,
) -> dict[str, Any]:
    return {
        "key": table_key,
        "label": label,
        "dataSourceKey": data_source_key or table_key,
        "serverPagination": True,
        "pageSize": page_size,
        "virtualized": True,
        "rowHeight": 44,
        "columns": columns,
    }


def _validate_cockpit_overview_contract(screen_id: str, definition: dict[str, Any]) -> None:
    layout = definition.get("layout") or {}
    if layout.get("floorplan") != "cockpit":
        raise ValueError(f"{screen_id}: CockpitOverviewParent erwartet layout.floorplan=cockpit")
    for key in ("density", "contextRail"):
        if not layout.get(key):
            raise ValueError(f"{screen_id}: CockpitOverviewParent erwartet layout.{key}")
    has_content = bool(definition.get("tiles")) or bool(definition.get("tables")) or bool(
        definition.get("calendar")
    ) or bool(definition.get("twin"))
    if not has_content:
        raise ValueError(f"{screen_id}: CockpitOverviewParent erwartet tiles, tables, calendar oder twin")
    if not definition.get("noWorkflowReason") and not (definition.get("workflow") or {}).get("processKey"):
        raise ValueError(f"{screen_id}: CockpitOverviewParent erwartet noWorkflowReason oder workflow.processKey")


def build_cockpit_overview_screen(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    business_purpose: str,
    example_prompts: list[str],
    test_id: str | None = None,
    summary: list[dict[str, Any]] | None = None,
    tiles: list[dict[str, Any]] | None = None,
    tables: list[dict[str, Any]] | None = None,
    data_sources: list[dict[str, Any]] | None = None,
    actions: list[dict[str, Any]] | None = None,
    calendar: dict[str, Any] | None = None,
    twin: dict[str, Any] | None = None,
    workflow: dict[str, Any] | None = None,
    no_workflow_reason: str | None = DEFAULT_NO_WORKFLOW,
    no_process_chain_reason: str | None = DEFAULT_NO_PROCESS_CHAIN,
    context_rail: str = "combined",
    table_profile: str | None = None,
    bundle_group: str | None = None,
    payload_budget_kb: int = 32,
    sensitive_fields: list[str] | None = None,
    forbidden_agent_tasks: list[str] | None = None,
    requires_lazy_tabs: bool = False,
    requires_virtual_tables: bool = False,
) -> dict[str, Any]:
    """Parent-Vertrag: mode=cockpit + overviewPage; Child liefert KPIs, Kacheln oder Tabellen."""
    slug = test_id or screen_id.replace("/", "-")
    layout: dict[str, Any] = {
        **COCKPIT_OVERVIEW_LAYOUT_KEYS,
        "contextRail": context_rail,
        "preferredMode": "desktopDense",
        "mobileMode": "mobileStack",
        "touchTargetPx": 44,
    }
    if table_profile:
        layout["tableProfile"] = table_profile
    elif tables:
        if domain in ("finance", "fibu", "pos") or screen_id.startswith(("finance/", "fibu/", "pos/")):
            layout["tableProfile"] = "financial"
        elif (
            domain in ("lager", "inventory", "workflow")
            or screen_id.startswith(("lager/", "inventory"))
            or screen_id.startswith("workflow/flow-spine-inventory")
        ):
            layout["tableProfile"] = "inventory"
        else:
            layout["tableProfile"] = "standard"

    definition: dict[str, Any] = {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "cockpit",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": layout,
        "performance": {
            "initialPayloadBudgetKb": payload_budget_kb,
            "requiresLazyTabs": requires_lazy_tabs,
            "requiresVirtualTables": requires_virtual_tables or bool(tables),
            "lookupMinChars": 2,
            "bundleGroup": bundle_group or domain,
        },
        "agentContract": {
            "businessPurpose": business_purpose,
            "examplePrompts": example_prompts,
            "sensitiveFields": list(sensitive_fields or []),
            "forbiddenAgentTasks": list(forbidden_agent_tasks or []),
            "testSelectors": {"screenRoot": f"[data-testid='{slug}']"},
        },
    }
    if summary is not None:
        definition["summary"] = summary
    if tiles:
        definition["tiles"] = tiles
    if tables:
        if data_sources and len(data_sources) == 1:
            sole_key = data_sources[0].get("key")
            if isinstance(sole_key, str):
                for table in tables:
                    if isinstance(table, dict) and table.get("dataSourceKey") == table.get("key"):
                        table["dataSourceKey"] = sole_key
        definition["tables"] = tables
    if data_sources:
        definition["dataSources"] = data_sources
    if actions:
        definition["actions"] = actions
    if calendar is not None:
        definition["calendar"] = calendar
    if twin is not None:
        definition["twin"] = twin
    if no_workflow_reason is not None:
        definition["noWorkflowReason"] = no_workflow_reason
    if workflow is not None:
        definition["workflow"] = workflow
    if no_process_chain_reason:
        definition["noProcessChainReason"] = no_process_chain_reason

    _validate_cockpit_overview_contract(screen_id, definition)
    return definition
