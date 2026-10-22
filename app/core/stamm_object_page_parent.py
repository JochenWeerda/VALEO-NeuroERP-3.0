"""StammObjectPageParent — gemeinsame Shell fuer Stamm-ObjectPages (UIX-P1).

Taxonomie: ``docs/architecture/uix/maskenfamilien-taxonomie.md`` §2.2.
Children ueberschreiben Fachfelder, Tabs und Endpoints; Layout/Meridian und
Bearbeiten-Aktion kommen aus dem Parent. Create bleibt Legacy bis Paritaet (UIX-057).
"""
from __future__ import annotations

from typing import Any


def stamm_kopf_tab(fields: list[dict[str, Any]], *, label: str = "Stammdaten") -> dict[str, Any]:
    """Immer-sichtbarer Kopf-Tab mit Entity-Feldern."""
    return {
        "key": "kopf",
        "label": label,
        "lazy": False,
        "keepAlive": True,
        "dataSourceKey": "entity",
        "fields": fields,
    }


def stamm_entity_tab(
    *,
    key: str,
    label: str,
    fields: list[dict[str, Any]],
    lazy: bool = False,
    keep_alive: bool = True,
) -> dict[str, Any]:
    """Zusaetzlicher Entity-Feld-Abschnitt (z. B. Preise, Lager, Zuordnung)."""
    return {
        "key": key,
        "label": label,
        "lazy": lazy,
        "keepAlive": keep_alive,
        "dataSourceKey": "entity",
        "fields": fields,
    }


def stamm_lazy_table_tab(
    *,
    key: str,
    label: str,
    columns: list[dict[str, Any]],
    page_size: int = 25,
    table_label: str | None = None,
    server_pagination: bool = True,
    row_route_template: str | None = None,
    data_source_key: str | None = None,
) -> dict[str, Any]:
    """Lazy Tab mit einer virtualisierten Tabelle (gleiche dataSourceKey wie Tab-Key)."""
    table: dict[str, Any] = {
        "key": key,
        "label": table_label or label,
        "dataSourceKey": data_source_key or key,
        "serverPagination": server_pagination,
        "pageSize": page_size,
        "virtualized": True,
        "rowHeight": 52,
        "columns": columns,
    }
    if row_route_template:
        table["rowRouteTemplate"] = row_route_template
    return {
        "key": key,
        "label": label,
        "lazy": True,
        "keepAlive": False,
        "tables": [table],
    }


def stamm_entity_source(endpoint: str) -> dict[str, Any]:
    return {"key": "entity", "endpoint": endpoint}


def stamm_tab_source(key: str, endpoint: str, *, page_size: int = 25) -> dict[str, Any]:
    return {"key": key, "endpoint": endpoint, "pageSize": page_size}


def build_stamm_object_page(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    identity_field: str | None,
    data_sources: list[dict[str, Any]],
    tabs: list[dict[str, Any]],
    edit_permission: str,
    no_workflow_reason: str | None = None,
    workflow: dict[str, Any] | None = None,
    business_purpose: str,
    example_prompts: list[str],
    test_id: str,
    sensitive_fields: list[str] | None = None,
    summary: list[dict[str, Any]] | None = None,
    summary_endpoint: str | None = None,
    extra_actions: list[dict[str, Any]] | None = None,
    edit_action_key: str = "edit",
    edit_action_zone: str | None = None,
    edit_action_overrides: dict[str, Any] | None = None,
    creation: dict[str, Any] | None = None,
    interaction: dict[str, Any] | None = None,
    density: str = "compact",
    context_rail: str = "combined",
    table_profile: str | None = None,
    payload_budget_kb: int = 36,
    requires_virtual_tables: bool = False,
    bundle_group: str | None = None,
) -> dict[str, Any]:
    """Parent-Vertrag: objectPage + anchors + sticky Header; Child liefert Tabs/Quellen."""
    if not tabs or tabs[0].get("key") != "kopf":
        raise ValueError(f"{screen_id}: StammObjectPageParent erwartet tabs[0].key == 'kopf'")
    if not any(ds.get("key") == "entity" for ds in data_sources):
        raise ValueError(f"{screen_id}: StammObjectPageParent erwartet dataSource 'entity'")
    if not no_workflow_reason and not workflow:
        raise ValueError(f"{screen_id}: StammObjectPageParent erwartet no_workflow_reason oder workflow")

    edit_action: dict[str, Any] = {
        "key": edit_action_key,
        "label": "Bearbeiten",
        "kind": "primary",
        "dangerLevel": "safe",
        "permission": edit_permission,
    }
    if edit_action_zone:
        edit_action["zone"] = edit_action_zone
    if edit_action_overrides:
        edit_action.update(edit_action_overrides)

    actions: list[dict[str, Any]] = [edit_action]
    if extra_actions:
        actions.extend(extra_actions)

    layout: dict[str, Any] = {
        "preferredMode": "desktopDense",
        "mobileMode": "mobileStack",
        "touchTargetPx": 44,
        "floorplan": "objectPage",
        "columnNavigation": "single",
        "sectionNavigation": "anchors",
        "density": density,
        "contextRail": context_rail,
        "summaryPlacement": "header",
        "stickyHeader": True,
        "stickyFooter": True,
    }
    if table_profile:
        layout["tableProfile"] = table_profile

    definition: dict[str, Any] = {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "detail",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "dataSources": data_sources,
        "tabs": tabs,
        "actions": actions,
        "agentContract": {
            "businessPurpose": business_purpose,
            "examplePrompts": example_prompts,
            "sensitiveFields": list(sensitive_fields or []),
            "testSelectors": {
                "screenRoot": f"[data-testid='{test_id}']",
                "primaryAction": f"[data-testid='action-{edit_action_key}']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
        "layout": layout,
        "performance": {
            "initialPayloadBudgetKb": payload_budget_kb,
            "requiresLazyTabs": True,
            "requiresVirtualTables": requires_virtual_tables,
            "lookupMinChars": 2,
            "bundleGroup": bundle_group or domain,
        },
    }
    if identity_field is not None:
        definition["identityField"] = identity_field
    if creation is not None:
        definition["creation"] = creation
    if workflow is not None:
        definition["workflow"] = workflow
    if no_workflow_reason is not None:
        definition["noWorkflowReason"] = no_workflow_reason
    if interaction is not None:
        definition["interaction"] = interaction
    if summary is not None:
        definition["summary"] = summary
    else:
        summary_key = identity_field or "id"
        definition["summary"] = [
            {"key": summary_key, "label": "Kennung", "value": None, "kind": "identity"},
        ]
    if summary_endpoint:
        definition["summaryEndpoint"] = summary_endpoint
    return definition
