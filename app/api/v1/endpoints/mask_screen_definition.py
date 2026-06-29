"""Mask ScreenDefinition API — native generator payloads."""

from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ....core.screen_definitions import get_screen_definition
from ....core.tenant import get_tenant_id


router = APIRouter(prefix="/masks", tags=["ui", "masks", "screen-definition"])

_SENSITIVE_PATTERN = re.compile(r"passw|token|secret|iban|bic|konto_nr|credit_card", re.IGNORECASE)


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


@router.get("/{mask_id}/screen-definition", response_model=dict[str, Any], summary="Native ScreenDefinition abrufen")
async def get_mask_screen_definition(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert die native ScreenDefinition fuer Generator-faehige Masken."""

    _ = tenant_id
    normalized = mask_id.strip("/")
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return definition


@router.get("/{mask_id}/agent-contract", response_model=dict[str, Any], summary="AgentMaskContract abrufen")
async def get_agent_mask_contract(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert den maschinenlesbaren AgentMaskContract fuer AI-Agenten.

    Wird deterministisch aus der ScreenDefinition abgeleitet — kein separates Speichern
    noetig. Explizite agentContract-Felder im Screen ueberschreiben die generierten Werte.
    """
    _ = tenant_id
    normalized = mask_id.strip("/")
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return _generate_agent_contract(definition)


def _check_readiness(definition: dict[str, Any]) -> dict[str, Any]:
    """Checks all generator readiness gates for a ScreenDefinition dict."""

    def collect_tables(d: dict[str, Any]) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = list(d.get("tables") or [])
        for tab in d.get("tabs") or []:
            tables.extend(tab.get("tables") or [])
        return tables

    all_tables = collect_tables(definition)
    gates = []

    # Gate 1: schema validation
    schema_errors: list[str] = []
    for req_field in ("id", "domain", "mode", "title"):
        if not definition.get(req_field):
            schema_errors.append(f"{req_field} is required")
    if definition.get("schemaVersion") != 1:
        schema_errors.append("schemaVersion must be 1")
    gates.append({"gate": "schema_valid", "passed": len(schema_errors) == 0, "detail": "; ".join(schema_errors) or "OK"})

    # Gate 2: sort whitelist
    has_sortable = any(col.get("sortable") for t in all_tables for col in (t.get("columns") or []))
    gates.append({
        "gate": "sort_whitelist",
        "passed": has_sortable or not all_tables,
        "detail": "OK" if has_sortable or not all_tables else "no sortable columns defined in any table",
    })

    # Gate 3: filterable columns
    has_filterable = any(col.get("filterable") for t in all_tables for col in (t.get("columns") or []))
    gates.append({
        "gate": "filter_columns",
        "passed": has_filterable or not all_tables,
        "detail": "OK" if has_filterable or not all_tables else "no filterable columns defined in any table",
    })

    # Gate 4: agentContract — always derivable
    has_explicit = bool((definition.get("agentContract") or {}).get("businessPurpose"))
    gates.append({"gate": "agent_contract", "passed": True, "detail": "explicit agentContract provided" if has_explicit else "auto-generated"})

    # Gate 5: dataSources when tables exist
    has_data_sources = bool(definition.get("dataSources"))
    gates.append({
        "gate": "data_sources",
        "passed": not all_tables or has_data_sources,
        "detail": "OK" if not all_tables or has_data_sources else "tables exist but no dataSources defined",
    })

    # Gate 6: non-temporary adapter
    is_temporary = bool((definition.get("adapter") or {}).get("temporary"))
    gates.append({
        "gate": "non_temporary",
        "passed": not is_temporary,
        "detail": "adapter.temporary=true — screen is not native yet" if is_temporary else "OK",
    })

    failed = [g for g in gates if not g["passed"]]
    return {
        "screenId": definition.get("id"),
        "generatorReady": len(failed) == 0,
        "gates": gates,
        "errors": [f"[{g['gate']}] {g['detail']}" for g in failed],
    }


@router.get("/{mask_id}/readiness", response_model=dict[str, Any], summary="Generator-Readiness pruefen")
async def get_mask_readiness(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Prueft alle Generator-Readiness-Gates fuer eine Maske.

    Gibt generatorReady=true nur wenn alle 6 Gates gruen sind:
    schema_valid, sort_whitelist, filter_columns, agent_contract, data_sources, non_temporary.
    """
    _ = tenant_id
    normalized = mask_id.strip("/")
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return _check_readiness(definition)
