"""
Process Kernel API — Wave 11

Command-Catalog, Policy-Override-Resolution, Exception-Katalog,
Prozessreferenz-Kontext und Explainability.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from ....core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionService,
    build_action_conflict_error,
)
from ....core.action_idempotency import (
    IdempotencyConflictError,
    get_action_idempotency_store,
)
from ....core.process_commands import get_process_command_catalog
from ....core.process_references import build_process_reference_context
from ....core.policy_decisions import PolicyOverrideLayer, resolve_policy_override_layers
from ....core.exception_rules import DEFAULT_SETTLEMENT_EXCEPTION_CATALOG, ProcessExceptionCatalog
from ....core.explainability import build_policy_explainability_view
from ....core.agrar_process_references import build_agrar_settlement_reference_context
from ....core.aggregate_registry import get_aggregate_definition
from ....core.canonical_process_definitions import (
    get_canonical_process_definition,
    get_canonical_process_definitions,
    get_canonical_processes_by_domain,
    get_canonical_processes_by_workflow_key,
)
from ....core.workflow_versioning import (
    get_active_workflow_version,
    get_workflow_version_registry,
    get_workflow_versions_for_process_definition,
)
from ....core.settlement_approval import (
    SettlementApprovalStatus,
    get_allowed_transitions,
    is_terminal,
)
from ....core.settlement_human_gate import get_default_gate_rules
from ....core.process_sla import build_default_sla_policies

router = APIRouter(prefix="/process", tags=["process-kernel", "commands"])

_EXCEPTION_CATALOGS: dict[str, ProcessExceptionCatalog] = {
    "settlement": DEFAULT_SETTLEMENT_EXCEPTION_CATALOG,
}


# ---------------------------------------------------------------------------
# AP1: Command-Catalog
# ---------------------------------------------------------------------------

@router.get("/commands", response_model=dict)
def get_commands() -> dict[str, Any]:
    """Liefert den vollständigen Process-Command-Katalog."""
    catalog = get_process_command_catalog()
    return {
        "commands": [cmd.model_dump(mode="json") for cmd in catalog],
        "count": len(catalog),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# AP2: Policy-Override-Resolution
# ---------------------------------------------------------------------------

@router.post("/policy/resolve", response_model=dict)
def resolve_policy(body: dict) -> dict[str, Any]:
    """Löst Policy-Override-Schichten auf und gibt die wirksame Entscheidung zurück."""
    rule_id: str = body.get("rule_id", "")
    if not rule_id:
        raise HTTPException(status_code=422, detail="rule_id is required")
    raw_layers: list[dict] = body.get("layers", [])
    layers = [PolicyOverrideLayer(**layer) for layer in raw_layers]
    base_params: dict[str, Any] = body.get("base_params") or {}
    resolution = resolve_policy_override_layers(rule_id, layers, base_params=base_params)
    return {**resolution.model_dump(mode="json"), "schema_version": 1}


# ---------------------------------------------------------------------------
# AP3: Exception-Catalog
# ---------------------------------------------------------------------------

@router.get("/exceptions/{process_key}", response_model=dict)
def get_exception_catalog(process_key: str) -> dict[str, Any]:
    """Liefert den Ausnahmekatalog für einen Prozesskern-Schlüssel."""
    catalog = _EXCEPTION_CATALOGS.get(process_key)
    if catalog is None:
        raise HTTPException(status_code=404, detail=f"Kein Ausnahmekatalog für Prozess '{process_key}'")
    return {
        **catalog.model_dump(mode="json"),
        "rule_count": len(catalog.rules),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# AP4: Prozessreferenz-Kontext
# ---------------------------------------------------------------------------

@router.post("/references", response_model=dict)
def build_reference(body: dict) -> dict[str, Any]:
    """Baut einen Prozessreferenz-Kontext für den Kernprozess."""
    process_key: str = body.get("process_key", "")
    anchor_entity: str = body.get("anchor_entity", "")
    anchor_id: str = body.get("anchor_id", "")
    if not process_key or not anchor_entity or not anchor_id:
        raise HTTPException(status_code=422, detail="process_key, anchor_entity und anchor_id sind erforderlich")
    ctx = build_process_reference_context(
        process_key=process_key,
        anchor_entity=anchor_entity,
        anchor_id=anchor_id,
        contract_id=body.get("contract_id"),
        harvest_acceptance_id=body.get("harvest_acceptance_id"),
        weighing_ticket_id=body.get("weighing_ticket_id"),
        quality_protocol_id=body.get("quality_protocol_id"),
        settlement_id=body.get("settlement_id"),
        charge_id=body.get("charge_id"),
        supplier_id=body.get("supplier_id"),
        article_id=body.get("article_id"),
    )
    return {**ctx.model_dump(mode="json"), "schema_version": 1}


# ---------------------------------------------------------------------------
# AP5: Finance Follow-up — Agrar Settlement Referenz
# ---------------------------------------------------------------------------

@router.post("/references/agrar/settlement", response_model=dict)
def build_agrar_settlement_ref(body: dict) -> dict[str, Any]:
    """Baut einen Prozessreferenz-Kontext verankert an einem Settlement."""
    settlement_id: str = body.get("settlement_id", "")
    if not settlement_id:
        raise HTTPException(status_code=422, detail="settlement_id ist erforderlich")
    ctx = build_agrar_settlement_reference_context(
        settlement_id=settlement_id,
        contract_id=body.get("contract_id"),
        harvest_acceptance_id=body.get("harvest_acceptance_id"),
        weighing_ticket_id=body.get("weighing_ticket_id"),
        quality_protocol_id=body.get("quality_protocol_id"),
        charge_id=body.get("charge_id"),
        supplier_id=body.get("supplier_id"),
        article_id=body.get("article_id"),
    )
    return {**ctx.model_dump(mode="json"), "schema_version": 1}


# ---------------------------------------------------------------------------
# AP6: Explainability aus Policy-Resolution
# ---------------------------------------------------------------------------

@router.post("/explainability", response_model=dict)
def build_explainability(body: dict) -> dict[str, Any]:
    """Erzeugt eine Explainability-Sicht aus einer Policy-Override-Resolution."""
    rule_id: str = body.get("rule_id", "")
    if not rule_id:
        raise HTTPException(status_code=422, detail="rule_id ist erforderlich")
    raw_layers: list[dict] = body.get("layers", [])
    layers = [PolicyOverrideLayer(**layer) for layer in raw_layers]
    base_params: dict[str, Any] = body.get("base_params") or {}
    resolution = resolve_policy_override_layers(rule_id, layers, base_params=base_params)
    view = build_policy_explainability_view(
        resolution,
        blocked=body.get("blocked", False),
        needs_approval=body.get("needs_approval", False),
    )
    return {**view.model_dump(mode="json"), "schema_version": 1}


# ---------------------------------------------------------------------------
# Wave 17: Action Execution Layer
# ---------------------------------------------------------------------------

@router.post("/actions/execute", response_model=dict)
def execute_action(body: ActionExecutionRequest) -> dict[str, Any]:
    """Fuehrt einen Process-Kernel-Command ueber den zentralen Action-Layer aus."""
    body.normalized_reference_context()
    try:
        get_aggregate_definition(body.aggregate_type)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    store = get_action_idempotency_store()
    fingerprint = body.request_fingerprint()
    existing = store.get_by_key(body.tenant_id, body.idempotency_key)
    if existing is not None:
        if existing.request_fingerprint != fingerprint:
            error = build_action_conflict_error()
            raise HTTPException(status_code=409, detail=error.model_dump(mode="json"))
        replay = existing.result.as_idempotent_replay()
        return replay.model_dump(mode="json")

    service = ActionExecutionService()
    result = service.execute(body)
    try:
        store.remember(
            tenant_id=body.tenant_id,
            idempotency_key=body.idempotency_key,
            request_fingerprint=fingerprint,
            result=result,
        )
    except IdempotencyConflictError as exc:
        error = build_action_conflict_error()
        raise HTTPException(status_code=409, detail=error.model_dump(mode="json")) from exc
    return result.model_dump(mode="json")


@router.get("/actions/idempotency/{tenant_id}/{idempotency_key}", response_model=dict)
def get_action_by_idempotency(tenant_id: str, idempotency_key: str) -> dict[str, Any]:
    """Liefert den kanonischen Action-Snapshot zu einem Idempotency-Key."""
    store = get_action_idempotency_store()
    record = store.get_by_key(tenant_id, idempotency_key)
    if record is None:
        raise HTTPException(status_code=404, detail="Keine Action zu diesem Idempotency-Key gefunden")
    return record.result.model_dump(mode="json")


@router.get("/actions/{execution_id}", response_model=dict)
def get_action_by_execution_id(execution_id: str) -> dict[str, Any]:
    """Liefert den kanonischen Action-Snapshot zu einer execution_id."""
    store = get_action_idempotency_store()
    record = store.get_by_execution_id(execution_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Keine Action zu dieser execution_id gefunden")
    return record.result.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Wave 18: Process Definitions + Workflow Versioning Surfacing
# ---------------------------------------------------------------------------


@router.get("/definitions", response_model=dict)
def list_process_definitions(
    domain: str | None = None,
    workflow_key: str | None = None,
) -> dict[str, Any]:
    """Liefert kanonische Prozessdefinitionen optional gefiltert nach Domain oder Workflow-Key."""
    if domain and workflow_key:
        definitions = [
            definition
            for definition in get_canonical_processes_by_domain(domain)
            if workflow_key in definition.workflow_process_keys
        ]
    elif domain:
        definitions = get_canonical_processes_by_domain(domain)
    elif workflow_key:
        definitions = get_canonical_processes_by_workflow_key(workflow_key)
    else:
        definitions = get_canonical_process_definitions()
    return {
        "definitions": [definition.model_dump(mode="json") for definition in definitions],
        "count": len(definitions),
        "schema_version": 1,
    }


@router.get("/definitions/{process_definition_key}", response_model=dict)
def get_process_definition(process_definition_key: str) -> dict[str, Any]:
    """Liefert eine einzelne kanonische Prozessdefinition inklusive aktiver Workflow-Version."""
    try:
        definition = get_canonical_process_definition(process_definition_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    active_version = get_active_workflow_version(process_definition_key)
    return {
        **definition.model_dump(mode="json"),
        "active_workflow_version": (
            active_version.model_dump(mode="json") if active_version else None
        ),
        "schema_version": 1,
    }


@router.get("/workflows", response_model=dict)
def list_process_workflows(
    process_definition_key: str | None = None,
    active_only: bool = False,
) -> dict[str, Any]:
    """Liefert workflow-versionierte Process-Kernel-Definitionen."""
    if process_definition_key:
        workflows = get_workflow_versions_for_process_definition(process_definition_key)
    else:
        workflows = get_workflow_version_registry()
    if active_only:
        workflows = [workflow for workflow in workflows if workflow.status == "active"]
    return {
        "workflows": [workflow.model_dump(mode="json") for workflow in workflows],
        "count": len(workflows),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 19 AP5: Settlement-Approval-Status Surfacing
# ---------------------------------------------------------------------------


@router.get("/settlement/approval-status/{settlement_id}", response_model=dict)
def get_settlement_approval_status(settlement_id: str) -> dict[str, Any]:
    """
    Liefert den kanonischen Freigabe-Status einer Abrechnung.

    Gibt erlaubte Folgestatus, Human-Gate-Regeln und SLA-Policies
    fuer den agrar_settlement-Prozess zurueck (schema_version=1).
    """
    # Default-Status: ENTWURF (in einem echten System aus DB geladen)
    current_status = SettlementApprovalStatus.ENTWURF
    allowed = get_allowed_transitions(current_status)
    terminal = is_terminal(current_status)

    # SLA-Policies fuer agrar_settlement
    sla_policies = [
        p.model_dump(mode="json")
        for p in build_default_sla_policies()
        if p.process_key.startswith("agrar_settlement")
    ]

    return {
        "settlement_id": settlement_id,
        "process_definition_key": "agrar_settlement",
        "workflow_version": "1.0",
        "current_status": current_status.value,
        "allowed_transitions": [s.value for s in allowed],
        "is_terminal": terminal,
        "human_gate_rules": get_default_gate_rules(),
        "sla_policies": sla_policies,
        "schema_version": 1,
    }
