"""Mask ScreenDefinition API — native generator payloads."""

from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ....core.screen_definitions import get_screen_definition
from ....core.tenant import get_tenant_id


router = APIRouter(prefix="/masks", tags=["ui", "masks", "screen-definition"])

_SENSITIVE_PATTERN = re.compile(r"passw|token|secret|iban|bic|konto_nr|credit_card", re.IGNORECASE)


def _normalize_mask_id(mask_id: str) -> str:
    return mask_id.strip("/").replace("__", "/")


def _generate_agent_contract(definition: dict[str, Any]) -> dict[str, Any]:
    """Derives an AgentMaskContract from a raw ScreenDefinition dict."""

    def collect_fields(d: dict[str, Any]) -> list[dict[str, Any]]:
        fields: list[dict[str, Any]] = list(d.get("fields") or [])
        for tab in d.get("tabs") or []:
            fields.extend(tab.get("fields") or [])
        return fields

    all_fields = collect_fields(definition)
    readable_fields = [f["key"] for f in all_fields]
    editable_fields = [f["key"] for f in all_fields if not f.get("readOnly")]
    sensitive_fields = [
        f["key"]
        for f in all_fields
        if _SENSITIVE_PATTERN.search(f.get("key", "")) or _SENSITIVE_PATTERN.search(f.get("label", ""))
    ]

    actions = definition.get("actions") or []
    available_actions = [
        {
            "key": a["key"],
            "label": a.get("label", a["key"]),
            "dangerLevel": a.get("dangerLevel", "safe"),
            "requiresHumanApproval": bool(a.get("humanApprovalRequired")),
            "requiresConfirmation": bool(a.get("requiresConfirmation")),
            "permission": a.get("permission"),
        }
        for a in actions
    ]

    validation_rules = [
        {"fieldKey": f["key"], "rule": "required", "severity": "blocking"}
        for f in all_fields
        if f.get("required")
    ]

    audit_requirements = [
        {"actionKey": a["key"], "requiresReason": True, "requiresEvidence": False}
        for a in actions
        if a.get("auditReasonRequired")
    ]

    explicit = definition.get("agentContract") or {}
    screen_id = definition.get("id", "")

    return {
        "screenId": screen_id,
        "domain": definition.get("domain"),
        "schemaVersion": definition.get("schemaVersion", 1),
        "contractVersion": 1,
        "businessPurpose": explicit.get("businessPurpose", f"{definition.get('title', screen_id)} — {definition.get('domain', '')}"),
        "primaryEntity": explicit.get("primaryEntity", screen_id.split("/")[-1] if "/" in screen_id else screen_id),
        "readableFields": explicit.get("readableFields", readable_fields),
        "editableFields": explicit.get("editableFields", editable_fields),
        "sensitiveFields": explicit.get("sensitiveFields", sensitive_fields),
        "availableActions": explicit.get("availableActions", available_actions),
        "validationRules": explicit.get("validationRules", validation_rules),
        "workflowRules": explicit.get("workflowRules", []),
        "auditRequirements": explicit.get("auditRequirements", audit_requirements),
        "recommendedAgentTasks": explicit.get("recommendedAgentTasks", []),
        "forbiddenAgentTasks": explicit.get("forbiddenAgentTasks", []),
        "testSelectors": explicit.get("testSelectors", {
            "screenRoot": f'[data-testid="screen-{screen_id}"]',
            "submitButton": '[data-testid="form-submit-btn"]',
            "workflowPanel": '[data-testid="workflow-panel"]',
        }),
        "examplePrompts": explicit.get("examplePrompts", []),
    }


@router.get("/{mask_id:path}/screen-definition", response_model=dict[str, Any], summary="Native ScreenDefinition abrufen")
async def get_mask_screen_definition(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert die native ScreenDefinition fuer Generator-faehige Masken."""

    _ = tenant_id
    normalized = _normalize_mask_id(mask_id)
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return definition


@router.get("/{mask_id:path}/agent-contract", response_model=dict[str, Any], summary="AgentMaskContract abrufen")
async def get_agent_mask_contract(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert den maschinenlesbaren AgentMaskContract fuer AI-Agenten.

    Wird deterministisch aus der ScreenDefinition abgeleitet — kein separates Speichern
    noetig. Explizite agentContract-Felder im Screen ueberschreiben die generierten Werte.
    """
    _ = tenant_id
    normalized = _normalize_mask_id(mask_id)
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return _generate_agent_contract(definition)


_TRIVIAL_KEYS = frozenset({"id", "pk", "uuid", "key", "name", "bezeichnung"})
_GENERIC_KEY_PATTERN = re.compile(r"^(col|column|field|item)\d+$", re.IGNORECASE)
_DETAIL_FLOORPLANS = frozenset({"objectPage", "transaction", "cockpit", "wizard"})
_FINANCIAL_SCREEN_PATTERN = re.compile(r"(^finance/|invoice|open-item|journal|payment|debitor|kreditor|bankkonto)", re.IGNORECASE)
_INVENTORY_SCREEN_PATTERN = re.compile(r"(^lager/|stock|inventory|article)", re.IGNORECASE)


def _check_readiness(definition: dict[str, Any]) -> dict[str, Any]:
    """Checks all generator readiness gates (mandatory + advisory) for a ScreenDefinition dict.

    Phases 030+033 — 6 mandatory gates (block generatorReady) + 6 advisory gates (warnings only).
    """

    def collect_tables(d: dict[str, Any]) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = list(d.get("tables") or [])
        for tab in d.get("tabs") or []:
            tables.extend(tab.get("tables") or [])
        return tables

    all_tables = collect_tables(definition)
    server_tables = [t for t in all_tables if t.get("serverPagination")]
    data_source_keys = {ds["key"] for ds in (definition.get("dataSources") or []) if ds.get("key")}
    mandatory: list[dict[str, Any]] = []
    advisory: list[dict[str, Any]] = []

    def m(gate: str, passed: bool, detail: str) -> None:
        mandatory.append({"gate": gate, "severity": "mandatory", "passed": passed, "detail": detail})

    def a(gate: str, passed: bool, detail: str) -> None:
        advisory.append({"gate": gate, "severity": "advisory", "passed": passed, "detail": detail})

    # ── Mandatory ────────────────────────────────────────────────────────────

    # 1. schema_valid
    schema_errors: list[str] = []
    for req in ("id", "domain", "mode", "title"):
        if not definition.get(req):
            schema_errors.append(f"{req} is required")
    if definition.get("schemaVersion") != 1:
        schema_errors.append("schemaVersion must be 1")
    m("schema_valid", len(schema_errors) == 0, "; ".join(schema_errors) or "OK")

    # 2. non_temporary
    is_temporary = bool((definition.get("adapter") or {}).get("temporary"))
    m("non_temporary", not is_temporary, "adapter.temporary=true — screen is not native yet" if is_temporary else "OK")

    # 3. data_sources — when any table exists
    has_ds = bool(definition.get("dataSources"))
    m("data_sources", not all_tables or has_ds, "OK" if not all_tables or has_ds else "tables exist but no dataSources defined")

    # 4. table_data_source_bound — every serverPagination table has matching dataSource
    unbound = [t["key"] for t in server_tables if not t.get("dataSourceKey") or t["dataSourceKey"] not in data_source_keys]
    m("table_data_source_bound",
      not server_tables or not unbound,
      f"tables missing bound dataSource: {', '.join(unbound)}" if unbound else
      ("no serverPagination tables — gate skipped" if not server_tables else "OK"))

    # 5. table_columns_complete — every table has ≥2 non-trivial columns
    def non_trivial(col: dict[str, Any]) -> bool:
        return col.get("key", "").lower() not in _TRIVIAL_KEYS

    thin = [t["key"] for t in all_tables if len([c for c in (t.get("columns") or []) if non_trivial(c)]) < 2]
    m("table_columns_complete",
      not all_tables or not thin,
      f"tables with <2 non-trivial columns: {', '.join(thin)}" if thin else
      ("no tables — gate skipped" if not all_tables else "OK"))

    # 6. actions_classified — every action has dangerLevel + permission (or stubReason)
    actions = definition.get("actions") or []
    unclassified = [a_["key"] for a_ in actions if not a_.get("dangerLevel") or (not a_.get("permission") and not a_.get("stubReason"))]
    m("actions_classified",
      not actions or not unclassified,
      f"actions missing dangerLevel or permission: {', '.join(unclassified)}" if unclassified else
      ("no actions — gate skipped" if not actions else "OK"))

    # Additional mandatory Meridian gates
    # 7. layout_metadata - Meridian floorplan, density and contextRail are mandatory
    layout = definition.get("layout") or {}
    missing_layout = [
        key
        for key in ("floorplan", "density", "contextRail")
        if not layout.get(key)
    ]
    invalid_detail_rail = layout.get("floorplan") in _DETAIL_FLOORPLANS and layout.get("contextRail") == "none"
    m("layout_metadata",
      not missing_layout and not invalid_detail_rail,
      f"layout missing Meridian metadata: {', '.join(missing_layout)}" if missing_layout else
      (f"floorplan={layout.get('floorplan')} requires contextRail other than none" if invalid_detail_rail else "OK"))

    screen_id = definition.get("id", "")
    expected_profile = (
        "financial"
        if definition.get("domain") == "finance" or _FINANCIAL_SCREEN_PATTERN.search(screen_id)
        else "inventory"
        if definition.get("domain") == "inventory" or _INVENTORY_SCREEN_PATTERN.search(screen_id)
        else None
    )
    has_table_profile = not all_tables or bool(layout.get("tableProfile"))
    # Tabellenlose Screens (z.B. cockpit-Workspaces, UIX-061) brauchen kein
    # Tabellen-Profil — die Domain-Erwartung gilt nur fuer echte Tabellen-Screens.
    profile_matches = not all_tables or not expected_profile or layout.get("tableProfile") == expected_profile
    # 8. table_profile - table screens require a Meridian profile
    m("table_profile",
      has_table_profile and profile_matches,
      "tables exist but layout.tableProfile is missing" if not has_table_profile else
      (f"expected layout.tableProfile={expected_profile} for {screen_id}" if not profile_matches else
       ("no tables - gate skipped" if not all_tables else "OK")))

    # Advisory gates

    # 9. sort_whitelist — every table with columns has ≥1 sortable
    no_sort = [t["key"] for t in all_tables if (t.get("columns") or []) and not any(c.get("sortable") for c in (t.get("columns") or []))]
    a("sort_whitelist", not all_tables or not no_sort, f"tables with no sortable column: {', '.join(no_sort)}" if no_sort else ("OK" if all_tables else "no tables"))

    # 10. filter_columns — every table with columns has ≥1 filterable
    no_filt = [t["key"] for t in all_tables if (t.get("columns") or []) and not any(c.get("filterable") for c in (t.get("columns") or []))]
    a("filter_columns", not all_tables or not no_filt, f"tables with no filterable column: {', '.join(no_filt)}" if no_filt else ("OK" if all_tables else "no tables"))

    # 11. agent_contract — explicit businessPurpose preferred
    has_explicit = bool((definition.get("agentContract") or {}).get("businessPurpose"))
    a("agent_contract", has_explicit, "explicit agentContract provided" if has_explicit else "no explicit agentContract — auto-generated only")

    # 12. workflow_declared
    needs_wf = definition.get("mode") in ("detail", "cockpit")
    has_wf = bool((definition.get("workflow") or {}).get("processKey")) or bool(definition.get("noWorkflowReason"))
    a("workflow_declared", not needs_wf or has_wf,
      "OK" if has_wf else (f"mode={definition.get('mode')} — gate skipped" if not needs_wf else "detail/cockpit screen missing workflow or noWorkflowReason"))

    # 13. stable_test_selectors
    has_sel = bool((definition.get("agentContract") or {}).get("testSelectors", {}).get("screenRoot"))
    a("stable_test_selectors", has_sel, "OK" if has_sel else "no explicit testSelectors.screenRoot (auto-generated only)")

    # 14. table_query_contract — sortable/filterable keys must not be generic
    generic_cols = [
        f"{t['key']}.{c['key']}"
        for t in all_tables
        for c in (t.get("columns") or [])
        if (c.get("sortable") or c.get("filterable")) and _GENERIC_KEY_PATTERN.match(c.get("key", ""))
    ]
    a("table_query_contract", not generic_cols, f"generic unstable column keys: {', '.join(generic_cols)}" if generic_cols else "OK")

    # 15. cockpit_content (UIX-061) — cockpit-Workspaces brauchen Inhalt:
    # entweder Kacheln (tiles) oder Tabellen. Advisory, damit leere Cockpits
    # als Warnung auffallen statt still generatorReady zu sein.
    is_cockpit = definition.get("mode") == "cockpit" or layout.get("floorplan") == "cockpit"
    has_cockpit_content = bool(definition.get("tiles")) or bool(definition.get("calendar")) or bool(all_tables)
    a("cockpit_content", not is_cockpit or has_cockpit_content,
      "OK" if not is_cockpit else ("OK" if has_cockpit_content else "cockpit without tiles or tables"))

    # ── Summary ───────────────────────────────────────────────────────────────
    all_gates = mandatory + advisory
    failed_m = [g for g in mandatory if not g["passed"]]
    failed_a = [g for g in advisory if not g["passed"]]
    advisory_score = round((len(advisory) - len(failed_a)) / len(advisory), 2) if advisory else 1.0

    return {
        "screenId": definition.get("id"),
        "generatorReady": len(failed_m) == 0,
        "advisoryScore": advisory_score,
        "gates": all_gates,
        "errors": [f"[{g['gate']}] {g['detail']}" for g in failed_m],
        "warnings": [f"[{g['gate']}] {g['detail']}" for g in failed_a],
    }


@router.get("/{mask_id:path}/readiness", response_model=dict[str, Any], summary="Generator-Readiness pruefen")
async def get_mask_readiness(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Prueft alle Generator-Readiness-Gates fuer eine Maske.

    Mandatory gates (blockieren generatorReady):
    schema_valid, non_temporary, data_sources, table_data_source_bound,
    table_columns_complete, actions_classified.

    Advisory gates (nur Warnungen, kein Block):
    sort_whitelist, filter_columns, agent_contract, workflow_declared,
    stable_test_selectors, table_query_contract.
    """
    _ = tenant_id
    normalized = _normalize_mask_id(mask_id)
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return _check_readiness(definition)


@router.get(
    "/{mask_id:path}/entity/{entity_id}",
    response_model=dict[str, Any],
    summary="Generischer Entity-Stub fuer native SDs ohne dedizierten Backend-Endpunkt",
)
async def get_mask_entity_stub(
    mask_id: str,
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Stub-Endpoint fuer native SDs, deren fachlicher Entity-Endpunkt noch nicht implementiert ist.

    Liefert Platzhalter-Daten damit das Frontend kein 404 erhaelt.
    Wird durch den realen Domain-Endpunkt ersetzt, sobald die API verfuegbar ist.
    """
    _ = tenant_id
    normalized = _normalize_mask_id(mask_id)
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    # Collect all field keys from kopf tab to build a minimal stub payload
    fields: list[dict[str, Any]] = []
    for tab in definition.get("tabs", []):
        if tab.get("key") == "kopf":
            fields = tab.get("fields", [])
            break
    stub: dict[str, Any] = {"id": entity_id, "_stub": True, "_mask_id": normalized}
    for f in fields:
        stub.setdefault(f["key"], None)
    return stub


@router.get(
    "/{mask_id:path}/entity/{entity_id}/tabs/{tab_key}",
    response_model=dict[str, Any],
    summary="Generischer Tab-Stub fuer native SDs ohne dedizierten Tab-Endpunkt",
)
async def get_mask_tab_stub(
    mask_id: str,
    entity_id: str,
    tab_key: str,
    page: int = 1,
    page_size: int = 25,
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Stub-Endpunkt fuer Tabellen-Tabs nativer SDs.

    Liefert leere Ergebnisliste damit das Frontend kein 404 erhaelt.
    Wird durch den realen Domain-Endpunkt ersetzt, sobald die API verfuegbar ist.
    """
    _ = tenant_id
    normalized = _normalize_mask_id(mask_id)
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "_stub": True,
        "_mask_id": normalized,
        "_entity_id": entity_id,
        "_tab_key": tab_key,
    }
