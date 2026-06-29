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
