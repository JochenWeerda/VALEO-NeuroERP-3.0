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


def stamm_lazy_table_tab(
    *,
    key: str,
    label: str,
    columns: list[dict[str, Any]],
    page_size: int = 25,
    table_label: str | None = None,
) -> dict[str, Any]:
    """Lazy Tab mit einer virtualisierten Tabelle (gleiche dataSourceKey wie Tab-Key)."""
    return {
        "key": key,
        "label": label,
        "lazy": True,
        "keepAlive": False,
        "tables": [
            {
                "key": key,
                "label": table_label or label,
                "dataSourceKey": key,
                "serverPagination": True,
                "pageSize": page_size,
                "virtualized": True,
                "rowHeight": 52,
                "columns": columns,
            }
        ],
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
    identity_field: str,
    data_sources: list[dict[str, Any]],
    tabs: list[dict[str, Any]],
    edit_permission: str,
    no_workflow_reason: str,
    business_purpose: str,
    example_prompts: list[str],
    test_id: str,
    sensitive_fields: list[str] | None = None,
    summary: list[dict[str, Any]] | None = None,
    summary_endpoint: str | None = None,
    extra_actions: list[dict[str, Any]] | None = None,
    density: str = "compact",
    context_rail: str = "none",
    payload_budget_kb: int = 36,
    requires_virtual_tables: bool = False,
    bundle_group: str | None = None,
) -> dict[str, Any]:
    """Parent-Vertrag: objectPage + anchors + sticky Header; Child liefert Tabs/Quellen."""
    if not tabs or tabs[0].get("key") != "kopf":
        raise ValueError(f"{screen_id}: StammObjectPageParent erwartet tabs[0].key == 'kopf'")
    if not any(ds.get("key") == "entity" for ds in data_sources):
        raise ValueError(f"{screen_id}: StammObjectPageParent erwartet dataSource 'entity'")

    actions: list[dict[str, Any]] = [
        {
            "key": "edit",
            "label": "Bearbeiten",
            "kind": "primary",
            "dangerLevel": "safe",
            "permission": edit_permission,
        },
    ]
    if extra_actions:
        actions.extend(extra_actions)

    definition: dict[str, Any] = {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "detail",
        "title": title,
        "subtitle": subtitle,
        "identityField": identity_field,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "dataSources": data_sources,
        "tabs": tabs,
        "actions": actions,
        "noWorkflowReason": no_workflow_reason,
        "agentContract": {
            "businessPurpose": business_purpose,
            "examplePrompts": example_prompts,
            "sensitiveFields": list(sensitive_fields or []),
            "testSelectors": {
                "screenRoot": f"[data-testid='{test_id}']",
                "primaryAction": "[data-testid='action-edit']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
        "layout": {
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
        },
        "performance": {
            "initialPayloadBudgetKb": payload_budget_kb,
            "requiresLazyTabs": True,
            "requiresVirtualTables": requires_virtual_tables,
            "lookupMinChars": 2,
            "bundleGroup": bundle_group or domain,
        },
    }
    if summary is not None:
        definition["summary"] = summary
    else:
        definition["summary"] = [
            {"key": identity_field, "label": "Kennung", "value": None, "kind": "identity"},
        ]
    if summary_endpoint:
        definition["summaryEndpoint"] = summary_endpoint
    return definition
