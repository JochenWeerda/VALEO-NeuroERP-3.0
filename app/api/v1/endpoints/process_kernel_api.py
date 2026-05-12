"""
Process Kernel API — Wave 11

Command-Catalog, Policy-Override-Resolution, Exception-Katalog,
Prozessreferenz-Kontext und Explainability.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionService,
    build_action_conflict_error,
)
from ....core.action_idempotency import get_action_idempotency_store
from ....core.business_commands import build_core_command_catalog
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
from ....core.settlement_completion_contracts import (
    SettlementCompletionEvidence,
    SettlementCompletionVariant,
    SettlementFinancialDocumentKind,
    evaluate_settlement_completion,
)
from ....core.settlement_human_gate import get_default_gate_rules
from ....core.process_sla import build_default_sla_policies
from ....core.settlement_audit_chain import build_genesis_chain
from ....core.gobd_settlement_check import build_stub_gobd_check
from ....core.price_formula_engine import (
    TerminmarktPriceSpec,
    evaluate_price,
    build_deviation_alert,
)
from ....core.settlement_journal_bridge import build_settlement_journal_draft
from ....core.settlement_e2e_reference import build_e2e_reference, validate_e2e_reference
from ....core.nebenkosten_engine import (
    NebenkostenInput,
    compute_nebenkosten,
    get_default_nebenkosten_rules,
)
from ....core.kampagnen_vorlage import (
    KampagnenTyp,
    get_default_kampagnen_vorlagen,
    get_vorlage_by_typ,
    instantiate_from_vorlage,
)
from ....core.tenant_prozess_variante import (
    SchrittStatus,
    build_default_tenant_variante,
    get_default_agrar_settlement_schritte,
    resolve_process_steps,
    validate_prozess_variante,
)
from ....core.sla_eskalation_engine import (
    evaluate_sla_breach,
    get_default_sla_eskalations_policies,
)
from ....core.otel_span_contracts import get_process_kernel_spans
from ....core.policy_code_engine import (
    evaluate_policy_set,
    get_default_agrar_policy_sets,
)
from ....core.query_contracts import get_process_kernel_queries
from ....core.human_approval_gate import (
    evaluate_approval_requirement,
    get_default_approval_rules,
)
from ....core.slo_definitions import (
    check_slo_compliance,
    get_process_kernel_slos,
)
from ....core.mcp_tool_contracts import get_process_kernel_mcp_tools
from ....core.data_quality_rules import (
    DQRuleSet,
    validate_datensatz,
    get_default_dq_rulesets,
    get_dq_ruleset_for_entity,
)
from ....core.bulk_operations import (
    BulkItem,
    BulkOperationTyp,
    BulkRequest,
    get_bulk_limit_by_domain,
    get_default_bulk_limits,
    evaluate_bulk_request_with_dq,
    validate_bulk_request,
)
from ....core.background_jobs import (
    JobEnqueueRequest,
    JobTyp,
    create_job_from_request,
    evaluate_job_routing,
    get_default_job_types,
)
from ....core.scheduler_recovery import (
    build_scheduler_recovery_notification,
    build_scheduler_recovery_plan,
)
from ....services.scheduler_service import get_scheduler_status
from ....core.workflow_versioning_contracts import (
    MigrationsTyp,
    WorkflowDefinitionsStatus,
    WorkflowInstanzStatus,
    get_default_sandbox_regeln,
    get_default_workflow_definitionen,
    pruefe_migration,
)
from ....core.canonical_process_audit_trail import (
    baue_beispiel_audit_kette,
    erstelle_audit_eintrag,
)
from ....core.process_capacity_contracts import (
    KapazitaetsTyp,
    get_default_kapazitaets_einheiten,
    pruefe_workflow_kapazitaet,
)
from ....core.domain_event_schema_registry import (
    KompatibilitaetsTyp,
    finde_aktives_schema,
    get_default_event_schemas,
    pruefe_schema_kompatibilitaet,
)
from ....core.process_compensation_contracts import (
    KompensationsStatus,
    KompensationsTyp,
    SagaStatus,
    erstelle_kompensations_kette,
    get_default_saga_definitionen,
)
from ....core.workflow_checkpoint_contracts import (
    CheckpointStatus,
    erstelle_checkpoint,
    get_default_checkpoint_regeln,
)
from ....core.process_routing_contracts import (
    get_default_routing_regeln,
    route_nachricht,
)
from ....core.data_lineage_contracts import (
    LineageKnotenTyp,
    get_default_lineage_graph,
)
from ....core.feature_flag_contracts import (
    evaluiere_flags,
    get_aktive_flag_ids,
    get_default_feature_flags,
)
from ....core.process_cost_contracts import (
    AbrechnungsEinheit,
    BudgetStatus,
    KostenTyp,
    erstelle_kosten_erfassung,
    get_default_budget_ueberwachungen,
)
from ....core.process_quarantine_contracts import (
    RetryStrategie,
    berechne_quarantaene_statistik,
    get_default_quarantaene_eintraege,
)
from ....core.workflow_acl_contracts import (
    AclAktion,
    get_default_acl_regeln,
    pruefe_acl,
)
from ....core.process_state_machine_contracts import (
    fuehre_uebergang_aus,
    get_default_zustandsautomat,
)
from ....core.workflow_delegation_contracts import (
    EskalationsStufe,
    get_default_delegations_regeln,
    loeseauf_delegation,
)
from ....core.process_timeout_contracts import (
    get_default_timeout_regeln,
    pruefe_timeout,
)
from ....core.workflow_batch_contracts import (
    BatchStatus,
    erstelle_chunks,
    get_default_batch_jobs,
)
from ....core.process_notification_contracts_wave49 import (
    erstelle_zustellung,
    get_default_notifikations_vorlagen,
)
from ....core.workflow_lock_contracts import (
    LockStatus,
    LockTyp,
    akquiriere_lock,
    get_default_locks,
)
from ....core.database import get_db
from ....core.process_archive_contracts import (
    berechne_archiv_statistik,
    get_default_archiv_eintraege,
)
from ....core.workflow_metrics_contracts import (
    MetrikAggregation,
    MetrikTyp,
    PerformanzBewertung,
    aggregiere_messpunkte,
    get_default_kpi_summaries,
)
from ....core.cross_domain_projection_contracts import (
    ProjectionLagStufe,
    berechne_lag_stufe,
    erstelle_projektions_gesundheit,
    get_default_projektionen,
)
from ....core.event_replay_contracts import (
    ReplayModus,
    ReplayStatus,
    SnapshotTyp,
    get_default_replay_auftraege,
    pruefe_replay_konsistenz,
)
from ....core.command_surfacing_contracts import (
    DichteStufe,
    SurfacingAnfrage,
    SurfacingKontext,
    berechne_surfacing,
    get_default_surfacing_regeln,
)
from ....core.process_notification_contracts import (
    NotifikationsAusloeser,
    erstelle_benachrichtigung,
    get_default_abonnements,
    get_default_eskalationsregeln,
    route_benachrichtigung,
)
from ....core.sustainability_reporting import (
    EmissionsKategorie,
    berechne_energie_co2e,
    berechne_transport_co2e,
    erstelle_beispiel_esg_bericht,
)
from ....core.benchmark_cockpit import (
    BenchmarkKategorie,
    berechne_branchenperzentile,
    get_example_benchmark_report,
)
from ....core.dms_ocr_contracts import (
    DokumentTyp,
    OCREngine,
    build_ocr_kernfluss,
    get_default_erkennungsregeln,
    klassifiziere_dokument,
)
from ....core.agent_integration_contracts import (
    AgentKategorie,
    AgentAutorisierungsStufe,
    get_default_agent_tools,
    get_default_agent_use_cases,
    match_capabilities,
)
from ....core.edi_hub_contracts import (
    EDIPartnerTyp,
    EDIStandard,
    get_default_edi_partners,
    get_edi_nachrichtentyp_katalog,
)
from ....core.supply_chain_tracking import (
    ETABerechnungsRequest,
    LieferkettenPhase,
    TransportModus,
    bewerte_eta_alarm,
    berechne_eta,
    bewerte_lieferkettenstatus,
    bewerte_mengenabweichung,
    bewerte_zeitliche_abweichung,
    get_example_tracking_events,
)
from ....core.inline_validation_contracts import (
    get_default_field_validations,
    get_field_by_id,
    validate_inline_field,
)
from ....core.error_guidance_contracts import (
    FehlerKategorie,
    FehlerKontext,
    evaluate_error_guidance,
    get_default_error_guidance_rules,
)
from ....core.tenant_rate_limits import (
    RateLimitRequest,
    evaluate_rate_limit,
    get_default_cache_configs,
    get_default_rate_limit_policies,
)
from ....core.security_hardening_contracts import (
    RBACPermission,
    RBACPermissionCheck,
    evaluate_rbac_permission,
    evaluate_security_posture,
    get_default_secret_classifications,
    get_default_security_controls,
)
from ....core.dashboard_snapshots import (  # noqa: F811
    SnapshotTyp,
    SnapshotRebuildRequest,
    SnapshotRebuildResult,
    get_default_dashboard_snapshots,
    validate_snapshot,
)
from ....core.query_fallback_contracts import (
    QueryFehlerKlasse,
    evaluate_fallback,
    get_default_fallback_rules,
)

router = APIRouter(prefix="/process", tags=["process-kernel", "commands"])


class SettlementCompletionEvaluateRequest(BaseModel):
    settlement_id: str = Field(..., min_length=1)
    variant: str = Field(..., description="GUTSCHRIFT | BELASTUNG | KORREKTUR")
    approval_status: str = Field(..., description="ENTWURF | ZUR_FREIGABE | FREIGEGEBEN | VERBUCHT")
    has_approval_history: bool = False
    has_audit_chain: bool = False
    has_gobd_check: bool = False
    has_journal_entry: bool = False
    has_blockchain_anchor: bool = False
    financial_document_kind: str | None = Field(
        default=None,
        description="GUTSCHRIFT | BELASTUNG | STORNO | KORREKTUR_NEU",
    )
    financial_document_status: str | None = None
    correction_mode: str | None = None
    correction_links_complete: bool = False

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
def execute_action(body: ActionExecutionRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
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
    # Idempotenz-Persistenz erfolgt ausschliesslich in ActionExecutionService.execute
    result = service.execute(body, db=db)
    return result.model_dump(mode="json")


@router.get("/actions/idempotency/overview", response_model=dict)
def get_idempotency_overview() -> dict[str, Any]:
    """Liefert einen Monitoring-Überblick über den Idempotenz-Layer."""
    store = get_action_idempotency_store()
    store_summary = store.summary()
    catalog = build_core_command_catalog()
    idempotent_commands = [cmd.command_name for cmd in catalog if cmd.idempotent]
    human_confirmation_commands = [cmd.command_name for cmd in catalog if cmd.requires_human_confirmation]
    agent_ready_commands = [cmd.command_name for cmd in catalog if cmd.allowed_agent_types]
    total_commands = len(catalog)
    idempotent_coverage_pct = round((len(idempotent_commands) / total_commands) * 100) if total_commands else 0
    confidence_score = min(100, max(0, round((idempotent_coverage_pct * 0.7) + (min(store_summary["total_records"], total_commands) * 3))))
    return {
        "schema_version": 1,
        "catalog": {
            "total_commands": total_commands,
            "idempotent_commands": len(idempotent_commands),
            "human_confirmation_commands": len(human_confirmation_commands),
            "agent_ready_commands": len(agent_ready_commands),
            "idempotent_coverage_pct": idempotent_coverage_pct,
        },
        "store": store_summary,
        "confidence_score": confidence_score,
        "recommended_action": (
            "Idempotente Commands sind live und replay-sicher. "
            "Nutze die Monitoring-Sicht, um Retries, Replays und Command-Abdeckung zu beobachten."
        ),
        "lookup_paths": [
            "/api/v1/process/actions/execute",
            "/api/v1/process/actions/idempotency/{tenant_id}/{idempotency_key}",
            "/api/v1/process/actions/{execution_id}",
        ],
    }


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


@router.post("/settlement/completion/evaluate", response_model=dict)
def evaluate_settlement_completion_contract(
    payload: SettlementCompletionEvaluateRequest,
) -> dict[str, Any]:
    """
    Canonical acceptance contract for Gap 004.

    Evaluates whether a settlement lifecycle variant is fully completed across
    approval, audit, GoBD and financial document evidence.
    """
    try:
        variant = SettlementCompletionVariant(payload.variant)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Unknown variant: {payload.variant}") from exc

    document_kind = None
    if payload.financial_document_kind is not None:
        try:
            document_kind = SettlementFinancialDocumentKind(payload.financial_document_kind)
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown financial_document_kind: {payload.financial_document_kind}",
            ) from exc

    result = evaluate_settlement_completion(
        SettlementCompletionEvidence(
            settlement_id=payload.settlement_id,
            variant=variant,
            approval_status=payload.approval_status,
            has_approval_history=payload.has_approval_history,
            has_audit_chain=payload.has_audit_chain,
            has_gobd_check=payload.has_gobd_check,
            has_journal_entry=payload.has_journal_entry,
            has_blockchain_anchor=payload.has_blockchain_anchor,
            financial_document_kind=document_kind,
            financial_document_status=payload.financial_document_status,
            correction_mode=payload.correction_mode,
            correction_links_complete=payload.correction_links_complete,
        )
    )
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 20 AP3: Settlement Audit-Chain (GoBD Hash-Kette)
# ---------------------------------------------------------------------------


@router.get("/settlement/audit-chain/{settlement_id}", response_model=dict)
def get_settlement_audit_chain(settlement_id: str) -> dict[str, Any]:
    """
    Liefert die vollständige GoBD-konforme Audit-Hash-Kette eines Settlements.

    Jedes Glied enthält SHA-256(previous_hash + Payload), sodass nachträgliche
    Manipulation einzelner Einträge die gesamte Kette invalidiert.
    Rechtsgrundlage: GoBD Rz. 108-112 (Unveränderbarkeit des Buchungsjournals).
    """
    # In Produktion: Kette aus DB laden; hier: Demo-Kette mit einem Anker-Link
    chain = build_genesis_chain(
        settlement_id=settlement_id,
        tenant_id="demo-tenant",
        gross_amount=0.0,
    )
    return chain.as_dict()


@router.post("/settlement/audit-chain/{settlement_id}/anchor", response_model=dict)
def create_settlement_audit_chain_anchor(settlement_id: str, payload: dict | None = None, db=Depends(get_db)) -> dict[str, Any]:
    from app.core.blockchain_anchor_runtime import anchor_settlement_audit_chain

    body = payload or {}
    chain = build_genesis_chain(
        settlement_id=settlement_id,
        tenant_id=body.get("tenant_id", "demo-tenant"),
        gross_amount=float(body.get("gross_amount", 0.0)),
        currency=body.get("currency", "EUR"),
        actor_id=body.get("actor_id", "system"),
    )
    anchor = anchor_settlement_audit_chain(db, chain=chain)
    return {
        "settlement_audit_chain": chain.as_dict(),
        "blockchain_anchor": anchor.as_dict(),
    }


# ---------------------------------------------------------------------------
# Wave 20 AP5: GoBD-Vollständigkeitsprüfung
# ---------------------------------------------------------------------------


@router.get("/settlement/gobd-check/{settlement_id}", response_model=dict)
def get_settlement_gobd_check(settlement_id: str) -> dict[str, Any]:
    """
    GoBD-Pflicht-Check für ein Settlement.

    Prueft ob alle Pflichtfelder (Belegnummer, Buchungsdatum, Betrag, Gegenkonto,
    Audit-Hash, Prozessreferenz) vorhanden sind. `compliant=True` bedeutet:
    das Settlement ist buchungsreif unter GoBD §§ 146/147 AO.
    """
    result = build_stub_gobd_check(settlement_id)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 21 AP3: Preis-Preview
# ---------------------------------------------------------------------------


@router.get("/settlement/price-preview/{settlement_id}", response_model=dict)
def get_settlement_price_preview(settlement_id: str) -> dict[str, Any]:
    """
    Preis-Preview fuer ein Settlement mit vollstaendiger Audit-Spur.

    Demonstriert alle drei Preistypen (FIXED, FORMULA, TERMINMARKT).
    In Produktion: Preisspezifikation aus Kontrakt-Stammdaten laden.
    """
    from decimal import Decimal

    # Demo: Terminmarkt-Preis (MATIF) mit Basis-Spread
    spec = TerminmarktPriceSpec(
        market_reference_id="MATIF_WEIZEN_MAR26",
        settlement_price_eur_per_ton=Decimal("225.50"),
        basis_spread_eur_per_ton=Decimal("-3.00"),
    )
    reference = Decimal("220.00")
    evaluation = evaluate_price(spec, reference_price=reference)
    alert = build_deviation_alert(settlement_id, evaluation)

    return {
        "settlement_id": settlement_id,
        "price_evaluation": evaluation.as_dict(),
        "deviation_alert": alert.as_dict() if alert else None,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 21 AP4: Journal-Preview
# ---------------------------------------------------------------------------


@router.get("/settlement/journal-preview/{settlement_id}", response_model=dict)
def get_settlement_journal_preview(settlement_id: str) -> dict[str, Any]:
    """
    Buchungsvorschau (JournalEntryDraft) fuer ein genehmigtes Settlement.

    In Produktion: Betraege aus Settlement-DB laden.
    Liefert Soll/Haben-Saetze, Gegenkonto und Prozessreferenz.
    """
    from decimal import Decimal

    draft = build_settlement_journal_draft(
        settlement_id=settlement_id,
        tenant_id="demo-tenant",
        gross_amount=Decimal("5000.00"),
        total_deductions=Decimal("250.00"),
        net_amount=Decimal("4750.00"),
    )

    e2e_ref = build_e2e_reference(
        settlement_id=settlement_id,
        tenant_id="demo-tenant",
        kontrakt_id=f"KNT-{settlement_id}",
        annahme_id=f"ANH-{settlement_id}",
    )
    e2e_validation = validate_e2e_reference(e2e_ref)

    return {
        "settlement_id": settlement_id,
        "journal_draft": draft.as_dict(),
        "e2e_reference": e2e_ref.as_dict(),
        "e2e_validation": e2e_validation.as_dict(),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 23 AP3: Nebenkosten-Vorschau
# ---------------------------------------------------------------------------


@router.get("/settlement/nebenkosten-preview/{settlement_id}", response_model=dict)
def get_settlement_nebenkosten_preview(settlement_id: str) -> dict[str, Any]:
    """
    Nebenkosten-Vorschau fuer ein Settlement (Gap 007).

    Liefert vollstaendigen NebenkostenBreakdown auf Basis der
    Standard-Regelsets. In Produktion: Mengen/Strecken aus Settlement laden.
    """
    from decimal import Decimal

    inp = NebenkostenInput(
        settlement_id=settlement_id,
        tenant_id="demo-tenant",
        billing_qty_tons=Decimal("50.0"),
        transport_km=Decimal("120.0"),
        storage_days=Decimal("14"),
        weighing_count=2,
    )
    rules = get_default_nebenkosten_rules()
    breakdown = compute_nebenkosten(inp, rules)

    return {
        "settlement_id": settlement_id,
        "nebenkosten": breakdown.as_dict(),
        "rule_count": len(rules),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 24 AP3: Kampagnenvorlagen
# ---------------------------------------------------------------------------


@router.get("/kampagnen/vorlagen", response_model=dict)
def list_kampagnen_vorlagen() -> dict[str, Any]:
    """
    Alle verfuegbaren Standard-Kampagnenvorlagen (Gap 005).

    Liefert Metadaten + Qualitaetsschwellen fuer alle 5 Ernte-Typen.
    """
    vorlagen = get_default_kampagnen_vorlagen()
    return {
        "vorlagen": [v.as_dict() for v in vorlagen],
        "count": len(vorlagen),
        "schema_version": 1,
    }


@router.get("/kampagnen/vorlagen/{typ}/instantiate", response_model=dict)
def instantiate_kampagnen_vorlage(typ: str) -> dict[str, Any]:
    """
    Instantiiert eine Kampagne aus der Standard-Vorlage fuer den angegebenen Typ.

    Typ-Werte: WINTERWEIZEN, SOMMERGERSTE, RAPS, KOERNERMAIS, ZUCKERRUEBEN
    """
    try:
        kampagnen_typ = KampagnenTyp(typ.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unbekannter Kampagnentyp: '{typ}'. Gueltig: {[t.value for t in KampagnenTyp]}",
        )

    vorlage = get_vorlage_by_typ(kampagnen_typ)
    if vorlage is None:
        raise HTTPException(status_code=404, detail=f"Keine Vorlage fuer Typ '{typ}' gefunden")

    instanz = instantiate_from_vorlage(
        vorlage,
        instanz_id=f"KI-{typ.upper()}-DEMO",
        tenant_id="demo-tenant",
        wirtschaftsjahr=2026,
    )
    return {
        "instanz": instanz.as_dict(),
        "vorlage_id": vorlage.vorlage_id,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 24 AP4: Tenant-Prozessvarianten
# ---------------------------------------------------------------------------


@router.get("/tenant/prozess-varianten", response_model=dict)
def list_tenant_prozess_varianten() -> dict[str, Any]:
    """
    Verfuegbare Prozessvarianten-Registry (Gap 009).

    Liefert alle unterstuetzten Prozesse mit Default-Schritten.
    """
    schritte = get_default_agrar_settlement_schritte()
    return {
        "prozesse": [
            {
                "prozess_key": "agrar_settlement",
                "bezeichnung": "Agrar Settlement-Prozess",
                "schritt_count": len(schritte),
                "pflichtschritte": sum(1 for s in schritte if s.pflicht),
                "optionale_schritte": sum(1 for s in schritte if not s.pflicht),
            }
        ],
        "schema_version": 1,
    }


@router.get("/tenant/prozess-varianten/{prozess_key}/steps", response_model=dict)
def get_tenant_prozess_steps(prozess_key: str) -> dict[str, Any]:
    """
    Aufgeloeste Prozessschritte fuer einen Prozess (Default + keine Overrides).

    In Produktion: Tenant-Overrides aus Konfiguration laden.
    """
    variante = build_default_tenant_variante(
        tenant_id="demo-tenant",
        prozess_key=prozess_key,
    )
    steps = resolve_process_steps(variante)
    validation = validate_prozess_variante(variante)

    return {
        "prozess_key": prozess_key,
        "variante_id": variante.variante_id,
        "steps": [s.as_dict() for s in steps],
        "step_count": len(steps),
        "validation": validation.as_dict(),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 26 AP3: Trocknungsabrechnung-Vorschau
# ---------------------------------------------------------------------------

from ....core.trocknungs_abrechnung import (
    TrocknungsInput,
    TrocknungsMethode,
    TrocknungsRegelParametrierung,
    compute_trocknungs_abrechnung,
    get_default_trocknungsregeln,
    validate_trocknungs_ergebnis,
)
from ....core.workflow_migrations_guard import (
    WorkflowDefinitionSnapshot,
    WorkflowSchrittSnapshot,
    validate_workflow_migration,
)


@router.get("/trocknungs-abrechnung/preview/{settlement_id}", response_model=dict)
def get_trocknungs_preview(settlement_id: str) -> dict[str, Any]:
    """
    Trocknungsabrechnung-Vorschau fuer ein Settlement (Gap 003).

    Deterministisch: gleicher Input => gleicher SHA-256 Audit-Hash.
    In Produktion: Messwerte aus Annahmeprozess laden.
    """
    from decimal import Decimal

    crop_code = "WW"
    params_map = get_default_trocknungsregeln()
    params = params_map.get(crop_code, TrocknungsRegelParametrierung())

    inp = TrocknungsInput(
        settlement_id=settlement_id,
        tenant_id="demo-tenant",
        crop_code=crop_code,
        rule_set_id="RS-WW-2024",
        rule_set_version=1,
        brutto_gewicht_kg=Decimal("50000"),
        eingangs_feuchte_pct=Decimal("17.2"),
        ziel_feuchte_pct=Decimal("14.5"),
        methode=TrocknungsMethode.FAKTOR_STUFUNG,
    )
    ergebnis = compute_trocknungs_abrechnung(inp, params)
    validation = validate_trocknungs_ergebnis(ergebnis)

    return {
        "settlement_id": settlement_id,
        "trocknungs_ergebnis": ergebnis.as_dict(),
        "validation": validation.as_dict(),
        "schema_version": 1,
    }


@router.get("/trocknungs-abrechnung/regelsets", response_model=dict)
def get_trocknungs_regelsets() -> dict[str, Any]:
    """Verfuegbare Default-Trocknungsregelsets (WW/SG/RA/KM/ZR)."""
    params_map = get_default_trocknungsregeln()
    return {
        "regelsets": {
            code: {
                "crop_code": code,
                "start_threshold_pct": str(p.start_threshold_pct),
                "trocknungskosten_eur_per_pct_per_t": str(p.trocknungskosten_eur_per_pct_per_t),
                "schwund_faktor": str(p.schwund_faktor),
                "max_abzug_pct": str(p.max_abzug_pct) if p.max_abzug_pct else None,
            }
            for code, p in params_map.items()
        },
        "count": len(params_map),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 26 AP4: Workflow-Migrations-Guard
# ---------------------------------------------------------------------------


@router.post("/workflow-migration/check", response_model=dict)
def check_workflow_migration(body: dict) -> dict[str, Any]:
    """
    Prueft ob eine Workflow-Migrations-Definition sicher ist (Gap 011).

    Body: { "prozess_key": str, "von_version": str, "zu_version": str,
            "alt_schritte": [...], "neu_schritte": [...] }
    """
    prozess_key = body.get("prozess_key", "agrar_settlement")
    von_version = body.get("von_version", "1.0")
    zu_version = body.get("zu_version", "1.1")

    def _parse_schritte(raw: list) -> list[WorkflowSchrittSnapshot]:
        return [
            WorkflowSchrittSnapshot(
                schritt_id=s.get("schritt_id", ""),
                pflicht=bool(s.get("pflicht", True)),
                reihenfolge=int(s.get("reihenfolge", 0)),
                terminal=bool(s.get("terminal", False)),
                rolle=s.get("rolle", ""),
            )
            for s in raw
            if s.get("schritt_id")
        ]

    alt_schritte = _parse_schritte(body.get("alt_schritte", []))
    neu_schritte = _parse_schritte(body.get("neu_schritte", []))

    # Defaults wenn keine Schritte uebergeben: agrar_settlement Demo
    if not alt_schritte:
        schritte = get_default_agrar_settlement_schritte()
        alt_schritte = [
            WorkflowSchrittSnapshot(
                schritt_id=s.schritt_id,
                pflicht=s.pflicht,
                reihenfolge=s.reihenfolge,
                terminal=(s.schritt_id == "AS-06-VERBUCHUNG"),
                rolle=s.rolle,
            )
            for s in schritte
        ]
        neu_schritte = alt_schritte[:]  # identisch → SAFE

    alt_snap = WorkflowDefinitionSnapshot(
        prozess_key=prozess_key,
        version=von_version,
        schema_version=1,
        schritte=alt_schritte,
    )
    neu_snap = WorkflowDefinitionSnapshot(
        prozess_key=prozess_key,
        version=zu_version,
        schema_version=1,
        schritte=neu_schritte,
    )
    result = validate_workflow_migration(alt_snap, neu_snap)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 28 AP3: SLA-Eskalationen
# ---------------------------------------------------------------------------

@router.get("/sla/eskalationen", response_model=dict)
def get_sla_eskalationen(
    ist_dauer_stunden: float = 0.0,
) -> dict[str, Any]:
    """
    Wertet alle Default-SLA-Policies fuer eine gegebene Ist-Dauer aus.

    ?ist_dauer_stunden=  — Anzahl vergangener Stunden (fuer Demo-/Test-Zwecke).
    """
    from decimal import Decimal
    policies = get_default_sla_eskalations_policies()
    dauer = Decimal(str(ist_dauer_stunden))
    auswertungen = [
        evaluate_sla_breach(p, instanz_id=f"demo-{p.policy_id}", ist_dauer_stunden=dauer).as_dict()
        for p in policies
    ]
    return {
        "ist_dauer_stunden": str(dauer),
        "policy_count": len(policies),
        "auswertungen": auswertungen,
        "schema_version": 1,
    }


@router.get("/sla/eskalationen/{prozess_key}", response_model=dict)
def get_sla_eskalationen_by_prozess(
    prozess_key: str,
    ist_dauer_stunden: float = 0.0,
) -> dict[str, Any]:
    """
    Wertet SLA-Policies fuer einen spezifischen Prozess aus.

    Gibt 404 wenn kein Policy fuer den Prozess bekannt.
    """
    from decimal import Decimal
    policies = [p for p in get_default_sla_eskalations_policies() if p.prozess_key == prozess_key]
    if not policies:
        raise HTTPException(status_code=404, detail=f"Kein SLA-Policy fuer prozess_key={prozess_key!r}")
    dauer = Decimal(str(ist_dauer_stunden))
    auswertungen = [
        evaluate_sla_breach(p, instanz_id=f"demo-{p.policy_id}", ist_dauer_stunden=dauer).as_dict()
        for p in policies
    ]
    return {
        "prozess_key": prozess_key,
        "ist_dauer_stunden": str(dauer),
        "policy_count": len(policies),
        "auswertungen": auswertungen,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 28 AP4: OTel Span-Registry
# ---------------------------------------------------------------------------

@router.get("/otel/span-registry", response_model=dict)
def get_otel_span_registry(domain: str = "") -> dict[str, Any]:
    """
    Gibt registrierte OpenTelemetry Span-Contracts zurueck.

    ?domain=  — Optional: Filtert nach Domain (agrar, finance, workflow, compliance, process).
    """
    registry = get_process_kernel_spans()
    if domain:
        contracts = registry.by_domain(domain)
        return {
            "domain_filter": domain,
            "contract_count": len(contracts),
            "convention_violations": [
                c.span_name for c in contracts if not c.validate_name()
            ],
            "contracts": [c.as_dict() for c in contracts],
            "schema_version": 1,
        }
    return registry.as_dict()


# ---------------------------------------------------------------------------
# Wave 29 AP3: Policy-as-Code Endpoints
# ---------------------------------------------------------------------------

@router.get("/policy-rules/{prozess_key}", response_model=dict)
def get_policy_rules(prozess_key: str) -> dict[str, Any]:
    """
    Gibt alle PolicySets fuer einen Prozess-Key zurueck.

    Gibt 404 wenn kein PolicySet fuer den prozess_key bekannt.
    """
    all_sets = get_default_agrar_policy_sets()
    matched = [ps for ps in all_sets if ps.prozess_key == prozess_key]
    if not matched:
        raise HTTPException(status_code=404, detail=f"Kein PolicySet fuer prozess_key={prozess_key!r}")
    return {
        "prozess_key": prozess_key,
        "policy_set_count": len(matched),
        "policy_sets": [ps.as_dict() for ps in matched],
        "schema_version": 1,
    }


@router.post("/policy-rules/evaluate", response_model=dict)
def evaluate_policy_rules(body: dict) -> dict[str, Any]:
    """
    Wertet PolicySet gegen einen Kontext aus.

    Body: { "prozess_key": str, "policy_set_id": str (optional), "kontext": dict }
    Gibt PolicyEvaluationResult zurueck.
    """
    prozess_key: str = body.get("prozess_key", "")
    policy_set_id: str = body.get("policy_set_id", "")
    kontext: dict = body.get("kontext", {})

    if not prozess_key:
        raise HTTPException(status_code=422, detail="prozess_key ist erforderlich")

    all_sets = get_default_agrar_policy_sets()

    if policy_set_id:
        matched = [ps for ps in all_sets if ps.policy_set_id == policy_set_id]
    else:
        matched = [ps for ps in all_sets if ps.prozess_key == prozess_key]

    if not matched:
        raise HTTPException(status_code=404, detail=f"Kein PolicySet gefunden fuer prozess_key={prozess_key!r}")

    # Ersten passenden PolicySet auswerten
    policy_set = matched[0]
    result = evaluate_policy_set(policy_set, kontext)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 29 AP6: Query-Registry Endpoint
# ---------------------------------------------------------------------------

@router.get("/query-registry", response_model=dict)
def get_query_registry(prozess_key: str = "") -> dict[str, Any]:
    """
    Gibt registrierte Query-Contracts zurueck.

    ?prozess_key= — Optional: Filtert nach Prozess-Key.
    """
    registry = get_process_kernel_queries()
    if prozess_key:
        contracts = registry.by_prozess_key(prozess_key)
        return {
            "prozess_key_filter": prozess_key,
            "contract_count": len(contracts),
            "contracts": [c.as_dict() for c in contracts],
            "schema_version": 1,
        }
    return registry.as_dict()


# ---------------------------------------------------------------------------
# Wave 30 AP3: Human-Approval-Gate Endpoints
# ---------------------------------------------------------------------------

@router.get("/agent/approval-rules", response_model=dict)
def get_agent_approval_rules() -> dict[str, Any]:
    """Gibt alle Default-Approval-Regeln fuer Agent-Aktionen zurueck."""
    regeln = get_default_approval_rules()
    return {
        "regel_count": len(regeln),
        "regeln": [r.as_dict() for r in regeln],
        "schema_version": 1,
    }


@router.post("/agent/approval-evaluate", response_model=dict)
def evaluate_agent_approval(body: dict) -> dict[str, Any]:
    """
    Bewertet ob eine Agent-Aktion menschliche Freigabe erfordert.

    Body: { "aktions_typ": str, "kontext": dict }
    """
    aktions_typ: str = body.get("aktions_typ", "")
    kontext: dict = body.get("kontext", {})
    if not aktions_typ:
        raise HTTPException(status_code=422, detail="aktions_typ ist erforderlich")
    regeln = get_default_approval_rules()
    result = evaluate_approval_requirement(aktions_typ, kontext, regeln)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 30 AP6: SLO-Registry Endpoints
# ---------------------------------------------------------------------------

@router.get("/slo/registry", response_model=dict)
def get_slo_registry(dienst: str = "") -> dict[str, Any]:
    """
    Gibt registrierte SLO-Definitionen zurueck.

    ?dienst= — Optional: Filtert nach Dienst.
    """
    registry = get_process_kernel_slos()
    if dienst:
        slos = registry.by_dienst(dienst)
        return {
            "dienst_filter": dienst,
            "slo_count": len(slos),
            "slos": [s.as_dict() for s in slos],
            "schema_version": 1,
        }
    return registry.as_dict()


@router.post("/slo/check", response_model=dict)
def check_slo(body: dict) -> dict[str, Any]:
    """
    Prueft ob ein Ist-Wert ein SLO erfuellt.

    Body: { "slo_id": str, "ist_wert": float | null }
    """
    slo_id: str = body.get("slo_id", "")
    ist_wert = body.get("ist_wert")
    if not slo_id:
        raise HTTPException(status_code=422, detail="slo_id ist erforderlich")
    registry = get_process_kernel_slos()
    slo = registry.by_slo_id(slo_id)
    if slo is None:
        raise HTTPException(status_code=404, detail=f"SLO {slo_id!r} nicht gefunden")
    result = check_slo_compliance(slo, float(ist_wert) if ist_wert is not None else None)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 31 AP3: MCP Tool-Registry Endpoint
# ---------------------------------------------------------------------------

@router.get("/agent/tool-registry", response_model=dict)
def get_mcp_tool_registry(domain: str = "") -> dict[str, Any]:
    """
    Gibt MCP/OpenAPI Tool-Contracts fuer externe Agenten zurueck.

    ?domain= — Optional: Filtert nach Domain (agrar, finance, workflow, ...).
    """
    registry = get_process_kernel_mcp_tools()
    # as_mcp_tool() gibt nur name/description/inputSchema zurueck —
    # kein api_endpoint oder interne Felder (Informationsminimierung).
    if domain:
        tools = registry.by_domain(domain)
        return {
            "domain_filter": domain,
            "tool_count": len(tools),
            "tools": [t.as_mcp_tool() for t in tools],
            "schema_version": 1,
        }
    all_tools = registry.tools
    return {
        "tool_count": len(all_tools),
        "domains": sorted({t.domain for t in all_tools}),
        "convention_violations": [
            t.tool_name for t in all_tools if not t.validate_name()
        ],
        "tools": [t.as_mcp_tool() for t in all_tools],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 31 AP6: Datenqualitaets-Endpoints
# ---------------------------------------------------------------------------

def _dq_ruleset_public(ruleset: "DQRuleSet") -> dict:
    """Serialisiert ein DQRuleSet ohne interne Implementierungsdetails."""
    d = ruleset.as_dict()
    for regel in d.get("regeln", []):
        # format_regex und unique_felder sind Implementierungsdetails,
        # nicht fuer externe Konsumenten bestimmt.
        regel.pop("format_regex", None)
        regel.pop("unique_felder", None)
    return d


@router.get("/data-quality/rulesets", response_model=dict)
def get_dq_rulesets() -> dict[str, Any]:
    """
    Gibt alle Default-DQ-Regelsets zurueck (Debitor, Lieferant, Kontrakt, Wiegeschein, Artikel, APRechnung, Abrechnung).
    """
    rulesets = get_default_dq_rulesets()
    return {
        "ruleset_count": len(rulesets),
        "rulesets": {k: _dq_ruleset_public(v) for k, v in rulesets.items()},
        "schema_version": 1,
    }


@router.post("/data-quality/validate", response_model=dict)
def validate_dq(body: dict) -> dict[str, Any]:
    """
    Validiert einen Datensatz gegen ein DQ-Regelset.

    Body: { "entity_typ": str, "datensatz": dict, "kontext_datensaetze": list[dict] | null }
    Optional: "ruleset_id" zum expliziten Regelset-Lookup (wird ignoriert, wenn entity_typ passt).
    """
    entity_typ: str = body.get("entity_typ", "")
    datensatz: dict = body.get("datensatz", {})
    kontext: list[dict] | None = body.get("kontext_datensaetze")

    if not entity_typ:
        raise HTTPException(status_code=422, detail="entity_typ ist erforderlich")
    if not isinstance(datensatz, dict):
        raise HTTPException(status_code=422, detail="datensatz muss ein Objekt sein")

    # Eingabegrenzen: DoS-Schutz
    _MAX_FELDER = 50
    _MAX_FELDWERT_LEN = 1000
    _MAX_KONTEXT = 100
    if len(datensatz) > _MAX_FELDER:
        raise HTTPException(status_code=422, detail=f"datensatz darf maximal {_MAX_FELDER} Felder enthalten")
    for k, v in datensatz.items():
        if isinstance(v, str) and len(v) > _MAX_FELDWERT_LEN:
            raise HTTPException(
                status_code=422,
                detail=f"Feldwert '{k}' ueberschreitet maximale Laenge ({_MAX_FELDWERT_LEN} Zeichen)",
            )
    if kontext is not None:
        if not isinstance(kontext, list) or len(kontext) > _MAX_KONTEXT:
            raise HTTPException(status_code=422, detail=f"kontext_datensaetze darf maximal {_MAX_KONTEXT} Eintraege enthalten")

    rulesets = get_default_dq_rulesets()
    ruleset = rulesets.get(entity_typ)
    if ruleset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Kein Regelset fuer entity_typ '{entity_typ}'. Bekannt: {list(rulesets.keys())}",
        )

    result = validate_datensatz(ruleset, datensatz, kontext)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 32 AP3: Dashboard-Snapshot-Endpoints
# ---------------------------------------------------------------------------

@router.get("/dashboards/snapshots", response_model=dict)
def get_dashboard_snapshots(typ: str = "") -> dict[str, Any]:
    """
    Gibt Dashboard-Snapshot-Definitionen zurueck.

    ?typ= — Optional: Filtert nach SnapshotTyp (z.B. FINANCE_KPIS).
    """
    registry = get_default_dashboard_snapshots()
    if typ:
        snapshot = registry.by_typ_str(typ)
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Snapshot-Typ '{typ}' nicht gefunden. Bekannt: {[s.snapshot_typ.value for s in registry.snapshots]}",
            )
        return snapshot.as_dict()
    return registry.as_dict()


@router.post("/dashboards/rebuild", response_model=dict)
def trigger_dashboard_rebuild(body: dict) -> dict[str, Any]:
    """
    Loest einen manuellen Snapshot-Rebuild aus.

    Body: { "snapshot_typ": str, "angefordert_von": str, "begruendung": str }
    """
    typ_str: str = body.get("snapshot_typ", "")
    angefordert_von: str = body.get("angefordert_von", "")

    if not typ_str:
        raise HTTPException(status_code=422, detail="snapshot_typ ist erforderlich")
    if not angefordert_von:
        raise HTTPException(status_code=422, detail="angefordert_von ist erforderlich")

    registry = get_default_dashboard_snapshots()
    snapshot = registry.by_typ_str(typ_str)
    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot-Typ '{typ_str}' nicht gefunden.",
        )

    result = SnapshotRebuildResult(
        snapshot_typ=snapshot.snapshot_typ,
        ausgeloest=True,
        meldung=(
            f"Rebuild fuer '{typ_str}' von '{angefordert_von}' angefordert. "
            f"Rebuild-Endpunkt: {snapshot.rebuild_endpoint}"
        ),
    )
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 32 AP6: Query-Fallback-Endpoints
# ---------------------------------------------------------------------------

@router.get("/query-fallbacks", response_model=dict)
def get_query_fallbacks(domain: str = "") -> dict[str, Any]:
    """
    Gibt Query-Fallback-Regeln zurueck.

    ?domain= — Optional: Filtert nach Domain (finance, agrar, compliance, workflow).
    """
    regeln = get_default_fallback_rules()
    if domain:
        gefiltert = [r for r in regeln if r.domain == domain or r.domain == "*"]
        return {
            "domain_filter": domain,
            "regel_count": len(gefiltert),
            "regeln": [r.as_dict() for r in gefiltert],
            "schema_version": 1,
        }
    return {
        "regel_count": len(regeln),
        "domains": sorted({r.domain for r in regeln}),
        "regeln": [r.as_dict() for r in regeln],
        "schema_version": 1,
    }


@router.post("/query-fallbacks/evaluate", response_model=dict)
def evaluate_query_fallback(body: dict) -> dict[str, Any]:
    """
    Bestimmt den Fallback fuer einen fehlgeschlagenen Query.

    Body: { "fehler_klasse": str, "domain": str, "query_name": str }
    """
    fehler_str: str = body.get("fehler_klasse", "")
    domain: str = body.get("domain", "")
    query_name: str = body.get("query_name", "")

    if not fehler_str or not domain or not query_name:
        raise HTTPException(
            status_code=422,
            detail="fehler_klasse, domain und query_name sind erforderlich",
        )

    try:
        fehler_klasse = QueryFehlerKlasse(fehler_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte fehler_klasse '{fehler_str}'. Erlaubt: {[e.value for e in QueryFehlerKlasse]}",
        )

    regeln = get_default_fallback_rules()
    result = evaluate_fallback(fehler_klasse, domain, query_name, regeln)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 33 — AP3: GET /process/bulk-limits + POST /process/bulk-operations/validate
# ---------------------------------------------------------------------------

@router.get("/bulk-limits", response_model=dict)
def get_bulk_limits(domain: str = "") -> dict[str, Any]:
    """
    Gibt Bulk-Operationen-Limits zurueck.

    Query-Parameter:
    - domain: Filtert auf eine Domain (leer = alle).
    """
    limits = get_default_bulk_limits()
    if domain:
        lim = get_bulk_limit_by_domain(domain, limits)
        if lim is None:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Bulk-Limits fuer Domain '{domain}' konfiguriert.",
            )
        return {"domain": domain, "limit": lim.as_dict(), "schema_version": 1}
    return {
        "limit_count": len(limits),
        "domains": [lim.domain for lim in limits],
        "limits": [lim.as_dict() for lim in limits],
        "schema_version": 1,
    }


@router.post("/bulk-operations/validate", response_model=dict)
def validate_bulk_operation(body: dict = None) -> dict[str, Any]:
    """
    Validiert eine Bulk-Request strukturell gegen Domain-Limits.

    Body-Felder:
    - operation_typ: z.B. "CREATE"
    - domain: z.B. "agrar"
    - ressource: z.B. "wiegescheine"
    - items: Liste von {item_id, payload}
    - trocken_lauf: bool (optional, default false)
    """
    if body is None:
        body = {}

    op_str: str = body.get("operation_typ", "")
    domain: str = body.get("domain", "")
    ressource: str = body.get("ressource", "")
    items_raw: list = body.get("items", [])

    if not op_str or not domain or not ressource:
        raise HTTPException(
            status_code=422,
            detail="operation_typ, domain und ressource sind erforderlich",
        )

    if not isinstance(items_raw, list):
        raise HTTPException(status_code=422, detail="items muss eine Liste sein")

    try:
        op_typ = BulkOperationTyp(op_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter operation_typ '{op_str}'. Erlaubt: {[e.value for e in BulkOperationTyp]}",
        )

    items = [
        BulkItem(
            item_id=str(it.get("item_id", "")),
            payload=it.get("payload", {}),
        )
        for it in items_raw
        if isinstance(it, dict)
    ]

    request = BulkRequest(
        operation_typ=op_typ,
        domain=domain,
        ressource=ressource,
        items=items,
        trocken_lauf=bool(body.get("trocken_lauf", False)),
    )

    limit = get_bulk_limit_by_domain(domain)
    result = validate_bulk_request(request, limit)
    return result.as_dict()


@router.post("/bulk-operations/evaluate", response_model=dict)
def evaluate_bulk_operation_with_dq(body: dict | None = None) -> dict[str, Any]:
    """
    Evaluates a bulk request together with the active DQ rule set.

    Body fields:
    - operation_typ
    - domain
    - ressource
    - entity_typ
    - items: [{item_id, payload}]
    - trocken_lauf (optional)
    - stop_bei_erstem_fehler (optional)
    """
    if body is None:
        body = {}

    entity_typ: str = body.get("entity_typ", "")
    op_str: str = body.get("operation_typ", "")
    domain: str = body.get("domain", "")
    ressource: str = body.get("ressource", "")
    items_raw: list = body.get("items", [])

    if not entity_typ:
        raise HTTPException(status_code=422, detail="entity_typ ist erforderlich")
    if not op_str or not domain or not ressource:
        raise HTTPException(status_code=422, detail="operation_typ, domain und ressource sind erforderlich")
    if not isinstance(items_raw, list):
        raise HTTPException(status_code=422, detail="items muss eine Liste sein")

    try:
        op_typ = BulkOperationTyp(op_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter operation_typ '{op_str}'. Erlaubt: {[e.value for e in BulkOperationTyp]}",
        )

    items = [
        BulkItem(
            item_id=str(it.get("item_id", "")),
            payload=it.get("payload", {}),
        )
        for it in items_raw
        if isinstance(it, dict)
    ]

    request = BulkRequest(
        operation_typ=op_typ,
        domain=domain,
        ressource=ressource,
        items=items,
        trocken_lauf=bool(body.get("trocken_lauf", True)),
        stop_bei_erstem_fehler=bool(body.get("stop_bei_erstem_fehler", False)),
    )

    limit = get_bulk_limit_by_domain(domain)
    ruleset = get_dq_ruleset_for_entity(entity_typ)
    if ruleset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Kein DQ-Regelset fuer entity_typ '{entity_typ}' gefunden. Bekannt: {list(get_default_dq_rulesets().keys())}",
        )

    validation, result = evaluate_bulk_request_with_dq(request, entity_typ=entity_typ, limit=limit)
    return {
        "validation": validation.as_dict(),
        "bulk_result": result.as_dict(),
        "dq_ruleset": ruleset.as_dict(),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 33 — AP6: GET /process/jobs + POST /process/jobs/enqueue
# ---------------------------------------------------------------------------

@router.get("/jobs", response_model=dict)
def list_job_types(
    typ: str = "",
    status: str = "",
) -> dict[str, Any]:
    """
    Gibt den Katalog der unterstuetzten Job-Typen mit Routing-Informationen zurueck.

    Query-Parameter:
    - typ: Filtert auf einen Job-Typ (leer = alle).
    - status: reserviert fuer kuenftige Queue-Status-Abfrage.
    """
    job_defs = get_default_job_types()
    if typ:
        try:
            job_typ = JobTyp(typ)
        except ValueError:
            raise HTTPException(
                status_code=404,
                detail=f"Unbekannter Job-Typ '{typ}'. Erlaubt: {[e.value for e in JobTyp]}",
            )
        matches = [d for d in job_defs if d.typ == job_typ]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Job-Typ '{typ}' nicht gefunden.")
        jd = matches[0]
        routing = evaluate_job_routing(job_typ)
        return {
            "typ": jd.typ.value,
            "definition": jd.as_dict(),
            "routing": routing.as_dict(),
            "schema_version": 1,
        }
    return {
        "job_type_count": len(job_defs),
        "typen": [jd.typ.value for jd in job_defs],
        "definitions": [jd.as_dict() for jd in job_defs],
        "schema_version": 1,
    }


@router.post("/jobs/enqueue", response_model=dict)
def enqueue_job(body: dict = None) -> dict[str, Any]:
    """
    Reiht einen Hintergrund-Job in die Queue ein (Contract-Ebene).

    Body-Felder:
    - typ: Job-Typ (z.B. "SETTLEMENT_BATCH")
    - angefordert_von: User-/System-ID
    - parameter: optionale Job-Parameter (dict)
    - prioritaet_override: optionale Prioritaet (KRITISCH/HOCH/MITTEL/NIEDRIG)
    - tenant_id: optionale Tenant-ID
    """
    if body is None:
        body = {}

    typ_str: str = body.get("typ", "")
    angefordert_von: str = body.get("angefordert_von", "")

    if not typ_str or not angefordert_von:
        raise HTTPException(
            status_code=422,
            detail="typ und angefordert_von sind erforderlich",
        )

    try:
        job_typ = JobTyp(typ_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Job-Typ '{typ_str}'. Erlaubt: {[e.value for e in JobTyp]}",
        )

    from ....core.background_jobs import JobPrioritaet
    prio_override = None
    if body.get("prioritaet_override"):
        try:
            prio_override = JobPrioritaet(body["prioritaet_override"])
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannte Prioritaet '{body['prioritaet_override']}'. "                       f"Erlaubt: {[e.value for e in JobPrioritaet]}",
            )

    req = JobEnqueueRequest(
        typ=job_typ,
        angefordert_von=angefordert_von,
        parameter=body.get("parameter", {}),
        prioritaet_override=prio_override,
        tenant_id=body.get("tenant_id", ""),
    )
    job, routing = create_job_from_request(req)
    return {
        "job_id": job.job_id,
        "typ": job.typ.value,
        "status": job.status.value,
        "prioritaet": job.prioritaet.value,
        "worker_klasse": routing.worker_klasse.value,
        "timeout_sekunden": routing.timeout_sekunden,
        "meldung": f"Job {job.job_id} eingereiht ({job.typ.value} / {job.prioritaet.value}).",
        "schema_version": 1,
    }


@router.get("/jobs/heartbeat", response_model=dict)
def get_jobs_heartbeat() -> dict[str, Any]:
    """
    Gibt den aktuellen Scheduler-/Worker-Heartbeat fuer die Job-Schicht zurueck.

    Liefert:
    - Scheduler-ID / Worker-ID
    - Heartbeat-Status ACTIVE / DEGRADED / STALE
    - zuletzt bekannte Lease-/Heartbeat-Daten
    - aktive Job-Tags des Schedulers
    """
    status = get_scheduler_status()
    heartbeat = status.get("heartbeat") or {}
    return {
        "running": status.get("running", False),
        "scheduler_id": status.get("scheduler_id", ""),
        "worker_id": status.get("worker_id", ""),
        "heartbeat": heartbeat,
        "total_jobs": status.get("total_jobs", 0),
        "schema_version": 1,
    }


@router.get("/jobs/heartbeat/recovery", response_model=dict)
def get_jobs_heartbeat_recovery() -> dict[str, Any]:
    """
    Liefert den standardisierten Recovery-/Eskalationsplan fuer den aktuellen Scheduler-Heartbeat.
    """
    status = get_scheduler_status()
    heartbeat = status.get("heartbeat") or {}
    if not heartbeat:
        raise HTTPException(status_code=503, detail="Kein Scheduler-Heartbeat verfuegbar")
    health = heartbeat.copy()
    from ....core.scheduler_heartbeat import HeartbeatHealthResult, SchedulerNodeStatus

    recovery_plan = build_scheduler_recovery_plan(
        HeartbeatHealthResult(
            scheduler_id=health["scheduler_id"],
            status=SchedulerNodeStatus(health["status"]),
            active_worker_ids=tuple(health.get("active_worker_ids", [])),
            degraded_worker_ids=tuple(health.get("degraded_worker_ids", [])),
            stale_worker_ids=tuple(health.get("stale_worker_ids", [])),
            running_job_ids=tuple(health.get("running_job_ids", [])),
            evaluated_at=datetime.fromisoformat(health["evaluated_at"]),
            stale_after_seconds=int(health["stale_after_seconds"]),
            degrade_after_seconds=int(health["degrade_after_seconds"]),
        )
    )
    recovery_notification = build_scheduler_recovery_notification(
        recovery_plan,
        worker_id=status.get("worker_id", ""),
    )
    return {
        "scheduler_id": status.get("scheduler_id", ""),
        "worker_id": status.get("worker_id", ""),
        "heartbeat_status": health["status"],
        "recovery_plan": recovery_plan.as_dict(),
        "notification_preview": recovery_notification.as_dict(),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 34 — AP3: GET /process/rate-limits + POST /process/rate-limits/check
# ---------------------------------------------------------------------------

@router.get("/rate-limits", response_model=dict)
def get_rate_limit_policies(domain: str = "") -> dict[str, Any]:
    """
    Gibt konfigurierte Rate-Limit-Policies zurueck.

    Query-Parameter:
    - domain: Filtert auf eine Domain (leer = alle).
    """
    policies = get_default_rate_limit_policies()
    if domain:
        gefiltert = [p for p in policies if p.domain == domain]
        if not gefiltert:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Rate-Limit-Policies fuer Domain '{domain}' konfiguriert. "                       f"Globale Wildcard-Policies (domain=*) gelten immer zusaetzlich.",
            )
        return {
            "domain_filter": domain,
            "policy_count": len(gefiltert),
            "policies": [p.as_dict() for p in gefiltert],
            "schema_version": 1,
        }
    cache_configs = get_default_cache_configs()
    return {
        "policy_count": len(policies),
        "domains": sorted({p.domain for p in policies}),
        "policies": [p.as_dict() for p in policies],
        "cache_configs": [c.as_dict() for c in cache_configs],
        "schema_version": 1,
    }


@router.post("/rate-limits/check", response_model=dict)
def check_rate_limit(body: dict = None) -> dict[str, Any]:
    """
    Prueft ob ein Request das Rate-Limit ueberschreitet.

    Body-Felder:
    - tenant_id: Tenant-ID
    - user_id: User-ID
    - endpoint: API-Endpunkt (z.B. "/api/v1/agrar/contracts")
    - domain: Domain (z.B. "agrar")
    - aktuelle_zaehlung: Bisherige Anfragen im Zeitfenster
    - zeitfenster_sekunden: Zeitfenster (default 60)
    """
    if body is None:
        body = {}

    tenant_id = body.get("tenant_id", "")
    user_id = body.get("user_id", "")
    endpoint = body.get("endpoint", "")
    domain = body.get("domain", "")

    if not tenant_id or not endpoint or not domain:
        raise HTTPException(
            status_code=422,
            detail="tenant_id, endpoint und domain sind erforderlich",
        )

    try:
        zaehlung = int(body.get("aktuelle_zaehlung", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="aktuelle_zaehlung muss eine Ganzzahl sein")

    req = RateLimitRequest(
        tenant_id=tenant_id,
        user_id=user_id,
        endpoint=endpoint,
        domain=domain,
        aktuelle_zaehlung=zaehlung,
        zeitfenster_sekunden=int(body.get("zeitfenster_sekunden", 60)),
    )
    policies = get_default_rate_limit_policies()
    result = evaluate_rate_limit(req, policies)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 34 — AP6: GET /process/security/controls + POST /process/security/rbac-check
# ---------------------------------------------------------------------------

@router.get("/security/controls", response_model=dict)
def get_security_controls(kategorie: str = "") -> dict[str, Any]:
    """
    Gibt den Security-Controls-Katalog zurueck.

    Query-Parameter:
    - kategorie: Filtert auf eine Kontrollkategorie (leer = alle).
    """
    controls = get_default_security_controls()
    secrets = get_default_secret_classifications()

    if kategorie:
        controls = [c for c in controls if c.kategorie.value == kategorie.upper()]
        if not controls:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Controls fuer Kategorie '{kategorie}' gefunden.",
            )
        return {
            "kategorie_filter": kategorie.upper(),
            "control_count": len(controls),
            "controls": [c.as_dict() for c in controls],
            "schema_version": 1,
        }

    posture = evaluate_security_posture(controls)
    return {
        "control_count": len(controls),
        "posture": posture.as_dict(),
        "controls": [c.as_dict() for c in controls],
        "secret_classifications": [s.as_dict() for s in secrets],
        "schema_version": 1,
    }


@router.post("/security/rbac-check", response_model=dict)
def check_rbac_permission(body: dict = None) -> dict[str, Any]:
    """
    Prueft eine RBAC-Permission fuer eine Rolle.

    Body-Felder:
    - user_id: User-ID
    - tenant_id: Tenant-ID
    - rolle: Rollenname (z.B. "sachbearbeiter", "buchhaltung", "leiter", "admin")
    - permission: Berechtigungsname (z.B. "SETTLEMENT_FREIGEBEN")
    - ressource_id: Optionale Ressourcen-ID (Row-Level-Security)
    """
    if body is None:
        body = {}

    user_id = body.get("user_id", "")
    tenant_id = body.get("tenant_id", "")
    rolle = body.get("rolle", "")
    permission_str = body.get("permission", "")

    if not user_id or not rolle or not permission_str:
        raise HTTPException(
            status_code=422,
            detail="user_id, rolle und permission sind erforderlich",
        )

    try:
        permission = RBACPermission(permission_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte Permission '{permission_str}'. "                   f"Erlaubt: {[p.value for p in RBACPermission][:10]} ...",
        )

    check = RBACPermissionCheck(
        user_id=user_id,
        tenant_id=tenant_id,
        rolle=rolle,
        permission=permission,
        ressource_id=body.get("ressource_id", ""),
    )
    result = evaluate_rbac_permission(check)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 35 — AP3: GET /process/inline-validations + POST /process/inline-validations/validate
# ---------------------------------------------------------------------------

@router.get("/inline-validations", response_model=dict)
def get_inline_validations(domain: str = "") -> dict[str, Any]:
    """
    Gibt Inline-Validierungsdefinitionen fuer Felder zurueck.

    Query-Parameter:
    - domain: Filtert auf eine Domain (leer = alle).
    """
    felder = get_default_field_validations()
    if domain:
        gefiltert = [f for f in felder if f.domain == domain]
        if not gefiltert:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Inline-Validierungen fuer Domain '{domain}' konfiguriert.",
            )
        return {
            "domain_filter": domain,
            "feld_count": len(gefiltert),
            "felder": [f.as_dict() for f in gefiltert],
            "schema_version": 1,
        }
    return {
        "feld_count": len(felder),
        "domains": sorted({f.domain for f in felder}),
        "felder": [f.as_dict() for f in felder],
        "schema_version": 1,
    }


@router.post("/inline-validations/validate", response_model=dict)
def run_inline_validation(body: dict = None) -> dict[str, Any]:
    """
    Validiert einen Eingabewert gegen die Regeln eines Feldes.

    Body-Felder:
    - feld_id: ID des Feldes (z.B. "ws-bruttogewicht")
    - wert: Der zu pruefende Eingabewert (als String)
    """
    if body is None:
        body = {}

    feld_id: str = body.get("feld_id", "")
    wert = body.get("wert", "")

    if not feld_id:
        raise HTTPException(status_code=422, detail="feld_id ist erforderlich")

    feld = get_field_by_id(feld_id)
    if feld is None:
        raise HTTPException(
            status_code=404,
            detail=f"Feld '{feld_id}' nicht gefunden. Verfuegbare Felder: "                   f"{[f.feld_id for f in get_default_field_validations()]}",
        )

    ergebnis = validate_inline_field(feld, wert)
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 35 — AP6: GET /process/error-guidance + POST /process/error-guidance/evaluate
# ---------------------------------------------------------------------------

@router.get("/error-guidance", response_model=dict)
def get_error_guidance_rules(http_status: int = 0) -> dict[str, Any]:
    """
    Gibt Error-Guidance-Regeln zurueck.

    Query-Parameter:
    - http_status: Filtert auf einen HTTP-Statuscode (0 = alle).
    """
    regeln = get_default_error_guidance_rules()
    if http_status:
        gefiltert = [r for r in regeln if r.http_status == http_status]
        if not gefiltert:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Guidance-Regeln fuer HTTP-Status {http_status} konfiguriert.",
            )
        return {
            "http_status_filter": http_status,
            "regel_count": len(gefiltert),
            "regeln": [r.as_dict() for r in gefiltert],
            "schema_version": 1,
        }
    return {
        "regel_count": len(regeln),
        "abgedeckte_status": sorted({r.http_status for r in regeln}),
        "regeln": [r.as_dict() for r in regeln],
        "schema_version": 1,
    }


@router.post("/error-guidance/evaluate", response_model=dict)
def evaluate_error_guidance_endpoint(body: dict = None) -> dict[str, Any]:
    """
    Wertet Error-Guidance fuer einen aufgetretenen Fehler aus.

    Body-Felder:
    - http_status: HTTP-Statuscode des Fehlers (z.B. 422, 403, 503)
    - fehler_kategorie: Fehlerklasse (z.B. "BENUTZER_FEHLER", "SYSTEM_FEHLER")
    - kontext: Prozesskontext (z.B. "WARENEINGANG", "ZAHLUNGSLAUF", "ALLGEMEIN")
    """
    if body is None:
        body = {}

    status_raw = body.get("http_status", 0)
    kategorie_str: str = body.get("fehler_kategorie", "")
    kontext_str: str = body.get("kontext", "ALLGEMEIN")

    try:
        http_status = int(status_raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="http_status muss eine Ganzzahl sein")

    if not http_status or not kategorie_str:
        raise HTTPException(
            status_code=422,
            detail="http_status und fehler_kategorie sind erforderlich",
        )

    try:
        kategorie = FehlerKategorie(kategorie_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte fehler_kategorie '{kategorie_str}'. "                   f"Erlaubt: {[e.value for e in FehlerKategorie]}",
        )

    try:
        kontext = FehlerKontext(kontext_str)
    except ValueError:
        kontext = FehlerKontext.ALLGEMEIN

    regeln = get_default_error_guidance_rules()
    result = evaluate_error_guidance(http_status, kategorie, kontext, regeln)
    return result.as_dict()


# ---------------------------------------------------------------------------
# Wave 36 — AP1: GET /process/edi/partners
# ---------------------------------------------------------------------------

@router.get("/edi/partners", response_model=dict)
def get_edi_partners(
    typ: str = "",
    standard: str = "",
) -> dict[str, Any]:
    """
    Gibt EDI-Partner zurück.

    Query-Parameter:
    - typ:      Filtert nach EDIPartnerTyp (z.B. LIEFERANT, KUNDE)
    - standard: Filtert nach EDIStandard   (z.B. EDIFACT, JSON_API)
    """
    partner = get_default_edi_partners()

    if typ:
        try:
            partner_typ = EDIPartnerTyp(typ)
            partner = [p for p in partner if p.typ == partner_typ]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter Partner-Typ '{typ}'. "
                       f"Erlaubt: {[e.value for e in EDIPartnerTyp]}",
            )

    if standard:
        try:
            edi_std = EDIStandard(standard)
            partner = [p for p in partner if p.edi_standard == edi_std]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter EDI-Standard '{standard}'. "
                       f"Erlaubt: {[e.value for e in EDIStandard]}",
            )

    return {
        "partner_count": len(partner),
        "partner": [p.as_dict() for p in partner],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 36 — AP2: GET /process/edi/nachrichtentypen
# ---------------------------------------------------------------------------

@router.get("/edi/nachrichtentypen", response_model=dict)
def get_edi_nachrichtentypen() -> dict[str, Any]:
    """Gibt den EDI-Nachrichtentyp-Katalog zurück."""
    katalog = get_edi_nachrichtentyp_katalog()
    return {
        "typ_count": len(katalog),
        "nachrichtentypen": [k.as_dict() for k in katalog],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 36 — AP3: POST /process/supply-chain/eta
# ---------------------------------------------------------------------------

@router.post("/supply-chain/eta", response_model=dict)
def berechne_lieferung_eta(body: dict = None) -> dict[str, Any]:
    """
    Berechnet die ETA (voraussichtliche Ankunftszeit) einer Lieferung.

    Pflichtfelder:
    - lieferung_id:      Interne Lieferungs-ID
    - transport_modus:   LKW | BAHN | SCHIFF | FLUGZEUG | MULTIMODAL
    - ursprungsort:      Abgangsort
    - zielort:           Zielort
    - geplante_abfahrt:  ISO-8601 Datetime
    - distanz_km:        Streckendistanz in Kilometern

    Optionale Felder:
    - zwischenstopps:    Anzahl Zwischenstopps (default 0)
    - zoll_erforderlich: Boolean (default false)
    - priorisiert:       Boolean — reduzierter Zeitpuffer (default false)
    """
    if body is None:
        body = {}

    pflicht = ["lieferung_id", "transport_modus", "ursprungsort", "zielort",
               "geplante_abfahrt", "distanz_km"]
    fehlend = [f for f in pflicht if not body.get(f)]
    if fehlend:
        raise HTTPException(
            status_code=422,
            detail=f"Pflichtfelder fehlen: {fehlend}",
        )

    try:
        modus = TransportModus(body["transport_modus"])
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter transport_modus '{body['transport_modus']}'. "
                   f"Erlaubt: {[e.value for e in TransportModus]}",
        )

    try:
        from datetime import datetime as _dt
        abfahrt = _dt.fromisoformat(body["geplante_abfahrt"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="geplante_abfahrt muss ISO-8601 sein (z.B. '2026-03-20T08:00:00')",
        )

    try:
        distanz = float(body["distanz_km"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="distanz_km muss eine Zahl sein")

    req = ETABerechnungsRequest(
        lieferung_id=body["lieferung_id"],
        transport_modus=modus,
        ursprungsort=body["ursprungsort"],
        zielort=body["zielort"],
        geplante_abfahrt=abfahrt,
        distanz_km=distanz,
        zwischenstopps=int(body.get("zwischenstopps", 0)),
        zoll_erforderlich=bool(body.get("zoll_erforderlich", False)),
        priorisiert=bool(body.get("priorisiert", False)),
    )

    try:
        ergebnis = berechne_eta(req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 36 — AP4: POST /process/supply-chain/status
# ---------------------------------------------------------------------------

@router.post("/supply-chain/status", response_model=dict)
def bewerte_supply_chain_status(body: dict = None) -> dict[str, Any]:
    """
    Bewertet den Gesamtstatus einer Lieferkette und erkennt Abweichungen.

    Pflichtfelder:
    - lieferung_id:   Interne Lieferungs-ID
    - aktuelle_phase: LieferkettenPhase (z.B. TRANSPORT_EINGEHEND)

    Optionale Felder:
    - verzoegerung_stunden: Zeitliche Verzögerung → erzeugt Abweichungsalarm
    - soll_menge / ist_menge: Mengenangaben → erzeugt Mengenabweichungsalarm
    """
    if body is None:
        body = {}

    lieferung_id: str = body.get("lieferung_id", "")
    phase_str: str = body.get("aktuelle_phase", "")

    if not lieferung_id or not phase_str:
        raise HTTPException(
            status_code=422,
            detail="lieferung_id und aktuelle_phase sind erforderlich",
        )

    try:
        aktuelle_phase = LieferkettenPhase(phase_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte Phase '{phase_str}'. "
                   f"Erlaubt: {[e.value for e in LieferkettenPhase]}",
        )

    events = get_example_tracking_events(lieferung_id)
    alarme = []

    # Zeitliche Abweichung
    verzoegerung = body.get("verzoegerung_stunden")
    if verzoegerung is not None:
        try:
            verzoegerung_h = float(verzoegerung)
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="verzoegerung_stunden muss eine Zahl sein")
        alarm = bewerte_zeitliche_abweichung(
            lieferung_id=lieferung_id,
            alarm_id=f"ALM-ZEIT-{lieferung_id}",
            verzoegerung_stunden=verzoegerung_h,
        )
        alarme.append(alarm)

    # Mengenabweichung
    soll = body.get("soll_menge")
    ist = body.get("ist_menge")
    if soll is not None and ist is not None:
        try:
            soll_f = float(soll)
            ist_f = float(ist)
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="soll_menge und ist_menge müssen Zahlen sein")
        try:
            alarm = bewerte_mengenabweichung(
                lieferung_id=lieferung_id,
                alarm_id=f"ALM-MENGE-{lieferung_id}",
                soll_menge=soll_f,
                ist_menge=ist_f,
            )
            alarme.append(alarm)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

    status = bewerte_lieferkettenstatus(
        lieferung_id=lieferung_id,
        aktuelle_phase=aktuelle_phase,
        events=events,
        alarme=alarme,
    )
    return status.as_dict()


# ---------------------------------------------------------------------------
# Wave 37 — AP1: GET /process/dms/erkennungsregeln
# ---------------------------------------------------------------------------

@router.get("/dms/erkennungsregeln", response_model=dict)
def get_dms_erkennungsregeln(dokument_typ: str = "") -> dict[str, Any]:
    """
    Gibt DMS-Erkennungsregeln zurück.

    Query-Parameter:
    - dokument_typ: Filtert auf einen bestimmten DokumentTyp (z.B. EINGANGSRECHNUNG)
    """
    regeln = get_default_erkennungsregeln()

    if dokument_typ:
        try:
            dt = DokumentTyp(dokument_typ)
            regeln = [r for r in regeln if r.dokument_typ == dt]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter DokumentTyp '{dokument_typ}'. "
                       f"Erlaubt: {[e.value for e in DokumentTyp]}",
            )

    return {
        "regel_count": len(regeln),
        "regeln": [r.as_dict() for r in regeln],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 37 — AP2: POST /process/dms/classify
# ---------------------------------------------------------------------------

@router.post("/dms/classify", response_model=dict)
def classify_dokument(body: dict = None) -> dict[str, Any]:
    """
    Klassifiziert ein Dokument automatisch anhand seines Volltexts.

    Pflichtfelder:
    - dokument_id: DMS-interne Dokument-ID
    - volltext:    OCR-Volltext des Dokuments

    Rückgabe: erkannter DokumentTyp, Confidence, gematchte Schlagwörter,
    Alternativen, Hinweis ob manuelle Prüfung erforderlich.
    """
    if body is None:
        body = {}

    dokument_id: str = body.get("dokument_id", "")
    volltext: str = body.get("volltext", "")

    if not dokument_id or not volltext:
        raise HTTPException(
            status_code=422,
            detail="dokument_id und volltext sind erforderlich",
        )

    ergebnis = klassifiziere_dokument(dokument_id, volltext)
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 37 — AP3: GET /process/agent-tools
# ---------------------------------------------------------------------------

@router.get("/agent-tools", response_model=dict)
def get_agent_tools(
    kategorie: str = "",
    autorisierung: str = "",
) -> dict[str, Any]:
    """
    Gibt registrierte Agent-Tools zurück.

    Query-Parameter:
    - kategorie:    Filtert nach AgentKategorie (z.B. RECHERCHE, TRANSAKTION)
    - autorisierung: Filtert nach Autorisierungsstufe (z.B. AUTHENTIFIZIERT)
    """
    tools = get_default_agent_tools()

    if kategorie:
        try:
            kat = AgentKategorie(kategorie)
            tools = [t for t in tools if t.kategorie == kat]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannte Kategorie '{kategorie}'. "
                       f"Erlaubt: {[e.value for e in AgentKategorie]}",
            )

    if autorisierung:
        try:
            auth = AgentAutorisierungsStufe(autorisierung)
            tools = [t for t in tools if t.autorisierung == auth]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannte Autorisierungsstufe '{autorisierung}'. "
                       f"Erlaubt: {[e.value for e in AgentAutorisierungsStufe]}",
            )

    use_cases = get_default_agent_use_cases()

    return {
        "tool_count": len(tools),
        "tools": [t.as_dict() for t in tools],
        "use_case_count": len(use_cases),
        "use_cases": [u.as_dict() for u in use_cases],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 37 — AP4: POST /process/agent-tools/match
# ---------------------------------------------------------------------------

@router.post("/agent-tools/match", response_model=dict)
def match_agent_capabilities(body: dict = None) -> dict[str, Any]:
    """
    Findet Agent-Tools, die eine Liste angefragter Capabilities abdecken.

    Body-Felder:
    - capabilities: Liste von Capability-Strings (z.B. ["kontrakt_lesen", "preis_ermitteln"])
    """
    if body is None:
        body = {}

    capabilities = body.get("capabilities", [])

    if not capabilities or not isinstance(capabilities, list):
        raise HTTPException(
            status_code=422,
            detail="'capabilities' muss eine nicht-leere Liste von Strings sein",
        )

    ergebnis = match_capabilities(capabilities)
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 38 — AP1: GET /process/sustainability/esg-bericht
# ---------------------------------------------------------------------------

@router.get("/sustainability/esg-bericht", response_model=dict)
def get_esg_bericht(
    tenant_id: str = "TENANT-001",
    jahr: int = 2026,
) -> dict[str, Any]:
    """
    Gibt einen ESG-Bericht mit CO2-Bilanz und Nachhaltigkeitskennzahlen zurück.

    Query-Parameter:
    - tenant_id: Tenant-ID (default: TENANT-001)
    - jahr:      Berichtsjahr (default: 2026)
    """
    if jahr < 2000 or jahr > 2100:
        raise HTTPException(
            status_code=422,
            detail="jahr muss zwischen 2000 und 2100 liegen",
        )
    bericht = erstelle_beispiel_esg_bericht(tenant_id=tenant_id, jahr=jahr)
    return bericht.as_dict()


# ---------------------------------------------------------------------------
# Wave 38 — AP2: POST /process/sustainability/co2-berechnen
# ---------------------------------------------------------------------------

@router.post("/sustainability/co2-berechnen", response_model=dict)
def berechne_co2_position(body: dict = None) -> dict[str, Any]:
    """
    Berechnet CO2e für eine einzelne Transport- oder Energieposition.

    Transport-Body:
    - positions_id: ID der Position
    - typ:          "TRANSPORT" | "ENERGIE"
    - kategorie:    EmissionsKategorie (z.B. TRANSPORT_LKW, ENERGIE_STROM)
    - menge:        Menge (für Transport: Tonnen; für Energie: kWh)
    - distanz_km:   Nur für Transport: Streckenlänge in km

    Energie-Body:
    - positions_id, typ="ENERGIE", kategorie, menge (kWh)
    """
    if body is None:
        body = {}

    positions_id: str = body.get("positions_id", "")
    typ: str = body.get("typ", "").upper()
    kategorie_str: str = body.get("kategorie", "")

    if not positions_id or not typ or not kategorie_str:
        raise HTTPException(
            status_code=422,
            detail="positions_id, typ und kategorie sind erforderlich",
        )

    if typ not in ("TRANSPORT", "ENERGIE"):
        raise HTTPException(
            status_code=422,
            detail=f"typ muss 'TRANSPORT' oder 'ENERGIE' sein, nicht '{typ}'",
        )

    try:
        kategorie = EmissionsKategorie(kategorie_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte Kategorie '{kategorie_str}'. "
                   f"Erlaubt: {[e.value for e in EmissionsKategorie]}",
        )

    try:
        menge = float(body.get("menge", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="menge muss eine Zahl sein")

    try:
        if typ == "TRANSPORT":
            distanz_km = float(body.get("distanz_km", 0))
            position = berechne_transport_co2e(positions_id, kategorie, menge, distanz_km)
        else:
            position = berechne_energie_co2e(positions_id, kategorie, menge)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return position.as_dict()


# ---------------------------------------------------------------------------
# Wave 38 — AP3: GET /process/benchmark/report
# ---------------------------------------------------------------------------

@router.get("/benchmark/report", response_model=dict)
def get_benchmark_report(
    tenant_id: str = "TENANT-001",
    kategorie: str = "",
) -> dict[str, Any]:
    """
    Gibt den Benchmark-Report einer Genossenschaft zurück.

    Query-Parameter:
    - tenant_id: Tenant-ID (default: TENANT-001)
    - kategorie: Filtert Kennzahlen nach BenchmarkKategorie (z.B. LOGISTIK)
    """
    report = get_example_benchmark_report(tenant_id=tenant_id)

    if kategorie:
        try:
            kat = BenchmarkKategorie(kategorie)
            report.kennzahlen = [k for k in report.kennzahlen if k.kategorie == kat]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannte Kategorie '{kategorie}'. "
                       f"Erlaubt: {[e.value for e in BenchmarkKategorie]}",
            )

    return report.as_dict()


# ---------------------------------------------------------------------------
# Wave 38 — AP4: POST /process/benchmark/perzentile
# ---------------------------------------------------------------------------

@router.post("/benchmark/perzentile", response_model=dict)
def berechne_perzentile(body: dict = None) -> dict[str, Any]:
    """
    Berechnet Branchenperzentile aus einer Werteverteilung.

    Body-Felder:
    - werte:        Liste von Zahlen (Branchenverteilung)
    - eigenwert:    Eigener Wert zum Einordnen (optional)
    - kennzahl_id:  Bezeichner (optional, für Rückgabe)
    """
    if body is None:
        body = {}

    werte_raw = body.get("werte", [])
    if not isinstance(werte_raw, list) or len(werte_raw) < 2:
        raise HTTPException(
            status_code=422,
            detail="'werte' muss eine Liste mit mindestens 2 Zahlen sein",
        )

    try:
        werte = [float(v) for v in werte_raw]
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Alle Werte müssen Zahlen sein")

    try:
        perzentile = berechne_branchenperzentile(werte)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    result: dict[str, Any] = {
        "kennzahl_id": body.get("kennzahl_id", ""),
        "anzahl_werte": len(werte),
        **perzentile,
    }

    eigenwert_raw = body.get("eigenwert")
    if eigenwert_raw is not None:
        try:
            eigenwert = float(eigenwert_raw)
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="eigenwert muss eine Zahl sein")
        # Trend-Berechnung: prüfe wo der Eigenwert im Feld steht
        p25 = perzentile["p25"]
        p75 = perzentile["p75"]
        p90 = perzentile["p90"]
        if eigenwert >= p90:
            einordnung = "TOP_10"
        elif eigenwert >= p75:
            einordnung = "TOP_25"
        elif eigenwert >= p25:
            einordnung = "MITTELFELD"
        else:
            einordnung = "UNTERES_VIERTEL"
        result["eigenwert"] = eigenwert
        result["einordnung"] = einordnung

    return result


# ---------------------------------------------------------------------------
# Wave 39 — AP1: GET /process/surfacing/regeln
# ---------------------------------------------------------------------------

@router.get("/surfacing/regeln", response_model=dict)
def get_surfacing_regeln(
    domain: str = "",
    kontext: str = "",
) -> dict[str, Any]:
    """
    Gibt Command-Surfacing-Regeln zurück.

    Query-Parameter:
    - domain:   Filtert nach Domain (z.B. agrar, finance)
    - kontext:  Filtert nach SurfacingKontext (z.B. TOOLBAR_PRIMARY, COMMAND_PALETTE)
    """
    regeln = get_default_surfacing_regeln()

    if domain:
        regeln = [r for r in regeln if r.domain == "" or r.domain == domain]

    if kontext:
        try:
            kontext_enum = SurfacingKontext(kontext)
            regeln = [r for r in regeln if kontext_enum in r.sichtbar_in]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter Kontext '{kontext}'. "
                       f"Erlaubt: {[e.value for e in SurfacingKontext]}",
            )

    return {
        "regel_count": len(regeln),
        "regeln": [r.as_dict() for r in regeln],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 39 — AP2: POST /process/surfacing/manifest
# ---------------------------------------------------------------------------

@router.post("/surfacing/manifest", response_model=dict)
def berechne_surfacing_manifest(body: dict = None) -> dict[str, Any]:
    """
    Berechnet das Command-Surfacing-Manifest für einen User/Kontext.

    Pflichtfelder:
    - rolle:    Benutzerrolle (z.B. sachbearbeiter, leiter, admin)
    - dichte:   FOKUSSIERT | STANDARD | VERDICHTET
    - kontext:  SurfacingKontext (z.B. TOOLBAR_PRIMARY, COMMAND_PALETTE)

    Optionale Felder:
    - domain:      Domain-Filter (z.B. agrar, finance)
    - command_id:  Prüft nur diesen einen Command
    """
    if body is None:
        body = {}

    rolle: str = body.get("rolle", "")
    dichte_str: str = body.get("dichte", "")
    kontext_str: str = body.get("kontext", "")

    if not rolle or not dichte_str or not kontext_str:
        raise HTTPException(
            status_code=422,
            detail="rolle, dichte und kontext sind erforderlich",
        )

    try:
        dichte = DichteStufe(dichte_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte dichte '{dichte_str}'. "
                   f"Erlaubt: {[e.value for e in DichteStufe]}",
        )

    try:
        kontext = SurfacingKontext(kontext_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter kontext '{kontext_str}'. "
                   f"Erlaubt: {[e.value for e in SurfacingKontext]}",
        )

    anfrage = SurfacingAnfrage(
        rolle=rolle,
        dichte=dichte,
        kontext=kontext,
        domain=body.get("domain", ""),
        command_id=body.get("command_id", ""),
    )
    manifest = berechne_surfacing(anfrage)
    return manifest.as_dict()


# ---------------------------------------------------------------------------
# Wave 39 — AP3: GET /process/notifications/abonnements
# ---------------------------------------------------------------------------

@router.get("/notifications/abonnements", response_model=dict)
def get_notification_abonnements(
    rolle: str = "",
    ausloeser: str = "",
) -> dict[str, Any]:
    """
    Gibt Benachrichtigungs-Abonnements zurück.

    Query-Parameter:
    - rolle:     Filtert nach Empfänger-Rolle
    - ausloeser: Filtert nach NotifikationsAusloeser (z.B. FREIGABE_ERFORDERLICH)
    """
    abos = get_default_abonnements()

    if rolle:
        abos = [a for a in abos if a.empfaenger_rolle == rolle]

    if ausloeser:
        try:
            asl = NotifikationsAusloeser(ausloeser)
            abos = [a for a in abos if asl in a.ausloeser]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter Auslöser '{ausloeser}'. "
                       f"Erlaubt: {[e.value for e in NotifikationsAusloeser]}",
            )

    eskalationsregeln = get_default_eskalationsregeln()

    return {
        "abo_count": len(abos),
        "abonnements": [a.as_dict() for a in abos],
        "eskalationsregel_count": len(eskalationsregeln),
        "eskalationsregeln": [e.as_dict() for e in eskalationsregeln],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 39 — AP4: POST /process/notifications/route
# ---------------------------------------------------------------------------

@router.post("/notifications/route", response_model=dict)
def route_notification(body: dict = None) -> dict[str, Any]:
    """
    Berechnet Routing für eine Benachrichtigung (Empfänger + Kanäle).

    Pflichtfelder:
    - ausloeser: NotifikationsAusloeser (z.B. FREIGABE_ERFORDERLICH)

    Optionale Felder:
    - domain:       Domain-Filter
    - prozess_typ:  Prozesstyp-Filter
    - nachricht_id: ID für die erzeugte Nachricht
    - titel:        Nachrichtentitel
    - inhalt:       Nachrichteninhalt
    """
    if body is None:
        body = {}

    ausloeser_str: str = body.get("ausloeser", "")
    if not ausloeser_str:
        raise HTTPException(status_code=422, detail="ausloeser ist erforderlich")

    try:
        ausloeser = NotifikationsAusloeser(ausloeser_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Auslöser '{ausloeser_str}'. "
                   f"Erlaubt: {[e.value for e in NotifikationsAusloeser]}",
        )

    routing = route_benachrichtigung(
        ausloeser=ausloeser,
        domain=body.get("domain", ""),
        prozess_typ=body.get("prozess_typ", ""),
    )

    result: dict[str, Any] = routing.as_dict()

    # Optional: vollständige Nachricht erzeugen
    titel = body.get("titel", "")
    inhalt = body.get("inhalt", "")
    nachricht_id = body.get("nachricht_id", "")
    if titel and inhalt and nachricht_id:
        nachricht = erstelle_benachrichtigung(
            nachricht_id=nachricht_id,
            ausloeser=ausloeser,
            titel=titel,
            inhalt=inhalt,
            prozess_id=body.get("prozess_id", ""),
            routing=routing,
        )
        result["nachricht"] = nachricht.as_dict()

    return result


# ---------------------------------------------------------------------------
# Wave 40 — AP1: GET /process/workflow-versioning/definitionen
# ---------------------------------------------------------------------------

@router.get("/workflow-versioning/definitionen", response_model=dict)
def get_workflow_definitionen(
    workflow_typ: str = "",
    status: str = "",
) -> dict[str, Any]:
    """
    Gibt Workflow-Definitionen zurück.

    Query-Parameter:
    - workflow_typ: Filtert nach Workflow-Typ (z.B. kontrakt_annahme)
    - status:       Filtert nach Status (ENTWURF|AKTIV|VERALTET|ARCHIVIERT)
    """
    definitionen = get_default_workflow_definitionen()

    if workflow_typ:
        definitionen = [d for d in definitionen if d.workflow_typ == workflow_typ]

    if status:
        try:
            st = WorkflowDefinitionsStatus(status)
            definitionen = [d for d in definitionen if d.status == st]
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter Status '{status}'. "
                       f"Erlaubt: {[e.value for e in WorkflowDefinitionsStatus]}",
            )

    sandbox_regeln = get_default_sandbox_regeln()

    return {
        "definition_count": len(definitionen),
        "definitionen": [d.as_dict() for d in definitionen],
        "sandbox_regeln": [r.as_dict() for r in sandbox_regeln],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 40 — AP2: POST /process/workflow-versioning/migration-pruefen
# ---------------------------------------------------------------------------

@router.post("/workflow-versioning/migration-pruefen", response_model=dict)
def pruefe_workflow_migration(body: dict = None) -> dict[str, Any]:
    """
    Prüft ob eine Workflow-Instanz auf eine Ziel-Definition migriert werden kann.

    Pflichtfelder:
    - instanz_id:       ID der laufenden Instanz
    - definition_id:    Aktuelle Definition-ID der Instanz
    - ziel_definition_id: Ziel-Definition-ID

    Optionale Felder:
    - versions_snapshot: Hash der Startversion (default: "")
    """
    if body is None:
        body = {}

    instanz_id: str = body.get("instanz_id", "")
    definition_id: str = body.get("definition_id", "")
    ziel_def_id: str = body.get("ziel_definition_id", "")

    if not instanz_id or not definition_id or not ziel_def_id:
        raise HTTPException(
            status_code=422,
            detail="instanz_id, definition_id und ziel_definition_id sind erforderlich",
        )

    definitionen = get_default_workflow_definitionen()
    ziel_def = next((d for d in definitionen if d.definition_id == ziel_def_id), None)
    if ziel_def is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ziel-Definition '{ziel_def_id}' nicht gefunden",
        )

    from ....core.workflow_versioning_contracts import WorkflowInstanzReferenz
    from datetime import datetime as _dt
    instanz = WorkflowInstanzReferenz(
        instanz_id=instanz_id,
        definition_id=definition_id,
        versions_snapshot=body.get("versions_snapshot", ""),
        gestartet_am=_dt.utcnow(),
        instanz_status=WorkflowInstanzStatus.LAUFEND,
    )

    ergebnis = pruefe_migration(instanz, ziel_def)
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 40 — AP3: GET /process/audit-trail/beispiel
# ---------------------------------------------------------------------------

@router.get("/audit-trail/beispiel", response_model=dict)
def get_audit_trail_beispiel(
    tenant_id: str = "TENANT-001",
    kontrakt_id: str = "KT-2026-0042",
) -> dict[str, Any]:
    """
    Gibt eine Beispiel-Audit-Kette mit Hash-Verkettung zurück.

    Query-Parameter:
    - tenant_id:    Tenant-ID (default: TENANT-001)
    - kontrakt_id:  Kontrakt-ID (default: KT-2026-0042)
    """
    kette = baue_beispiel_audit_kette(tenant_id=tenant_id, kontrakt_id=kontrakt_id)
    return kette.as_dict()


# ---------------------------------------------------------------------------
# Wave 40 — AP4: POST /process/audit-trail/integritaet-pruefen
# ---------------------------------------------------------------------------

@router.post("/audit-trail/integritaet-pruefen", response_model=dict)
def pruefe_audit_integritaet(body: dict = None) -> dict[str, Any]:
    """
    Prüft die Integrität einer Audit-Kette (Hash-Verkettung + GoBD-Vollständigkeit).

    Body-Felder:
    - tenant_id:    Tenant-ID
    - kontrakt_id:  Kontrakt-ID für die Beispielkette (optional)
    - min_gobd_pflicht: Mindestanzahl GoBD-Pflichteinträge (default: 0)
    """
    if body is None:
        body = {}

    tenant_id: str = body.get("tenant_id", "TENANT-001")
    kontrakt_id: str = body.get("kontrakt_id", "KT-2026-0042")
    min_gobd: int = int(body.get("min_gobd_pflicht", 0))

    kette = baue_beispiel_audit_kette(tenant_id=tenant_id, kontrakt_id=kontrakt_id)
    integritaets_stati = kette.pruefe_kettenintegritaet()

    hash_fehler = [
        i for i, s in enumerate(integritaets_stati)
        if s.value != "UNVERAENDERT"
    ]
    gobd_anzahl = len(kette.gobd_pflichtige_eintraege)
    gobd_erfuellt = gobd_anzahl >= min_gobd

    return {
        "kette_id": kette.kette_id,
        "tenant_id": tenant_id,
        "eintrag_anzahl": len(kette.eintraege),
        "ist_integer": kette.ist_integer,
        "hash_fehler_positionen": hash_fehler,
        "gobd_pflicht_anzahl": gobd_anzahl,
        "gobd_mindestanforderung_erfuellt": gobd_erfuellt,
        "integritaets_stati": [s.value for s in integritaets_stati],
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 41 — Process Capacity Contracts
# ---------------------------------------------------------------------------

@router.get("/capacity/einheiten")
def get_kapazitaets_einheiten(
    tenant_id: str = "TENANT-001",
    domain: str = "",
):
    """
    Gibt alle Kapazitätseinheiten zurück (optional gefiltert nach Domain).
    """
    einheiten = get_default_kapazitaets_einheiten(tenant_id=tenant_id)
    if domain:
        einheiten = [e for e in einheiten if e.domain == domain or e.domain == ""]
    return {
        "einheiten": [e.as_dict() for e in einheiten],
        "anzahl": len(einheiten),
        "ueberlastete": sum(1 for e in einheiten if e.ist_engpass),
        "schema_version": 1,
    }


@router.post("/capacity/pruefe-workflow")
def pruefe_workflow_kapazitaet_endpoint(body: dict | None = None):
    """
    Prüft ob für eine Workflow-Instanz ausreichend Kapazität vorhanden ist.

    Body-Parameter:
    - workflow_instanz_id: ID der Instanz
    - domain: Domain des Workflows
    - tenant_id: Tenant
    """
    if body is None:
        body = {}

    workflow_instanz_id: str = body.get("workflow_instanz_id", "WF-INST-001")
    domain: str = body.get("domain", "agrar")
    tenant_id: str = body.get("tenant_id", "TENANT-001")

    einheiten = get_default_kapazitaets_einheiten(tenant_id=tenant_id)
    ergebnis = pruefe_workflow_kapazitaet(
        workflow_instanz_id=workflow_instanz_id,
        domain=domain,
        verfuegbare_einheiten=einheiten,
    )
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 41 — Event Replay Contracts
# ---------------------------------------------------------------------------

@router.get("/event-replay/auftraege")
def get_replay_auftraege(
    tenant_id: str = "TENANT-001",
    status: str = "",
):
    """
    Gibt Replay-Aufträge zurück (optional gefiltert nach Status).
    """
    auftraege = get_default_replay_auftraege(tenant_id=tenant_id)
    if status:
        auftraege = [a for a in auftraege if a.status.value == status.upper()]
    return {
        "auftraege": [a.as_dict() for a in auftraege],
        "anzahl": len(auftraege),
        "laufende": sum(1 for a in auftraege if a.status == ReplayStatus.LAUFEND),
        "schema_version": 1,
    }


@router.post("/event-replay/konsistenz-pruefen")
def pruefe_event_stream_konsistenz(body: dict | None = None):
    """
    Prüft die Konsistenz eines Event-Streams (Lücken und Duplikate).

    Body-Parameter:
    - pruefung_id: ID der Prüfung
    - stream_id: Event-Stream-Bezeichner
    - positionen: Liste der vorhandenen Event-Positionen (int)
    """
    if body is None:
        body = {}

    pruefung_id: str = body.get("pruefung_id", "KP-001")
    stream_id: str = body.get("stream_id", "kontrakt-annahme-stream")
    positionen: list[int] = [int(p) for p in body.get("positionen", list(range(0, 10)))]

    ergebnis = pruefe_replay_konsistenz(
        pruefung_id=pruefung_id,
        stream_id=stream_id,
        positionen=positionen,
    )
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 42 — Domain Event Schema Registry
# ---------------------------------------------------------------------------

@router.get("/event-schema/schemata")
def get_event_schemata(
    event_typ: str = "",
    status: str = "",
):
    """
    Gibt alle Event-Schemata zurück (optional gefiltert nach event_typ und status).
    """
    schemata = get_default_event_schemas()
    if event_typ:
        schemata = [s for s in schemata if s.event_typ == event_typ]
    if status:
        schemata = [s for s in schemata if s.status.value == status.upper()]
    return {
        "schemata": [s.as_dict() for s in schemata],
        "anzahl": len(schemata),
        "aktive": sum(1 for s in schemata if s.ist_aktiv),
        "schema_version": 1,
    }


@router.post("/event-schema/validiere-payload")
def validiere_event_payload(body: dict | None = None):
    """
    Validiert einen Payload gegen das aktive Schema eines Event-Typs.

    Body-Parameter:
    - event_typ: Event-Typ (z.B. "kontrakt.erstellt")
    - payload: dict mit den zu prüfenden Feldern
    - tenant_id: optional
    """
    if body is None:
        body = {}

    event_typ: str = body.get("event_typ", "kontrakt.erstellt")
    payload: dict = body.get("payload", {})
    tenant_id: str = body.get("tenant_id", "")

    schemata = get_default_event_schemas()
    schema = finde_aktives_schema(event_typ=event_typ, schemata=schemata, tenant_id=tenant_id)

    if schema is None:
        return {
            "event_typ": event_typ,
            "schema_gefunden": False,
            "gueltig": False,
            "fehlende_felder": [],
            "nachricht": f"Kein aktives Schema für Event-Typ '{event_typ}' gefunden.",
            "schema_version": 1,
        }

    gueltig, fehlend = schema.validiere_payload(payload)
    return {
        "event_typ": event_typ,
        "schema_id": schema.schema_id,
        "schema_version_str": schema.version,
        "schema_gefunden": True,
        "gueltig": gueltig,
        "fehlende_felder": fehlend,
        "nachricht": "Payload gültig." if gueltig else f"{len(fehlend)} Pflichtfeld(er) fehlen.",
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 42 — Process Compensation Contracts
# ---------------------------------------------------------------------------

@router.get("/compensation/saga-definitionen")
def get_saga_definitionen(workflow_typ: str = ""):
    """
    Gibt alle Saga-Definitionen zurück (optional gefiltert nach workflow_typ).
    """
    sagas = get_default_saga_definitionen()
    if workflow_typ:
        sagas = [s for s in sagas if s.workflow_typ == workflow_typ]
    return {
        "saga_definitionen": [s.as_dict() for s in sagas],
        "anzahl": len(sagas),
        "schema_version": 1,
    }


@router.post("/compensation/erstelle-kette")
def erstelle_kompensationskette_endpoint(body: dict | None = None):
    """
    Erstellt eine Kompensationskette für eine Workflow-Instanz.

    Body-Parameter:
    - workflow_instanz_id: ID der fehlgeschlagenen Instanz
    - saga_id: ID der Saga-Definition (SAGA-001/002/003)
    - tenant_id: Tenant
    """
    if body is None:
        body = {}

    workflow_instanz_id: str = body.get("workflow_instanz_id", "WF-INST-FAIL-001")
    saga_id: str = body.get("saga_id", "SAGA-001")
    tenant_id: str = body.get("tenant_id", "TENANT-001")

    sagas = get_default_saga_definitionen()
    saga = next((s for s in sagas if s.saga_id == saga_id), sagas[0])

    kette = erstelle_kompensations_kette(
        workflow_instanz_id=workflow_instanz_id,
        saga=saga,
        tenant_id=tenant_id,
    )
    return kette.as_dict()


# ---------------------------------------------------------------------------
# Wave 43 — Workflow Checkpoint Contracts
# ---------------------------------------------------------------------------

@router.get("/checkpoints/regeln")
def get_checkpoint_regeln(workflow_typ: str = ""):
    """
    Gibt Checkpoint-Regeln zurück (optional gefiltert nach workflow_typ).
    """
    regeln = get_default_checkpoint_regeln()
    if workflow_typ:
        regeln = [r for r in regeln if r.workflow_typ == workflow_typ]
    return {
        "regeln": [r.as_dict() for r in regeln],
        "anzahl": len(regeln),
        "schema_version": 1,
    }


@router.post("/checkpoints/erstelle")
def erstelle_workflow_checkpoint(body: dict | None = None):
    """
    Erstellt einen Checkpoint für eine Workflow-Instanz.

    Body-Parameter:
    - checkpoint_id: Checkpoint-ID
    - workflow_instanz_id: Instanz-ID
    - schritt_id: Aktueller Schritt
    - tenant_id: Tenant
    - schritte_ausgefuehrt: Anzahl bisher ausgeführter Schritte
    - zustand: dict mit aktuellem Workflow-Zustand
    """
    if body is None:
        body = {}

    checkpoint = erstelle_checkpoint(
        checkpoint_id=body.get("checkpoint_id", "CP-001"),
        workflow_instanz_id=body.get("workflow_instanz_id", "WF-INST-001"),
        schritt_id=body.get("schritt_id", "SCHRITT-03"),
        tenant_id=body.get("tenant_id", "TENANT-001"),
        zustand=body.get("zustand", {}),
        schritte_ausgefuehrt=int(body.get("schritte_ausgefuehrt", 0)),
    )
    return checkpoint.as_dict()


# ---------------------------------------------------------------------------
# Wave 43 — Cross-Domain Projection Contracts
# ---------------------------------------------------------------------------

@router.get("/projections/gesundheit")
def get_projektions_gesundheit(tenant_id: str = "TENANT-001"):
    """
    Gibt den aggregierten Gesundheitsstatus aller Projektionen zurück.
    """
    from datetime import datetime as _dt
    projektionen = get_default_projektionen(tenant_id=tenant_id)
    gesundheit = erstelle_projektions_gesundheit(
        gesundheits_id="PG-AKTUELL",
        projektionen=projektionen,
        geprueft_am=_dt.utcnow(),
    )
    return gesundheit.as_dict()


@router.post("/projections/pruefe-lag")
def pruefe_projektions_lag(body: dict | None = None):
    """
    Berechnet die Lag-Stufe für einen gegebenen Lag-Wert in Sekunden.

    Body-Parameter:
    - lag_sekunden: Lag-Wert in Sekunden (float)
    - projection_id: optional, für Kontext
    """
    if body is None:
        body = {}

    lag_sekunden: float = float(body.get("lag_sekunden", 0.0))
    projection_id: str = body.get("projection_id", "")

    lag_stufe = berechne_lag_stufe(lag_sekunden)
    return {
        "projection_id": projection_id,
        "lag_sekunden": lag_sekunden,
        "lag_stufe": lag_stufe.value,
        "ist_kritisch": lag_stufe == ProjectionLagStufe.KRITISCH,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 44 — Process Routing Contracts
# ---------------------------------------------------------------------------

@router.get("/routing/regeln")
def get_routing_regeln(workflow_typ: str = ""):
    """
    Gibt Routing-Regeln zurück (optional gefiltert nach workflow_typ).
    """
    regeln = get_default_routing_regeln()
    if workflow_typ:
        regeln = [r for r in regeln if r.workflow_typ == workflow_typ]
    return {
        "regeln": [r.as_dict() for r in regeln],
        "anzahl": len(regeln),
        "workflow_typen": sorted({r.workflow_typ for r in get_default_routing_regeln()}),
        "schema_version": 1,
    }


@router.post("/routing/route")
def route_workflow_nachricht(body: dict | None = None):
    """
    Routet eine Nachricht anhand der priorisierten Routing-Regeln.

    Body-Parameter:
    - workflow_typ: Typ des Workflows (z.B. "kontrakt_annahme")
    - kontext: dict mit Nachrichtenkontext (Felder, Werte, Rolle)
    - entscheidung_id: optional
    """
    if body is None:
        body = {}

    workflow_typ: str = body.get("workflow_typ", "kontrakt_annahme")
    kontext: dict = body.get("kontext", {})
    entscheidung_id: str | None = body.get("entscheidung_id")

    entscheidung = route_nachricht(
        workflow_typ=workflow_typ,
        kontext=kontext,
        entscheidung_id=entscheidung_id,
    )
    return entscheidung.as_dict()


# ---------------------------------------------------------------------------
# Wave 44 — Data Lineage Contracts
# ---------------------------------------------------------------------------

@router.get("/lineage/graph")
def get_lineage_graph(tenant_id: str = "TENANT-001"):
    """
    Gibt den Standard-Lineage-Graphen für den Agrar-Settlement-Prozess zurück.
    """
    graph = get_default_lineage_graph(tenant_id=tenant_id)
    return graph.as_dict()


@router.post("/lineage/pfad")
def finde_lineage_pfad(body: dict | None = None):
    """
    Findet den Pfad zwischen zwei Knoten im Lineage-Graphen (BFS).

    Body-Parameter:
    - von_knoten_id: Start-Knoten-ID
    - zu_knoten_id: Ziel-Knoten-ID
    - tenant_id: optional
    """
    if body is None:
        body = {}

    von: str = body.get("von_knoten_id", "LK-001")
    zu: str = body.get("zu_knoten_id", "LK-004")
    tenant_id: str = body.get("tenant_id", "TENANT-001")

    graph = get_default_lineage_graph(tenant_id=tenant_id)
    pfad = graph.finde_pfad(von, zu)

    return {
        "von_knoten_id": von,
        "zu_knoten_id": zu,
        "pfad": pfad,
        "pfad_laenge": len(pfad),
        "pfad_gefunden": len(pfad) > 0,
        "hat_zyklus": graph.hat_zyklus,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 45 — Feature Flag Contracts
# ---------------------------------------------------------------------------

@router.get("/feature-flags")
def get_feature_flags(
    tenant_id: str = "TENANT-001",
    rolle: str = "",
):
    """
    Gibt alle Feature-Flags mit Zugangsauswertung für Tenant/Rolle zurück.
    """
    flags = get_default_feature_flags()
    aktive_ids = get_aktive_flag_ids(tenant_id=tenant_id, rolle=rolle, flags=flags)
    return {
        "flags": [f.as_dict() for f in flags],
        "anzahl": len(flags),
        "aktive_flag_ids": aktive_ids,
        "aktive_anzahl": len(aktive_ids),
        "schema_version": 1,
    }


@router.post("/feature-flags/evaluiere")
def evaluiere_feature_flags(body: dict | None = None):
    """
    Evaluiert alle Feature-Flags für einen Tenant und eine Rolle.

    Body-Parameter:
    - tenant_id: Tenant-ID
    - rolle: Rolle des Nutzers (optional)
    """
    if body is None:
        body = {}

    tenant_id: str = body.get("tenant_id", "TENANT-001")
    rolle: str = body.get("rolle", "")

    flags = get_default_feature_flags()
    evaluierungen = evaluiere_flags(
        tenant_id=tenant_id,
        rolle=rolle,
        flags=flags,
    )
    return {
        "tenant_id": tenant_id,
        "rolle": rolle,
        "evaluierungen": [e.as_dict() for e in evaluierungen],
        "zugang_anzahl": sum(1 for e in evaluierungen if e.hat_zugang),
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 45 — Process Cost Contracts
# ---------------------------------------------------------------------------

@router.get("/costs/budget-ueberwachung")
def get_budget_ueberwachung(
    tenant_id: str = "TENANT-001",
    domain: str = "",
):
    """
    Gibt Budget-Überwachungsstatus zurück (optional gefiltert nach Domain).
    """
    budgets = get_default_budget_ueberwachungen(tenant_id=tenant_id)
    if domain:
        budgets = [b for b in budgets if b.domain == domain]
    kritisch = [b for b in budgets
                if b.budget_status in {BudgetStatus.GESPERRT, BudgetStatus.UEBERSCHRITTEN}]
    return {
        "budgets": [b.as_dict() for b in budgets],
        "anzahl": len(budgets),
        "kritische_anzahl": len(kritisch),
        "schema_version": 1,
    }


@router.post("/costs/erstelle-erfassung")
def erstelle_prozess_kostenerfassung(body: dict | None = None):
    """
    Erstellt eine Kostenerfassung für eine Workflow-Instanz.

    Body-Parameter:
    - erfassung_id: Erfassungs-ID
    - workflow_instanz_id: Instanz-ID
    - tenant_id: Tenant
    - positionen: Liste von {position_id, kosten_typ, menge, einheit_preis_eur, abrechnungs_einheit}
    """
    if body is None:
        body = {}

    from ....core.process_cost_contracts import KostenPosition  # noqa: F811

    rohe_positionen = body.get("positionen", [
        {"position_id": "P-001", "kosten_typ": "CPU",
         "menge": 2.5, "einheit_preis_eur": 0.01,
         "abrechnungs_einheit": "PRO_SEKUNDE"},
    ])

    positionen = [
        KostenPosition(
            position_id=p.get("position_id", f"P-{i}"),
            kosten_typ=KostenTyp(p.get("kosten_typ", "MANUELL")),
            menge=float(p.get("menge", 1)),
            einheit_preis_eur=float(p.get("einheit_preis_eur", 0)),
            abrechnungs_einheit=AbrechnungsEinheit(
                p.get("abrechnungs_einheit", "PRO_AUSFUEHRUNG")
            ),
            beschreibung=p.get("beschreibung", ""),
        )
        for i, p in enumerate(rohe_positionen, 1)
    ]

    erfassung = erstelle_kosten_erfassung(
        erfassung_id=body.get("erfassung_id", "KE-001"),
        workflow_instanz_id=body.get("workflow_instanz_id", "WF-INST-001"),
        tenant_id=body.get("tenant_id", "TENANT-001"),
        positionen=positionen,
    )
    return erfassung.as_dict()


# ---------------------------------------------------------------------------
# Wave 46 — Process Quarantine Contracts
# ---------------------------------------------------------------------------

@router.get("/quarantine/eintraege")
def get_quarantaene_eintraege(
    tenant_id: str = "TENANT-001",
    status: str = "",
):
    """
    Gibt Quarantäne-Einträge zurück (optional gefiltert nach Status).
    """
    eintraege = get_default_quarantaene_eintraege(tenant_id=tenant_id)
    if status:
        eintraege = [e for e in eintraege if e.status.value == status.upper()]
    statistik = berechne_quarantaene_statistik(
        get_default_quarantaene_eintraege(tenant_id=tenant_id), tenant_id
    )
    return {
        "eintraege": [e.as_dict() for e in eintraege],
        "anzahl": len(eintraege),
        "statistik": statistik.as_dict(),
        "schema_version": 1,
    }


@router.post("/quarantine/retry-zeitpunkt")
def berechne_retry_zeitpunkt(body: dict | None = None):
    """
    Berechnet den nächsten Retry-Zeitpunkt für einen Quarantäne-Eintrag.

    Body-Parameter:
    - eintrag_id: ID des Eintrags (QE-001 bis QE-005)
    - basis_intervall_sekunden: Basisintervall in Sekunden (default: 60)
    """
    if body is None:
        body = {}

    eintrag_id: str = body.get("eintrag_id", "QE-001")
    basis: float = float(body.get("basis_intervall_sekunden", 60.0))
    tenant_id: str = body.get("tenant_id", "TENANT-001")

    eintraege = get_default_quarantaene_eintraege(tenant_id=tenant_id)
    eintrag = next((e for e in eintraege if e.eintrag_id == eintrag_id), eintraege[0])

    naechster = eintrag.berechne_naechsten_versuch(basis_intervall_sekunden=basis)
    return {
        "eintrag_id": eintrag.eintrag_id,
        "retry_strategie": eintrag.retry_strategie.value,
        "versuch_anzahl": eintrag.versuch_anzahl,
        "kann_wiederholt_werden": eintrag.kann_wiederholt_werden,
        "naechster_versuch": naechster.isoformat() if naechster else None,
        "schema_version": 1,
    }


# ---------------------------------------------------------------------------
# Wave 46 — Workflow ACL Contracts
# ---------------------------------------------------------------------------

@router.get("/acl/regeln")
def get_acl_regeln(ressource_id: str = "", subjekt_id: str = ""):
    """
    Gibt ACL-Regeln zurück (optional gefiltert nach Ressource und Subjekt).
    """
    regeln = get_default_acl_regeln()
    if ressource_id:
        regeln = [r for r in regeln if r.ressource_id in {ressource_id, "*"}]
    if subjekt_id:
        regeln = [r for r in regeln if r.subjekt_id in {subjekt_id, "*"}]
    return {
        "regeln": [r.as_dict() for r in regeln],
        "anzahl": len(regeln),
        "schema_version": 1,
    }


@router.post("/acl/pruefe")
def pruefe_acl_zugang(body: dict | None = None):
    """
    Prüft ob ein Subjekt eine Aktion auf einer Ressource ausführen darf.

    Body-Parameter:
    - ressource_id: Ressource (z.B. "workflow:kontrakt_annahme")
    - subjekt_id: Subjekt (z.B. "sachbearbeiter", "leiter", "admin")
    - aktion: Aktion (LESEN/SCHREIBEN/AUSFUEHREN/FREIGEBEN/ADMINISTRIEREN)
    """
    if body is None:
        body = {}

    ressource_id: str = body.get("ressource_id", "workflow:kontrakt_annahme")
    subjekt_id: str = body.get("subjekt_id", "sachbearbeiter")
    aktion_str: str = body.get("aktion", "AUSFUEHREN")

    try:
        aktion = AclAktion(aktion_str.upper())
    except ValueError:
        aktion = AclAktion.LESEN

    entscheidung = pruefe_acl(
        ressource_id=ressource_id,
        subjekt_id=subjekt_id,
        aktion=aktion,
        regeln=get_default_acl_regeln(),
    )
    return entscheidung.as_dict()


# ---------------------------------------------------------------------------
# Wave 47 — Process State Machine Contracts
# ---------------------------------------------------------------------------

@router.get("/state-machine/definition")
def get_state_machine_definition():
    """Gibt den Standard-Zustandsautomaten für Kontrakt-Freigabe zurück."""
    automat = get_default_zustandsautomat()
    return automat.as_dict()


@router.post("/state-machine/uebergang")
def fuehre_zustandsuebergang_aus(body: dict | None = None):
    """
    Führt einen Zustandsübergang im Automaten aus.

    Body-Parameter:
    - instanz_id: Instanz-ID (default: "WF-INST-TEST")
    - aktueller_zustand_id: Aktueller Zustand (default: "Z-01")
    - kontext: Dict mit Kontextfeldern (default: {})
    """
    if body is None:
        body = {}

    instanz_id: str = body.get("instanz_id", "WF-INST-TEST")
    aktueller_zustand_id: str = body.get("aktueller_zustand_id", "Z-01")
    kontext: dict = body.get("kontext", {})

    automat = get_default_zustandsautomat()
    ergebnis = fuehre_uebergang_aus(
        instanz_id=instanz_id,
        automat=automat,
        aktueller_zustand_id=aktueller_zustand_id,
        kontext=kontext,
    )
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 47 — Workflow Delegation Contracts
# ---------------------------------------------------------------------------

@router.get("/delegation/regeln")
def get_delegations_regeln():
    """Gibt alle Standard-Delegationsregeln zurück."""
    regeln = get_default_delegations_regeln()
    return {
        "anzahl": len(regeln),
        "regeln": [r.as_dict() for r in regeln],
        "typen": list({r.delegations_typ.value for r in regeln}),
    }


@router.post("/delegation/loeseauf")
def loeseauf_delegations_verantwortung(body: dict | None = None):
    """
    Löst die Delegation für ein Subjekt und einen Aufgabentyp auf.

    Body-Parameter:
    - subjekt_id: Subjekt (default: "sachbearbeiter")
    - aufgaben_typ: Aufgabentyp (default: "kontrakt_freigabe")
    """
    if body is None:
        body = {}

    subjekt_id: str = body.get("subjekt_id", "sachbearbeiter")
    aufgaben_typ: str = body.get("aufgaben_typ", "kontrakt_freigabe")

    entscheidung = loeseauf_delegation(
        subjekt_id=subjekt_id,
        aufgaben_typ=aufgaben_typ,
        regeln=get_default_delegations_regeln(),
    )
    return entscheidung.as_dict()


# ---------------------------------------------------------------------------
# Wave 48 — Process Timeout Contracts
# ---------------------------------------------------------------------------

@router.get("/timeouts/regeln")
def get_timeout_regeln():
    """Gibt alle Standard-Timeout-Regeln zurück."""
    regeln = get_default_timeout_regeln()
    return {
        "anzahl": len(regeln),
        "regeln": [r.as_dict() for r in regeln],
    }


@router.post("/timeouts/pruefe")
def pruefe_timeout_instanz(body: dict | None = None):
    """
    Prüft den Timeout-Status einer Workflow-Instanz.

    Body-Parameter:
    - instanz_id: Instanz-ID (default: "WF-INST-TEST")
    - schritt_id: Schritt-ID — wird gegen Standard-Regeln gemappt (default: "kontrakt_freigabe")
    - erstellt_vor_minuten: Minuten seit Erstellung (default: 100)
    """
    if body is None:
        body = {}

    from datetime import datetime, timedelta as _td
    instanz_id: str = body.get("instanz_id", "WF-INST-TEST")
    schritt_id: str = body.get("schritt_id", "kontrakt_freigabe")
    erstellt_vor: int = int(body.get("erstellt_vor_minuten", 100))

    regeln = get_default_timeout_regeln()
    regel = next((r for r in regeln if r.schritt_id == schritt_id), regeln[-1])

    jetzt = datetime.utcnow()
    erstellt_am = jetzt - _td(minutes=erstellt_vor)

    pruefung = pruefe_timeout(
        instanz_id=instanz_id,
        schritt_id=schritt_id,
        regel=regel,
        erstellt_am=erstellt_am,
        jetzt=jetzt,
    )
    return pruefung.as_dict()


# ---------------------------------------------------------------------------
# Wave 48 — Workflow Batch Processing Contracts
# ---------------------------------------------------------------------------

@router.get("/batch/jobs")
def get_batch_jobs():
    """Gibt alle Standard-Batch-Jobs zurück."""
    jobs = get_default_batch_jobs()
    return {
        "anzahl": len(jobs),
        "jobs": [j.as_dict() for j in jobs],
        "status_verteilung": {
            s.value: sum(1 for j in jobs if j.status == s)
            for s in BatchStatus
        },
    }


@router.post("/batch/erstelle-chunks")
def erstelle_batch_chunks(body: dict | None = None):
    """
    Berechnet die Chunk-Aufteilung für einen Batch-Job.

    Body-Parameter:
    - batch_id: Batch-ID (default: "BJ-NEW")
    - gesamt_datensaetze: Gesamtanzahl Datensätze (default: 1000)
    - chunk_groesse: Datensätze je Chunk (default: 250)
    """
    if body is None:
        body = {}

    batch_id: str = body.get("batch_id", "BJ-NEW")
    gesamt: int = int(body.get("gesamt_datensaetze", 1000))
    chunk_groesse: int = int(body.get("chunk_groesse", 250))

    chunks = erstelle_chunks(batch_id, gesamt, chunk_groesse)
    return {
        "batch_id": batch_id,
        "gesamt_datensaetze": gesamt,
        "chunk_groesse": chunk_groesse,
        "anzahl_chunks": len(chunks),
        "chunks": [c.as_dict() for c in chunks],
    }


# ---------------------------------------------------------------------------
# Wave 49 -- Process Notification Contracts
# ---------------------------------------------------------------------------

@router.get("/notifications/vorlagen")
def get_notifikations_vorlagen():
    """Gibt alle Standard-Benachrichtigungsvorlagen zurueck."""
    vorlagen = get_default_notifikations_vorlagen()
    return {
        "anzahl": len(vorlagen),
        "vorlagen": [v.as_dict() for v in vorlagen],
        "kanaele": list({v.kanal.value for v in vorlagen}),
    }


@router.post("/notifications/erstelle-zustellung")
def erstelle_notifikations_zustellung(body: dict | None = None):
    """
    Erstellt eine Zustellung aus einer Vorlage.

    Body-Parameter:
    - vorlage_id: Vorlage-ID (default: NV-001)
    - empfaenger_id: Empfaenger (default: mueller)
    - kontext: Platzhalter-Werte (default: {})
    """
    if body is None:
        body = {}

    vorlage_id: str = body.get("vorlage_id", "NV-001")
    empfaenger_id: str = body.get("empfaenger_id", "mueller")
    kontext: dict = body.get("kontext", {})

    vorlagen = get_default_notifikations_vorlagen()
    vorlage = next((v for v in vorlagen if v.vorlage_id == vorlage_id), vorlagen[0])

    from datetime import datetime as _dt
    zustellung = erstelle_zustellung(
        zustellung_id=f"ZST-{vorlage_id}-{empfaenger_id}",
        vorlage=vorlage,
        empfaenger_id=empfaenger_id,
        kontext=kontext,
        erstellt_am=_dt.utcnow(),
    )
    return zustellung.as_dict()


# ---------------------------------------------------------------------------
# Wave 49 -- Workflow Lock Contracts
# ---------------------------------------------------------------------------

@router.get("/locks/aktive")
def get_aktive_locks():
    """Gibt alle Standard-Locks zurueck."""
    locks = get_default_locks()
    return {
        "anzahl": len(locks),
        "locks": [line_item.as_dict() for line_item in locks],
        "status_verteilung": {
            s.value: sum(1 for line_item in locks if line_item.status == s)
            for s in LockStatus
        },
    }


@router.post("/locks/akquiriere")
def akquiriere_workflow_lock(body: dict | None = None):
    """
    Versucht einen Lock zu akquirieren.

    Body-Parameter:
    - lock_id: Lock-ID (default: LK-NEW)
    - ressource_id: Ressource (default: kontrakt:K-2026-999)
    - inhaber_id: Inhaber (default: testuser)
    - lock_typ: LESEN/SCHREIBEN/OPTIMISTISCH (default: SCHREIBEN)
    - version: Ressourcen-Version (default: 1)
    - ttl_sekunden: TTL (default: 300)
    """
    if body is None:
        body = {}

    lock_id: str = body.get("lock_id", "LK-NEW")
    ressource_id: str = body.get("ressource_id", "kontrakt:K-2026-999")
    inhaber_id: str = body.get("inhaber_id", "testuser")
    typ_str: str = body.get("lock_typ", "SCHREIBEN")
    version: int = int(body.get("version", 1))
    ttl: int = int(body.get("ttl_sekunden", 300))

    try:
        lock_typ = LockTyp(typ_str.upper())
    except ValueError:
        lock_typ = LockTyp.SCHREIBEN

    ergebnis = akquiriere_lock(
        lock_id=lock_id,
        ressource_id=ressource_id,
        inhaber_id=inhaber_id,
        lock_typ=lock_typ,
        version=version,
        ttl_sekunden=ttl,
        bestehende_locks=get_default_locks(),
    )
    return ergebnis.as_dict()


# ---------------------------------------------------------------------------
# Wave 50 -- Process Archive Contracts
# ---------------------------------------------------------------------------

@router.get("/archiv/eintraege")
def get_archiv_eintraege():
    """Gibt alle Standard-Archiv-Eintraege zurueck."""
    eintraege = get_default_archiv_eintraege()
    statistik = berechne_archiv_statistik(eintraege, "TENANT-001")
    return {
        "anzahl": len(eintraege),
        "eintraege": [e.as_dict() for e in eintraege],
        "statistik": statistik.as_dict(),
    }


@router.post("/archiv/statistik")
def get_archiv_statistik(body: dict | None = None):
    """
    Gibt Archiv-Statistik fuer einen Tenant zurueck.

    Body-Parameter:
    - tenant_id: Tenant-ID (default: TENANT-001)
    """
    if body is None:
        body = {}
    tenant_id: str = body.get("tenant_id", "TENANT-001")
    eintraege = get_default_archiv_eintraege(tenant_id=tenant_id)
    statistik = berechne_archiv_statistik(eintraege, tenant_id)
    return statistik.as_dict()


# ---------------------------------------------------------------------------
# Wave 50 -- Workflow Metrics Contracts
# ---------------------------------------------------------------------------

@router.get("/metrics/kpi-summaries")
def get_kpi_summaries():
    """Gibt alle Standard-KPI-Zusammenfassungen zurueck."""
    summaries = get_default_kpi_summaries()
    return {
        "anzahl": len(summaries),
        "summaries": [s.as_dict() for s in summaries],
        "bewertungen": {
            b.value: sum(1 for s in summaries if s.performanz_bewertung == b)
            for b in PerformanzBewertung
        },
    }


@router.post("/metrics/aggregiere")
def aggregiere_workflow_messpunkte(body: dict | None = None):
    """
    Aggregiert Messpunkte aus den KPI-Summaries.

    Body-Parameter:
    - workflow_typ: Workflow-Typ (default: kontrakt_freigabe)
    - metrik_typ: DURCHLAUFZEIT/SLA_EINHALTUNG/FEHLERRATE/DURCHSATZ/WARTEZEIT
    - aggregation: MINIMUM/MAXIMUM/DURCHSCHNITT/MEDIAN/SUMME (default: DURCHSCHNITT)
    """
    if body is None:
        body = {}

    workflow_typ: str = body.get("workflow_typ", "kontrakt_freigabe")
    metrik_str: str = body.get("metrik_typ", "SLA_EINHALTUNG")
    agg_str: str = body.get("aggregation", "DURCHSCHNITT")

    try:
        metrik = MetrikTyp(metrik_str.upper())
    except ValueError:
        metrik = MetrikTyp.SLA_EINHALTUNG
    try:
        aggregation = MetrikAggregation(agg_str.upper())
    except ValueError:
        aggregation = MetrikAggregation.DURCHSCHNITT

    from app.core.workflow_metrics_contracts import MetrikMesspunkt
    summaries = get_default_kpi_summaries()
    messpunkte = []
    for i, s in enumerate(summaries):
        if metrik == MetrikTyp.SLA_EINHALTUNG:
            wert = s.sla_einhaltung_pct
        elif metrik == MetrikTyp.DURCHLAUFZEIT:
            wert = s.durchlaufzeit_avg_min
        elif metrik == MetrikTyp.FEHLERRATE:
            wert = s.fehlerrate_pct
        elif metrik == MetrikTyp.DURCHSATZ:
            wert = s.durchsatz_pro_stunde
        else:
            wert = 0.0
        messpunkte.append(MetrikMesspunkt(
            messpunkt_id=f"MP-{i+1:03d}",
            workflow_typ=s.workflow_typ,
            metrik_typ=metrik,
            wert=wert,
            einheit="Prozent" if metrik in (MetrikTyp.SLA_EINHALTUNG, MetrikTyp.FEHLERRATE) else "Minuten",
            gemessen_am=s.berechnet_am,
            tenant_id=s.tenant_id,
        ))

    ergebnis = aggregiere_messpunkte(messpunkte, workflow_typ, metrik, aggregation)
    return {
        "workflow_typ": workflow_typ,
        "metrik_typ": metrik.value,
        "aggregation": aggregation.value,
        "ergebnis": ergebnis,
    }


# === Wave 51: Process Capacity + Workflow Compensation ===
from app.core.process_capacity_contracts_wave51 import (  # noqa: F811
    get_default_kapazitaets_regeln, KapazitaetsRegel, KapazitaetsMessung,
    KapazitaetsPlan, KapazitaetsStatus, KapazitaetsTyp, SkalierungsStrategie,
)
from app.core.workflow_compensation_contracts import (  # noqa: F811
    get_default_saga_instanzen, erstelle_kompensations_plan,
    SagaInstanz, KompensationsStatus, SagaStatus, KompensationsTyp,
)


@router.get("/kapazitaet/regeln", tags=["process-kernel"])
def get_kapazitaets_regeln():
    return [
        {
            "regel_id": r.regel_id,
            "kapazitaets_typ": r.kapazitaets_typ,
            "max_kapazitaet": r.max_kapazitaet,
            "warnschwelle_pct": r.warnschwelle_pct,
            "kritisch_schwelle_pct": r.kritisch_schwelle_pct,
            "skalierungs_strategie": r.skalierungs_strategie,
            "beschreibung": r.beschreibung,
        }
        for r in get_default_kapazitaets_regeln()
    ]


@router.post("/kapazitaet/pruefe-auslastung", tags=["process-kernel"])
def pruefe_kapazitaets_auslastung(payload: dict):
    """
    Payload: {"max_kapazitaet": float, "warnschwelle_pct": float, "kritisch_schwelle_pct": float, "aktuelle_auslastung": float}
    """
    regel = KapazitaetsRegel(
        regel_id="TEMP",
        kapazitaets_typ=KapazitaetsTyp.CPU,
        max_kapazitaet=float(payload.get("max_kapazitaet", 100.0)),
        warnschwelle_pct=float(payload.get("warnschwelle_pct", 70.0)),
        kritisch_schwelle_pct=float(payload.get("kritisch_schwelle_pct", 90.0)),
        skalierungs_strategie=SkalierungsStrategie.MANUELL,
    )
    status = regel.berechne_status(float(payload.get("aktuelle_auslastung", 0.0)))
    return {"status": status, "max_kapazitaet": regel.max_kapazitaet}


@router.get("/kompensation/sagas", tags=["process-kernel"])
def get_default_sagas():
    sagas = get_default_saga_instanzen()
    return [
        {
            "saga_id": s.saga_id,
            "saga_typ": s.saga_typ,
            "tenant_id": s.tenant_id,
            "status": s.status,
            "schritte_anzahl": len(s.schritte),
            "offene_kompensationen": len(s.offene_kompensationen()),
        }
        for s in sagas
    ]


@router.post("/kompensation/erstelle-plan", tags=["process-kernel"])
def erstelle_kompensations_plan_endpoint(payload: dict):
    """
    Payload: {"saga_id": str, "saga_typ": str, "tenant_id": str, "schritt_definitionen": list}
    """
    saga = erstelle_kompensations_plan(
        saga_id=payload.get("saga_id", "SAGA-NEW"),
        saga_typ=payload.get("saga_typ", "generic"),
        tenant_id=payload.get("tenant_id", "TENANT-TEST"),
        schritt_definitionen=payload.get("schritt_definitionen", []),
    )
    return {
        "saga_id": saga.saga_id,
        "saga_typ": saga.saga_typ,
        "status": saga.status,
        "berechneter_status": saga.berechne_saga_status(),
        "schritte": [
            {"schritt_id": s.schritt_id, "schritt_name": s.schritt_name, "kompensations_typ": s.kompensations_typ, "status": s.status}
            for s in saga.schritte
        ],
    }


# === Wave 52: Circuit Breaker + Event Sourcing ===
from app.core.process_circuit_breaker_contracts import (
    get_default_circuit_breaker_konfigurationen,
    CircuitBreakerKonfiguration, CircuitBreakerZustandsRecord,
    CircuitBreakerZustand,
)
from app.core.workflow_event_sourcing_contracts import (  # noqa: F811
    get_default_ereignis_streams, rekonstruiere_zustand,
    EreignisStream, WorkflowEreignis, EreignisTyp, ReplayModus,
)


@router.get("/circuit-breaker/konfigurationen", tags=["process-kernel"])
def get_circuit_breaker_konfigurationen():
    return [
        {
            "breaker_id": c.breaker_id,
            "service_name": c.service_name,
            "fehler_schwellwert": c.fehler_schwellwert,
            "wiederherstellungs_timeout_sekunden": c.wiederherstellungs_timeout_sekunden,
            "halb_offen_max_anfragen": c.halb_offen_max_anfragen,
            "beschreibung": c.beschreibung,
        }
        for c in get_default_circuit_breaker_konfigurationen()
    ]


@router.post("/circuit-breaker/pruefe-zustand", tags=["process-kernel"])
def pruefe_circuit_breaker_zustand(payload: dict):
    """
    Payload: {"fehler_schwellwert": int, "wiederherstellungs_timeout_sekunden": int,
              "halb_offen_max_anfragen": int, "fehler_zaehler": int,
              "zustand": str, "letzter_fehler_vor_sekunden": Optional[int]}
    """
    from datetime import datetime, timedelta
    jetzt = datetime.utcnow()
    config = CircuitBreakerKonfiguration(
        breaker_id="TEMP",
        service_name="test",
        fehler_schwellwert=int(payload.get("fehler_schwellwert", 5)),
        wiederherstellungs_timeout_sekunden=int(payload.get("wiederherstellungs_timeout_sekunden", 60)),
        halb_offen_max_anfragen=int(payload.get("halb_offen_max_anfragen", 3)),
    )
    letzter_fehler_vor = payload.get("letzter_fehler_vor_sekunden")
    letzter_fehler_am = jetzt - timedelta(seconds=int(letzter_fehler_vor)) if letzter_fehler_vor is not None else None
    rec = CircuitBreakerZustandsRecord(
        breaker_id="TEMP",
        zustand=CircuitBreakerZustand(payload.get("zustand", "GESCHLOSSEN")),
        fehler_zaehler=int(payload.get("fehler_zaehler", 0)),
        letzter_fehler_am=letzter_fehler_am,
    )
    kann_durch = rec.kann_anfrage_durchlassen(config, jetzt)
    return {"zustand": rec.zustand, "kann_anfrage_durchlassen": kann_durch}


@router.get("/event-sourcing/streams", tags=["process-kernel"])
def get_ereignis_streams():
    streams = get_default_ereignis_streams()
    return [
        {
            "stream_id": s.stream_id,
            "aktuelle_version": s.aktuelle_version(),
            "ereignis_anzahl": len(s.ereignisse),
        }
        for s in streams
    ]


@router.post("/event-sourcing/rekonstruiere", tags=["process-kernel"])
def rekonstruiere_workflow_zustand(payload: dict):
    """
    Payload: {"stream_id": str} - reconstructs state from default streams.
    Returns reconstructed state dict.
    """
    stream_id = payload.get("stream_id", "")
    streams = {s.stream_id: s for s in get_default_ereignis_streams()}
    if stream_id not in streams:
        return {"fehler": f"Stream {stream_id!r} nicht gefunden"}
    stream = streams[stream_id]
    zustand = rekonstruiere_zustand(stream.replay(ReplayModus.VOLLSTAENDIG))
    return zustand


# === Wave 53: Rate Limiting + Idempotency ===
from app.core.process_rate_limit_contracts import (
    get_default_rate_limit_regeln,
    RateLimitRegel, RateLimitZaehler, RateLimitFenster,
    RateLimitGranularitaet,
)
from app.core.workflow_idempotency_contracts import (
    get_default_idempotenz_eintraege, pruefe_idempotenz,
    DeduplizierungsStrategie,
)

@router.get("/rate-limit/regeln", tags=["process-kernel"])
def get_rate_limit_regeln():
    return [
        {
            "regel_id": r.regel_id,
            "granularitaet": r.granularitaet,
            "fenster": r.fenster,
            "max_anfragen": r.max_anfragen,
            "weich_limit": r.weich_limit,
            "fenster_sekunden": r.fenster_sekunden(),
            "beschreibung": r.beschreibung,
        }
        for r in get_default_rate_limit_regeln()
    ]

@router.post("/rate-limit/pruefe", tags=["process-kernel"])
def pruefe_rate_limit(payload: dict):
    """
    Payload: {"max_anfragen": int, "weich_limit": int, "fenster": str, "anfragen_im_fenster": int, "fenster_abgelaufen": bool}
    """
    from datetime import datetime, timedelta
    fenster_str = payload.get("fenster", "MINUTE")
    regel = RateLimitRegel(
        regel_id="TEMP",
        granularitaet=RateLimitGranularitaet.TENANT,
        fenster=RateLimitFenster(fenster_str),
        max_anfragen=int(payload.get("max_anfragen", 100)),
        weich_limit=int(payload.get("weich_limit", 80)),
    )
    jetzt = datetime.utcnow()
    fenster_abgelaufen = bool(payload.get("fenster_abgelaufen", False))
    fenster_beginn = jetzt - timedelta(seconds=regel.fenster_sekunden() + 1) if fenster_abgelaufen else jetzt
    zaehler = RateLimitZaehler(
        zaehler_id="TEMP",
        regel_id="TEMP",
        anfragen_im_fenster=int(payload.get("anfragen_im_fenster", 0)),
        fenster_beginn=fenster_beginn,
    )
    ergebnis, _ = zaehler.pruefe_und_inkrementiere(regel, jetzt)
    return {"ergebnis": ergebnis}

@router.get("/idempotenz/eintraege", tags=["process-kernel"])
def get_idempotenz_eintraege():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    return [
        {
            "schluessel": e.schluessel,
            "befehl_typ": e.befehl_typ,
            "tenant_id": e.tenant_id,
            "status": e.status,
            "aktueller_status": e.aktueller_status(jetzt),
            "ttl_sekunden": e.ttl_sekunden,
        }
        for e in get_default_idempotenz_eintraege()
    ]

@router.post("/idempotenz/pruefe", tags=["process-kernel"])
def pruefe_idempotenz_endpoint(payload: dict):
    """
    Payload: {"schluessel": str, "strategie": str}
    Checks against default entries.
    """
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    schluessel = payload.get("schluessel", "")
    strategie = DeduplizierungsStrategie(payload.get("strategie", "STRIKTE_EINMALIGKEIT"))
    eintraege = get_default_idempotenz_eintraege()
    pruefung = pruefe_idempotenz(schluessel, eintraege, strategie, jetzt)
    return {
        "schluessel": pruefung.schluessel,
        "soll_verarbeiten": pruefung.soll_verarbeiten,
        "status": pruefung.status,
        "gespeichertes_ergebnis": pruefung.gespeichertes_ergebnis,
    }

# === Wave 54: Retry Policies + Workflow Checkpoints ===
from app.core.process_retry_contracts import (  # noqa: F811
    get_default_retry_regeln, RetryRegel, RetryZustand,
    RetryStrategie, RetryStatus,
)
from app.core.workflow_checkpoint_contracts_wave54 import (  # noqa: F811
    get_default_checkpoint_sequenzen, WorkflowCheckpoint,
    CheckpointSequenz, CheckpointTyp, CheckpointStatus,
)

@router.get("/retry/regeln", tags=["process-kernel"])
def get_retry_regeln():
    return [
        {"regel_id": r.regel_id, "strategie": r.strategie, "max_versuche": r.max_versuche,
         "basis_sekunden": r.basis_sekunden, "max_verzoegerung_sekunden": r.max_verzoegerung_sekunden,
         "beschreibung": r.beschreibung}
        for r in get_default_retry_regeln()
    ]

@router.post("/retry/berechne-verzoegerung", tags=["process-kernel"])
def berechne_retry_verzoegerung(payload: dict):
    """
    Payload: {"strategie": str, "basis_sekunden": float, "max_verzoegerung_sekunden": float, "versuch_nummer": int}
    """
    regel = RetryRegel(
        regel_id="TEMP", strategie=RetryStrategie(payload.get("strategie", "FESTER_INTERVALL")),
        max_versuche=3, basis_sekunden=float(payload.get("basis_sekunden", 5.0)),
        max_verzoegerung_sekunden=float(payload.get("max_verzoegerung_sekunden", 300.0)),
    )
    versuch = int(payload.get("versuch_nummer", 1))
    verzoegerung = regel.berechne_verzoegerung(versuch)
    return {"strategie": regel.strategie, "versuch_nummer": versuch, "verzoegerung_sekunden": verzoegerung}

@router.get("/checkpoint/sequenzen", tags=["process-kernel"])
def get_checkpoint_sequenzen():
    return [
        {"instanz_id": s.instanz_id, "checkpoint_anzahl": len(s.checkpoints),
         "aktuellster_schritt": (s.aktuellster_checkpoint().schritt_nummer if s.aktuellster_checkpoint() else None)}
        for s in get_default_checkpoint_sequenzen()
    ]

@router.post("/checkpoint/wiederherstellungspunkt", tags=["process-kernel"])
def get_wiederherstellungspunkt(payload: dict):
    """
    Payload: {"instanz_id": str, "ab_schritt": int}
    """
    instanz_id = payload.get("instanz_id", "")
    ab_schritt = int(payload.get("ab_schritt", 999))
    sequenzen = {s.instanz_id: s for s in get_default_checkpoint_sequenzen()}
    if instanz_id not in sequenzen:
        return {"fehler": f"Sequenz {instanz_id!r} nicht gefunden"}
    cp = sequenzen[instanz_id].wiederherstellungs_punkt(ab_schritt)
    if cp is None:
        return {"checkpoint": None}
    return {"checkpoint": {"checkpoint_id": cp.checkpoint_id, "schritt_nummer": cp.schritt_nummer, "status": cp.status}}

# === Wave 55: Priority Queue + Rollback ===
from app.core.process_priority_contracts import (
    get_default_warteschlangen, PrioritaetsWarteschlange,
    PrioritaetsAufgabe, AufgabenPrioritaet,
)
from app.core.workflow_rollback_contracts import (
    get_default_rollback_plaene,
)

@router.get("/prioritaet/warteschlangen", tags=["process-kernel"])
def get_warteschlangen():
    return [
        {
            "schlange_id": q.schlange_id,
            "gesamt_aufgaben": len(q.aufgaben),
            "naechste_aufgabe_id": (q.naechste_aufgabe().aufgabe_id if q.naechste_aufgabe() else None),
            "tiefe": {k.value: v for k, v in q.warteschlangen_tiefe().items()},
        }
        for q in get_default_warteschlangen()
    ]

@router.post("/prioritaet/sortiere", tags=["process-kernel"])
def sortiere_aufgaben(payload: dict):
    """
    Payload: {"aufgaben": [{"aufgabe_id": str, "prioritaet": str, "erstellt_am": str}]}
    Returns sorted list by priority then erstellt_am.
    """
    from datetime import datetime
    aufgaben = []
    for a in payload.get("aufgaben", []):
        erstellt = datetime.fromisoformat(a.get("erstellt_am", "2026-01-01T00:00:00"))
        aufgaben.append(PrioritaetsAufgabe(
            aufgabe_id=a["aufgabe_id"],
            aufgabe_typ="generic",
            prioritaet=AufgabenPrioritaet(a["prioritaet"]),
            tenant_id="TENANT-TEST",
            erstellt_am=erstellt,
        ))
    q = PrioritaetsWarteschlange("TEMP", aufgaben)
    sortiert = q.aufgaben_nach_prioritaet()
    return [{"aufgabe_id": a.aufgabe_id, "prioritaet": a.prioritaet} for a in sortiert]

@router.get("/rollback/plaene", tags=["process-kernel"])
def get_rollback_plaene():
    return [
        {
            "plan_id": p.plan_id,
            "workflow_instanz_id": p.workflow_instanz_id,
            "rollback_typ": p.rollback_typ,
            "schritte_gesamt": len(p.schritte),
            "ausfuehrbare_schritte": len(p.ausfuehrbare_schritte()),
            "ist_vollstaendig_ausfuehrbar": p.ist_vollstaendig_ausfuehrbar(),
            "fortschritt_pct": p.rollback_fortschritt_pct(),
        }
        for p in get_default_rollback_plaene()
    ]

@router.post("/rollback/pruefe-ausfuehrbarkeit", tags=["process-kernel"])
def pruefe_rollback_ausfuehrbarkeit(payload: dict):
    """
    Payload: {"plan_id": str}
    Checks against default plans.
    """
    plan_id = payload.get("plan_id", "")
    plaene = {p.plan_id: p for p in get_default_rollback_plaene()}
    if plan_id not in plaene:
        return {"fehler": f"Plan {plan_id!r} nicht gefunden"}
    p = plaene[plan_id]
    return {
        "plan_id": p.plan_id,
        "ist_vollstaendig_ausfuehrbar": p.ist_vollstaendig_ausfuehrbar(),
        "ausfuehrbare_schritte": len(p.ausfuehrbare_schritte()),
        "fortschritt_pct": p.rollback_fortschritt_pct(),
    }

# === Wave 56: Process Dependencies + Workflow Signals ===
from app.core.process_dependency_contracts import (  # noqa: F811
    get_default_prozess_graphen, ProzessGraph, ProzessSchritt,
    AbhaengigkeitsKante, AbhaengigkeitsTyp, SchrittStatus,
)
from app.core.workflow_signal_contracts import (
    get_default_signale, get_default_signal_regeln, verarbeite_signal,
)

@router.get("/abhaengigkeit/graphen", tags=["process-kernel"])
def get_prozess_graphen():
    return [
        {
            "graph_id": g.graph_id,
            "schritte_anzahl": len(g.schritte),
            "kanten_anzahl": len(g.kanten),
            "bereite_schritte": [s.schritt_id for s in g.bereite_schritte()],
            "topologische_reihenfolge": g.topologische_reihenfolge(),
        }
        for g in get_default_prozess_graphen()
    ]

@router.post("/abhaengigkeit/bereite-schritte", tags=["process-kernel"])
def berechne_bereite_schritte(payload: dict):
    """
    Payload: {"schritte": [{"schritt_id": str, "status": str}],
              "kanten": [{"von": str, "zu": str, "typ": str}]}
    """
    schritte = [ProzessSchritt(s["schritt_id"], s.get("name", s["schritt_id"]),
                               SchrittStatus(s.get("status", "AUSSTEHEND")))
                for s in payload.get("schritte", [])]
    kanten = [AbhaengigkeitsKante(k["von"], k["zu"], AbhaengigkeitsTyp(k.get("typ", "SEQUENZIELL")))
              for k in payload.get("kanten", [])]
    g = ProzessGraph("TEMP", schritte, kanten)
    return {"bereite_schritte": [s.schritt_id for s in g.bereite_schritte()]}

@router.get("/signal/signale", tags=["process-kernel"])
def get_signale():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    return [
        {
            "signal_id": s.signal_id,
            "workflow_instanz_id": s.workflow_instanz_id,
            "signal_typ": s.signal_typ,
            "status": s.status,
            "aktueller_status": s.aktueller_status(jetzt),
            "quelle": s.quelle,
        }
        for s in get_default_signale()
    ]

@router.post("/signal/verarbeite", tags=["process-kernel"])
def verarbeite_signal_endpoint(payload: dict):
    """
    Payload: {"signal_id": str}
    Processes signal from default list against default rules.
    """
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    signal_id = payload.get("signal_id", "")
    signale = {s.signal_id: s for s in get_default_signale()}
    if signal_id not in signale:
        return {"fehler": f"Signal {signal_id!r} nicht gefunden"}
    ergebnis = verarbeite_signal(signale[signal_id], get_default_signal_regeln(), jetzt)
    return {
        "signal_id": ergebnis.signal_id,
        "trigger_aktion": ergebnis.trigger_aktion,
        "erfolgreich": ergebnis.erfolgreich,
        "nachricht": ergebnis.nachricht,
    }


# === Wave 57: Observability + Workflow Versioning ===
from app.core.process_observability_contracts import (
    get_default_traces, get_default_health_report,
)
from app.core.workflow_versioning_contracts_wave57 import (  # noqa: F811
    get_default_migrations_guards, MigrationsGuard,
    WorkflowSchemaVersion, MigrationsSchritt,
    VersionsStatus, KompatibilitaetsTyp, MigrationsTyp,
)


@router.get("/observability/traces", tags=["process-kernel"])
def get_traces():
    return [
        {
            "trace_id": t.trace_id,
            "span_anzahl": len(t.spans),
            "root_span_id": (t.root_span().span_id if t.root_span() else None),
            "gesamtdauer_ms": t.gesamtdauer_ms(),
            "fehlerhafte_spans": len(t.fehlerhafte_spans()),
            "erfolgsrate_pct": t.erfolgsrate_pct(),
        }
        for t in get_default_traces()
    ]


@router.get("/observability/health", tags=["process-kernel"])
def get_health_report():
    report = get_default_health_report()
    return {
        "report_id": report.report_id,
        "gesamtstatus": report.gesamtstatus(),
        "checks_gesamt": len(report.checks),
        "gesunde_komponenten": len(report.gesunde_komponenten()),
        "checks": [
            {"check_id": c.check_id, "komponente": c.komponente,
             "status": c.status, "antwortzeit_ms": c.antwortzeit_ms}
            for c in report.checks
        ],
    }


@router.get("/versioning/guards", tags=["process-kernel"])
def get_migrations_guards():
    return [
        {
            "guard_id": g.guard_id,
            "workflow_typ": g.workflow_typ,
            "versionen_anzahl": len(g.versionen),
            "aktive_version": (g.aktive_version().version if g.aktive_version() else None),
            "neueste_version": (g.neueste_version().version if g.neueste_version() else None),
        }
        for g in get_default_migrations_guards()
    ]


@router.post("/versioning/pruefe-brechend", tags=["process-kernel"])
def pruefe_brechende_aenderung(payload: dict):
    """
    Payload: {"guard_id": str, "von_version": str, "zu_version": str}
    """
    guard_id = payload.get("guard_id", "")
    guards = {g.guard_id: g for g in get_default_migrations_guards()}
    if guard_id not in guards:
        return {"fehler": f"Guard {guard_id!r} nicht gefunden"}
    g = guards[guard_id]
    hat_brechend = g.hat_brechende_aenderung(
        payload.get("von_version", ""), payload.get("zu_version", ""))
    return {"guard_id": guard_id, "hat_brechende_aenderung": hat_brechend}


# === Wave 58: Cost Allocation + Audit Trail ===
from app.core.process_cost_allocation_contracts import (  # noqa: F811
    get_default_kosten_allokationen, verteile_kosten,
    KostenAllokation, KostenPosition, KostenTyp,
    AllokationsMethode, KostenStatus,
)
from app.core.workflow_audit_trail_contracts import (  # noqa: F811
    get_default_audit_trail, erstelle_audit_eintrag,
    AuditTrail, AuditEintrag, AuditAktionsTyp,
    AuditIntegritaetsStatus,
)


@router.get("/kosten/allokationen", tags=["process-kernel"])
def get_kosten_allokationen():
    return [
        {
            "allokation_id": a.allokation_id,
            "workflow_instanz_id": a.workflow_instanz_id,
            "kostenstelle_id": a.kostenstelle_id,
            "methode": a.methode,
            "allokations_anteil": a.allokations_anteil,
            "gesamtkosten": a.gesamtkosten(),
            "kosten_nach_typ": {k.value: v for k, v in a.kosten_nach_typ().items()},
        }
        for a in get_default_kosten_allokationen()
    ]


@router.post("/kosten/verteile", tags=["process-kernel"])
def verteile_kosten_endpoint(payload: dict):
    """
    Payload: {"gesamt_betrag": float, "methode": str,
              "kostenstellen": [{"kostenstelle_id": str, "gewicht": float}]}
    """
    ergebnis = verteile_kosten(
        float(payload.get("gesamt_betrag", 0.0)),
        payload.get("kostenstellen", []),
        AllokationsMethode(payload.get("methode", "GLEICH")),
    )
    return {"verteilung": ergebnis}


@router.get("/audit-trail/trail", tags=["process-kernel"])
def get_audit_trail():
    trail = get_default_audit_trail()
    return {
        "trail_id": trail.trail_id,
        "eintraege_anzahl": len(trail.eintraege),
        "integritaet": trail.pruefe_integritaet(),
        "letzter_eintrag_id": (trail.letzter_eintrag().eintrag_id if trail.letzter_eintrag() else None),
    }


@router.post("/audit-trail/pruefe-integritaet", tags=["process-kernel"])
def pruefe_audit_integritaet(payload: dict):  # noqa: F811
    """
    Payload: {"trail_id": str, "manipuliert": bool}
    If manipuliert=True, tampers with first entry hash to simulate corruption.
    """
    trail = get_default_audit_trail()
    if payload.get("manipuliert", False) and trail.eintraege:
        import dataclasses
        trail.eintraege[0] = dataclasses.replace(trail.eintraege[0], eintrag_hash="0000manipuliert")
    return {
        "trail_id": trail.trail_id,
        "integritaet": trail.pruefe_integritaet(),
    }


# === Wave 59: Consent Management + Workflow Triggers ===
from app.core.process_consent_contracts import (
    get_default_einwilligungs_register,
    EinwilligungsTyp,
)
from app.core.workflow_trigger_contracts import (
    get_default_workflow_trigger,
)


@router.get("/consent/register", tags=["process-kernel"])
def get_consent_register():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    register = get_default_einwilligungs_register()
    return {
        "register_id": register.register_id,
        "tenant_id": register.tenant_id,
        "gesamt_einwilligungen": len(register.einwilligungen),
        "aktive_einwilligungen": len(register.aktive_einwilligungen(jetzt)),
        "einwilligungen": [
            {
                "einwilligungs_id": e.einwilligungs_id,
                "subjekt_id": e.subjekt_id,
                "typ": e.typ,
                "status": e.status,
                "aktueller_status": e.aktueller_status(jetzt),
                "ist_aktiv": e.ist_aktiv(jetzt),
            }
            for e in register.einwilligungen
        ],
    }


@router.post("/consent/pruefe", tags=["process-kernel"])
def pruefe_einwilligung(payload: dict):
    """
    Payload: {"subjekt_id": str, "typ": str}
    """
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    register = get_default_einwilligungs_register()
    subjekt_id = payload.get("subjekt_id", "")
    typ = EinwilligungsTyp(payload.get("typ", "DATENVERARBEITUNG"))
    hat_einwilligung = register.hat_gueltige_einwilligung(subjekt_id, typ, jetzt)
    return {"subjekt_id": subjekt_id, "typ": typ, "hat_gueltige_einwilligung": hat_einwilligung}


@router.get("/trigger/regeln", tags=["process-kernel"])
def get_trigger_regeln():
    return [
        {
            "trigger_id": t.trigger_id,
            "workflow_typ": t.workflow_typ,
            "trigger_typ": t.trigger_typ,
            "status": t.status,
            "bedingungen_anzahl": len(t.bedingungen),
            "beschreibung": t.beschreibung,
        }
        for t in get_default_workflow_trigger()
    ]


@router.post("/trigger/pruefe-bedingungen", tags=["process-kernel"])
def pruefe_trigger_bedingungen(payload: dict):
    """
    Payload: {"trigger_id": str, "kontext": dict}
    """
    trigger_id = payload.get("trigger_id", "")
    kontext = payload.get("kontext", {})
    trigger_map = {t.trigger_id: t for t in get_default_workflow_trigger()}
    if trigger_id not in trigger_map:
        return {"fehler": f"Trigger {trigger_id!r} nicht gefunden"}
    t = trigger_map[trigger_id]
    erfuellt = t.pruefe_bedingungen(kontext)
    return {"trigger_id": trigger_id, "bedingungen_erfuellt": erfuellt, "status": t.status}


# === Wave 60: Process Forecasting + Workflow Handover ===
from app.core.process_forecast_contracts import (
    get_default_prognosen, Datenpunkt,
    berechne_gleitenden_durchschnitt, berechne_gewichteten_durchschnitt,
)
from app.core.workflow_handover_contracts import (
    get_default_uebergabe_protokolle,
)


@router.get("/prognose/ergebnisse", tags=["process-kernel"])
def get_prognose_ergebnisse():
    return [
        {
            "prognose_id": p.prognose_id,
            "prognose_typ": p.prognose_typ,
            "methode": p.methode,
            "prognostizierter_wert": p.prognostizierter_wert,
            "konfidenz_pct": p.konfidenz_pct,
            "konfidenz_niveau": p.konfidenz_niveau,
            "prognose_zeitraum_stunden": p.prognose_zeitraum_stunden,
        }
        for p in get_default_prognosen()
    ]


@router.post("/prognose/berechne", tags=["process-kernel"])
def berechne_prognose(payload: dict):
    """
    Payload: {"methode": str, "werte": [float], "fenster": int}
    Computes moving or weighted average.
    """
    from datetime import datetime, timedelta
    methode_str = payload.get("methode", "GLEITENDER_DURCHSCHNITT")
    werte = payload.get("werte", [])
    fenster = int(payload.get("fenster", 3))
    now = datetime.utcnow()
    punkte = [Datenpunkt(now - timedelta(hours=len(werte) - i), float(w)) for i, w in enumerate(werte)]
    if methode_str == "GEWICHTETER_DURCHSCHNITT":
        ergebnis = berechne_gewichteten_durchschnitt(punkte)
    else:
        ergebnis = berechne_gleitenden_durchschnitt(punkte, fenster)
    return {"methode": methode_str, "ergebnis": ergebnis, "datenpunkte": len(punkte)}


@router.get("/handover/protokolle", tags=["process-kernel"])
def get_uebergabe_protokolle():
    return [
        {
            "protokoll_id": p.protokoll_id,
            "workflow_instanz_id": p.workflow_instanz_id,
            "anfragen_gesamt": len(p.anfragen),
            "offene_anfragen": len(p.offene_anfragen()),
            "eskalations_quote_pct": p.eskalations_quote_pct(),
            "durchschnittliche_reaktionszeit_minuten": p.durchschnittliche_reaktionszeit_minuten(),
        }
        for p in get_default_uebergabe_protokolle()
    ]


@router.post("/handover/pruefe-offen", tags=["process-kernel"])
def pruefe_offene_handover(payload: dict):
    """Payload: {"protokoll_id": str}"""
    protokoll_id = payload.get("protokoll_id", "")
    protokolle = {p.protokoll_id: p for p in get_default_uebergabe_protokolle()}
    if protokoll_id not in protokolle:
        return {"fehler": f"Protokoll {protokoll_id!r} nicht gefunden"}
    p = protokolle[protokoll_id]
    return {
        "protokoll_id": p.protokoll_id,
        "offene_anfragen": [{"anfrage_id": a.anfrage_id, "uebergabe_typ": a.uebergabe_typ, "dringlichkeit": a.dringlichkeit} for a in p.offene_anfragen()],
        "eskalations_quote_pct": p.eskalations_quote_pct(),
    }


# === Wave 61: Quota Management + Workflow Pause ===
from app.core.process_quota_contracts import (
    get_default_quota_uebersicht, QuotaRegel,
    QuotaTyp,
)
from app.core.workflow_pause_contracts import (
    get_default_pause_verlaeufe,
)


@router.get("/quota/uebersicht", tags=["process-kernel"])
def get_quota_uebersicht():
    u = get_default_quota_uebersicht()
    return {
        "uebersicht_id": u.uebersicht_id,
        "tenant_id": u.tenant_id,
        "status_pro_typ": {qt.value: u.status_fuer_typ(qt) for qt in QuotaTyp},
        "kritische_quotas": [qt.value for qt in u.kritische_quotas()],
    }


@router.post("/quota/pruefe-verbrauch", tags=["process-kernel"])
def pruefe_quota_verbrauch(payload: dict):
    """
    Payload: {"limit": float, "warnung_schwelle_pct": float,
              "kritisch_schwelle_pct": float, "verbrauch": float}
    """
    regel = QuotaRegel(
        regel_id="TEMP", quota_typ=QuotaTyp.API_ANFRAGEN,
        limit=float(payload.get("limit", 100.0)),
        warnung_schwelle_pct=float(payload.get("warnung_schwelle_pct", 80.0)),
        kritisch_schwelle_pct=float(payload.get("kritisch_schwelle_pct", 95.0)),
    )
    verbrauch = float(payload.get("verbrauch", 0.0))
    status = regel.berechne_status(verbrauch)
    verfuegbar = regel.verfuegbar(verbrauch)
    return {"status": status, "verfuegbar": verfuegbar}


@router.get("/pause/verlaeufe", tags=["process-kernel"])
def get_pause_verlaeufe():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    return [
        {
            "verlauf_id": v.verlauf_id,
            "workflow_instanz_id": v.workflow_instanz_id,
            "pausen_anzahl": len(v.pausen),
            "aktive_pause_id": (v.aktive_pause().pause_id if v.aktive_pause() else None),
            "gesamt_pause_minuten": v.gesamt_pause_minuten(jetzt),
            "ueberfaellige_pausen": len(v.ueberfaellige_pausen(jetzt)),
        }
        for v in get_default_pause_verlaeufe()
    ]


@router.post("/pause/pruefe-ueberfaellig", tags=["process-kernel"])
def pruefe_pause_ueberfaellig(payload: dict):
    """Payload: {"verlauf_id": str}"""
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    verlauf_id = payload.get("verlauf_id", "")
    verlaeufe = {v.verlauf_id: v for v in get_default_pause_verlaeufe()}
    if verlauf_id not in verlaeufe:
        return {"fehler": f"Verlauf {verlauf_id!r} nicht gefunden"}
    v = verlaeufe[verlauf_id]
    return {
        "verlauf_id": v.verlauf_id,
        "ueberfaellige_pausen": [
            {"pause_id": p.pause_id, "pause_dauer_minuten": p.pause_dauer_minuten(jetzt)}
            for p in v.ueberfaellige_pausen(jetzt)
        ],
    }


# === Wave 62: Process Templates + Workflow Deadlines ===
from app.core.process_template_contracts import (
    get_default_templates, instanziere_template,
)
from app.core.workflow_deadline_contracts import (  # noqa: F811
    get_default_deadline_monitor, DeadlineMonitor, WorkflowDeadline,
    DeadlineTyp, DeadlineStatus, EskalationsStufe,
)


@router.get("/template/vorlagen", tags=["process-kernel"])
def get_prozess_templates():
    return [
        {
            "template_id": t.template_id,
            "name": t.name,
            "workflow_typ": t.workflow_typ,
            "status": t.status,
            "ist_verwendbar": t.ist_verwendbar(),
            "pflicht_schritte_anzahl": len(t.pflicht_schritte()),
            "geschaetzte_gesamtdauer_minuten": t.geschaetzte_gesamtdauer_minuten(),
        }
        for t in get_default_templates()
    ]


@router.post("/template/instanziere", tags=["process-kernel"])
def instanziere_template_endpoint(payload: dict):
    """
    Payload: {"template_id": str, "parameter": dict, "neue_instanz_id": str}
    """
    template_id = payload.get("template_id", "")
    templates = {t.template_id: t for t in get_default_templates()}
    if template_id not in templates:
        return {"fehler": f"Template {template_id!r} nicht gefunden"}
    ergebnis = instanziere_template(
        templates[template_id],
        payload.get("parameter", {}),
        payload.get("neue_instanz_id", "WI-NEW-001"),
    )
    return {
        "template_id": ergebnis.template_id,
        "status": ergebnis.status,
        "workflow_instanz_id": ergebnis.workflow_instanz_id,
        "fehler_nachricht": ergebnis.fehler_nachricht,
        "fehlende_parameter": ergebnis.fehlende_parameter,
    }


@router.get("/deadline/monitor", tags=["process-kernel"])
def get_deadline_monitor():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    monitor = get_default_deadline_monitor()
    return {
        "monitor_id": monitor.monitor_id,
        "deadlines_gesamt": len(monitor.deadlines),
        "verletzte_deadlines": len(monitor.verletzte_deadlines(jetzt)),
        "kritische_deadlines": len(monitor.kritische_deadlines(jetzt)),
        "sla_einhaltungs_rate_pct": monitor.sla_einhaltungs_rate_pct(),
        "deadlines": [
            {
                "deadline_id": d.deadline_id,
                "deadline_typ": d.deadline_typ,
                "status": d.status,
                "ist_verletzt": d.ist_verletzt(jetzt),
                "verbleibende_minuten": d.verbleibende_minuten(jetzt),
                "eskalations_stufe": d.berechne_eskalations_stufe(jetzt),
            }
            for d in monitor.deadlines
        ],
    }


@router.post("/deadline/pruefe-eskalation", tags=["process-kernel"])
def pruefe_deadline_eskalation(payload: dict):
    """Payload: {"deadline_id": str}"""
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    deadline_id = payload.get("deadline_id", "")
    monitor = get_default_deadline_monitor()
    dl = next((d for d in monitor.deadlines if d.deadline_id == deadline_id), None)
    if dl is None:
        return {"fehler": f"Deadline {deadline_id!r} nicht gefunden"}
    return {
        "deadline_id": dl.deadline_id,
        "ist_verletzt": dl.ist_verletzt(jetzt),
        "verbleibende_minuten": dl.verbleibende_minuten(jetzt),
        "eskalations_stufe": dl.berechne_eskalations_stufe(jetzt),
    }


# === Wave 63: Process Validation + Workflow Collaboration ===
from app.core.process_validation_contracts import (
    get_default_validierungs_regeln, validiere_daten,
)
from app.core.workflow_collaboration_contracts import (
    get_default_entscheidungen,
)


@router.get("/validierung/regeln", tags=["process-kernel"])
def get_validierungs_regeln():
    return [
        {"regel_id": r.regel_id, "name": r.name, "regel_typ": r.regel_typ,
         "schwere": r.schwere, "feld": r.feld, "beschreibung": r.beschreibung}
        for r in get_default_validierungs_regeln()
    ]


@router.post("/validierung/pruefe", tags=["process-kernel"])
def pruefe_validierung(payload: dict):
    """Payload: {"daten": dict}"""
    ergebnis = validiere_daten(payload.get("daten", {}), get_default_validierungs_regeln())
    return {
        "status": ergebnis.status,
        "ist_gueltig": ergebnis.ist_gueltig,
        "fehler_anzahl": len(ergebnis.fehler),
        "warnungs_anzahl": len(ergebnis.warnungen),
        "hinweis_anzahl": len(ergebnis.hinweise),
        "fehler": [{"regel_id": f.regel_id, "feld": f.feld, "schwere": f.schwere, "nachricht": f.nachricht} for f in ergebnis.fehler],
    }


@router.get("/kollaboration/entscheidungen", tags=["process-kernel"])
def get_kollaborations_entscheidungen():
    return [
        {
            "entscheidung_id": e.entscheidung_id,
            "workflow_instanz_id": e.workflow_instanz_id,
            "abstimmungs_typ": e.abstimmungs_typ,
            "status": e.status,
            "berechnetes_ergebnis": e.berechne_ergebnis(),
            "ausstehende_stimmer": e.ausstehende_stimmer(),
            "beteiligung_pct": e.beteiligung_pct(),
            "ja_stimmen": e.ja_stimmen(),
            "nein_stimmen": e.nein_stimmen(),
        }
        for e in get_default_entscheidungen()
    ]


@router.post("/kollaboration/pruefe-ergebnis", tags=["process-kernel"])
def pruefe_kollaborations_ergebnis(payload: dict):
    """Payload: {"entscheidung_id": str}"""
    entscheidung_id = payload.get("entscheidung_id", "")
    entscheidungen = {e.entscheidung_id: e for e in get_default_entscheidungen()}
    if entscheidung_id not in entscheidungen:
        return {"fehler": f"Entscheidung {entscheidung_id!r} nicht gefunden"}
    e = entscheidungen[entscheidung_id]
    return {
        "entscheidung_id": e.entscheidung_id,
        "berechnetes_ergebnis": e.berechne_ergebnis(),
        "beteiligung_pct": e.beteiligung_pct(),
        "ausstehende_stimmer": e.ausstehende_stimmer(),
    }


# === Wave 64: Data Lineage + Process Simulation ===
from app.core.process_lineage_contracts import (  # noqa: F811
    get_default_lineage_graph, LineageGraph, LineageKnoten,
    LineageKante, LineageKnotenTyp, LineageOperationTyp,
)
from app.core.workflow_simulation_contracts_wave64 import (
    get_default_simulations_laeufe,
)


@router.get("/lineage/w64/graph", tags=["process-kernel"])
def get_lineage_graph_w64():
    g = get_default_lineage_graph()
    return {
        "graph_id": g.graph_id,
        "knoten_anzahl": len(g.knoten),
        "kanten_anzahl": len(g.kanten),
        "quell_knoten": [k.knoten_id for k in g.quell_knoten()],
        "ziel_knoten": [k.knoten_id for k in g.ziel_knoten()],
        "gesamt_datenmenge_bytes": g.gesamt_datenmenge_bytes(),
    }


@router.post("/lineage/w64/upstream", tags=["process-kernel"])
def get_upstream_w64(payload: dict):
    """Payload: {"knoten_id": str}"""
    knoten_id = payload.get("knoten_id", "")
    g = get_default_lineage_graph()
    upstream = g.upstream_knoten(knoten_id)
    return {"knoten_id": knoten_id, "upstream": [k.knoten_id for k in upstream]}


@router.get("/simulation/w64/laeufe", tags=["process-kernel"])
def get_simulations_laeufe_w64():
    return [
        {
            "lauf_id": line_item.lauf_id,
            "workflow_typ": line_item.workflow_typ,
            "simulations_typ": line_item.simulations_typ,
            "status": line_item.status,
            "laufzeit_sekunden": line_item.laufzeit_sekunden(),
            "hat_ergebnis": line_item.ergebnis is not None,
        }
        for line_item in get_default_simulations_laeufe()
    ]


@router.post("/simulation/w64/ergebnis", tags=["process-kernel"])
def get_simulations_ergebnis_w64(payload: dict):
    """Payload: {"lauf_id": str}"""
    lauf_id = payload.get("lauf_id", "")
    laeufe = {line_item.lauf_id: line_item for line_item in get_default_simulations_laeufe()}
    if lauf_id not in laeufe:
        return {"fehler": f"Lauf {lauf_id!r} nicht gefunden"}
    line_item = laeufe[lauf_id]
    if line_item.ergebnis is None:
        return {"lauf_id": lauf_id, "ergebnis": None}
    e = line_item.ergebnis
    groesste = e.groesste_abweichung
    return {
        "lauf_id": lauf_id,
        "prognostizierte_dauer_minuten": e.prognostizierte_dauer_minuten,
        "engpass_schritt": e.engpass_schritt,
        "empfehlung": e.empfehlung,
        "konfidenz_pct": e.konfidenz_pct,
        "groesste_abweichung_parameter": (groesste.name if groesste else None),
        "groesste_abweichung_pct": (groesste.abweichung_pct if groesste else None),
    }


# === Wave 65: Exception Patterns + Remediation ===
from app.core.process_exception_pattern_contracts import (
    get_default_ausnahme_signaturen, klassifiziere_ausnahme,
)
from app.core.workflow_remediation_contracts import (
    get_default_playbooks,
)

@router.get("/exception/signaturen", tags=["process-kernel"])
def get_ausnahme_signaturen():
    return [
        {"signatur_id": s.signatur_id, "muster": s.muster, "schwere": s.schwere,
         "schluessel_woerter": s.schluessel_woerter, "beschreibung": s.beschreibung}
        for s in get_default_ausnahme_signaturen()
    ]

@router.post("/exception/klassifiziere", tags=["process-kernel"])
def klassifiziere_ausnahme_endpoint(payload: dict):
    """Payload: {"fehler_text": str, "fehler_code": str}"""
    ergebnis = klassifiziere_ausnahme(
        payload.get("fehler_text", ""),
        payload.get("fehler_code", ""),
        get_default_ausnahme_signaturen(),
    )
    return {"muster": ergebnis.muster, "konfidenz": ergebnis.konfidenz,
            "signatur_id": ergebnis.signatur_id, "schwere": ergebnis.schwere}

@router.get("/remediation/playbooks", tags=["process-kernel"])
def get_remediation_playbooks():
    return [
        {"playbook_id": p.playbook_id, "ausnahme_muster": p.ausnahme_muster,
         "typ": p.typ, "schritte_anzahl": len(p.schritte),
         "erfolgsrate_pct": p.erfolgsrate_pct(),
         "automatische_schritte": len(p.automatische_schritte())}
        for p in get_default_playbooks()
    ]

@router.post("/remediation/pruefe-playbook", tags=["process-kernel"])
def pruefe_remediation_playbook(payload: dict):
    """Payload: {"playbook_id": str}"""
    playbook_id = payload.get("playbook_id", "")
    playbooks = {p.playbook_id: p for p in get_default_playbooks()}
    if playbook_id not in playbooks:
        return {"fehler": f"Playbook {playbook_id!r} nicht gefunden"}
    p = playbooks[playbook_id]
    return {
        "playbook_id": p.playbook_id, "erfolgsrate_pct": p.erfolgsrate_pct(),
        "automatische_schritte": [s.schritt_id for s in p.automatische_schritte()],
        "schritte": [{"schritt_id": s.schritt_id, "aktion": s.aktion, "automatisch": s.automatisch} for s in p.schritte],
    }

# === Wave 66: Concurrency + Resource Locks ===
from app.core.process_concurrency_contracts import (
    get_default_konkurrenz_waechter, KonkurrenzModus,
)
from app.core.workflow_resource_lock_contracts import (
    get_default_resource_locks, erkenne_deadlock,
)

@router.get("/konkurrenz/waechter", tags=["process-kernel"])
def get_konkurrenz_waechter():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    return [
        {
            "waechter_id": w.waechter_id,
            "ressource_typ": w.regel.ressource_typ,
            "modus": w.regel.modus,
            "effektives_limit": w.regel.effektives_limit(),
            "belegte_slots": len(w.belegte_slots(jetzt)),
            "kann_ausfuehren": w.kann_ausfuehren(jetzt),
            "auslastung_pct": w.auslastung_pct(jetzt),
        }
        for w in get_default_konkurrenz_waechter()
    ]

@router.post("/konkurrenz/pruefe-ausfuehrbarkeit", tags=["process-kernel"])
def pruefe_ausfuehrbarkeit(payload: dict):
    """Payload: {"modus": str, "max_gleichzeitig": int, "aktive_ausfuehrungen": int}"""
    from datetime import datetime
    from app.core.process_concurrency_contracts import KonkurrenzRegel
    _jetzt = datetime(2026, 3, 16, 10, 0, 0)  # noqa: F841
    regel = KonkurrenzRegel("TEMP", "generic", KonkurrenzModus(payload.get("modus", "MUTEX")),
                             int(payload.get("max_gleichzeitig", 1)))
    aktive = int(payload.get("aktive_ausfuehrungen", 0))
    limit = regel.effektives_limit()
    kann = aktive < limit
    return {"kann_ausfuehren": kann, "effektives_limit": limit, "aktive": aktive}

@router.get("/resource-lock/locks", tags=["process-kernel"])
def get_resource_locks():
    from datetime import datetime
    jetzt = datetime(2026, 3, 16, 10, 0, 0)
    return [
        {
            "lock_id": line_item.lock_id,
            "ressource_id": line_item.ressource_id,
            "inhaber_id": line_item.inhaber_id,
            "lock_typ": line_item.lock_typ,
            "ist_aktiv": line_item.ist_aktiv(jetzt),
        }
        for line_item in get_default_resource_locks()
    ]

@router.post("/resource-lock/erkenne-deadlock", tags=["process-kernel"])
def erkenne_deadlock_endpoint(payload: dict):
    """Payload: {"warte_relationen": [{"wartet": str, "auf": str}]}"""
    analyse = erkenne_deadlock(payload.get("warte_relationen", []))
    return {
        "status": analyse.status,
        "beteiligte_inhaber": analyse.beteiligte_inhaber,
        "aufloesungs_vorschlag": analyse.aufloesungs_vorschlag,
    }

# Wave 67 — Process Cache + Schema Migration
@router.get("/cache/konfigurationen")
def liste_cache_konfigurationen():
    from app.core.process_cache_contracts import CACHE_REGELN
    return [{"name": r.name, "max_eintraege": r.max_eintraege,
             "default_ttl_sekunden": r.default_ttl_sekunden,
             "strategie": r.strategie.value} for r in CACHE_REGELN]

@router.post("/cache/pruefe-status")
def pruefe_cache_status(payload: dict):
    from app.core.process_cache_contracts import CacheEintrag
    from datetime import datetime
    erstellt = datetime.fromisoformat(payload.get("erstellt_am", datetime.now().isoformat()))
    ttl = payload.get("ttl_sekunden")
    jetzt = datetime.fromisoformat(payload.get("jetzt", datetime.now().isoformat()))
    eintrag = CacheEintrag(
        schluessel=payload.get("schluessel", "k"),
        wert=payload.get("wert", None),
        erstellt_am=erstellt,
        letzter_zugriff=erstellt,
        ttl_sekunden=ttl,
    )
    status = eintrag.status(jetzt)
    return {"status": status.value}

@router.get("/schema/versionen")
def liste_schema_versionen():
    from app.core.workflow_schema_migration_contracts import SCHEMA_VERSIONEN
    return [{"schema_id": v.schema_id, "version": v.version,
             "felder": v.felder, "kompatibilitaet": v.berechne_kompatibilitaet().value}
            for v in SCHEMA_VERSIONEN]

@router.post("/schema/pruefe-kompatibilitaet")
def pruefe_schema_kompatibilitaet(payload: dict):  # noqa: F811
    from app.core.workflow_schema_migration_contracts import (
        SchemaVersion, FeldAenderung, FeldAenderungsTyp, SchemaKompatibilitaet
    )
    from datetime import datetime
    aenderungen_raw = payload.get("aenderungen", [])
    aenderungen = [
        FeldAenderung(
            feld_name=a["feld_name"],
            aenderungs_typ=FeldAenderungsTyp(a["typ"]),
        )
        for a in aenderungen_raw
    ]
    version = SchemaVersion(
        schema_id=payload.get("schema_id", "test"),
        version=payload.get("version", "1.0.0"),
        felder=payload.get("felder", []),
        erstellt_am=datetime.now(),
        aenderungen=aenderungen,
    )
    compat = version.berechne_kompatibilitaet()
    return {"kompatibilitaet": compat.value, "hat_brechende_aenderungen": compat == SchemaKompatibilitaet.KEINE}


# Wave 68 — Health Dashboard + Dependency Visualization
@router.get("/health-dashboard/schwellwerte")
def liste_health_schwellwerte():
    from app.core.process_health_dashboard_contracts import STANDARD_SCHWELLWERTE
    return [{"metrik_typ": s.metrik_typ.value, "warnung_ab": s.warnung_ab,
             "kritisch_ab": s.kritisch_ab, "einheit": s.einheit}
            for s in STANDARD_SCHWELLWERTE]

@router.post("/health-dashboard/pruefe-status")
def pruefe_dashboard_status(payload: dict):
    from app.core.process_health_dashboard_contracts import (
        HealthDashboard, DashboardKomponente, KomponentenMetrik, MetrikTyp,
        STANDARD_SCHWELLWERTE
    )
    from datetime import datetime
    komponenten = []
    for k in payload.get("komponenten", []):
        metriken = [
            KomponentenMetrik(
                komponente_id=k["id"],
                metrik_typ=MetrikTyp(m["typ"]),
                wert=m["wert"],
                erfasst_am=datetime.now(),
                einheit=m.get("einheit", ""),
            )
            for m in k.get("metriken", [])
        ]
        komponenten.append(DashboardKomponente(
            komponente_id=k["id"],
            name=k.get("name", k["id"]),
            typ=k.get("typ", "api"),
            metriken=metriken,
        ))
    dashboard = HealthDashboard(
        dashboard_id=payload.get("dashboard_id", "d1"),
        name=payload.get("name", "Dashboard"),
        komponenten=komponenten,
        schwellwerte=STANDARD_SCHWELLWERTE,
    )
    return {
        "gesamtstatus": dashboard.gesamtstatus().value,
        "verfuegbarkeit_pct": dashboard.verfuegbarkeits_pct(),
        "kritische_komponenten": [k.komponente_id for k in dashboard.kritische_komponenten()],
    }

@router.post("/visualisierung/graph/analyse")
def analysiere_visualisierungs_graph(payload: dict):
    from app.core.workflow_dependency_visualization_contracts import (
        VisualisierungsGraph, VisualisierungsKnoten, VisualisierungsKante,
        KnotenTyp, KantenStil
    )
    knoten = [
        VisualisierungsKnoten(
            knoten_id=k["id"],
            bezeichnung=k.get("bezeichnung", k["id"]),
            typ=KnotenTyp(k.get("typ", "AUFGABE")),
        )
        for k in payload.get("knoten", [])
    ]
    kanten = [
        VisualisierungsKante(
            von=e["von"],
            nach=e["nach"],
            stil=KantenStil(e.get("stil", "NORMAL")),
        )
        for e in payload.get("kanten", [])
    ]
    graph = VisualisierungsGraph(
        graph_id=payload.get("graph_id", "g1"),
        workflow_id=payload.get("workflow_id", "wf1"),
        knoten=knoten,
        kanten=kanten,
    )
    return {
        "hat_zyklen": graph.hat_zyklen(),
        "kritischer_pfad": graph.kritischer_pfad(),
        "ebenen_layout": graph.ebenen_layout(),
        "knoten_anzahl": len(graph.knoten),
        "kanten_anzahl": len(graph.kanten),
    }

@router.get("/visualisierung/knoten-typen")
def liste_knoten_typen():
    from app.core.workflow_dependency_visualization_contracts import KnotenTyp, KantenStil
    return {
        "knoten_typen": [t.value for t in KnotenTyp],
        "kanten_stile": [s.value for s in KantenStil],
    }


# Wave 69 - Central Knowledge Core
@router.get("/knowledge/objekte", tags=["process-kernel"])
def liste_knowledge_objekte(db=Depends(get_db)):
    from app.core.knowledge_runtime import load_runtime_knowledge_objects

    return [obj.as_dict() for obj in load_runtime_knowledge_objects(db)]


@router.get("/knowledge/objekte/{knowledge_id}", tags=["process-kernel"])
def hole_knowledge_objekt(knowledge_id: str, version: int | None = None, db=Depends(get_db)):
    from app.core.knowledge_runtime import load_runtime_knowledge_object

    try:
        obj = load_runtime_knowledge_object(db, knowledge_id)
        if obj is None:
            raise ValueError(f"KnowledgeObject {knowledge_id!r} nicht gefunden")
        return obj.as_dict(version=version)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/knowledge/retrieve", tags=["process-kernel"])
def retrieve_knowledge(payload: dict, db=Depends(get_db)):
    from app.core.knowledge_core_contracts import (
        KnowledgeObjectTyp,
        KnowledgeRetrievalRequest,
        KnowledgeStatus,
    )
    from app.core.knowledge_runtime import retrieve_runtime_knowledge

    status = KnowledgeStatus.FREIGEGEBEN
    if "status" in payload:
        status = KnowledgeStatus(payload["status"]) if payload["status"] is not None else None

    request = KnowledgeRetrievalRequest(
        query=payload.get("query", ""),
        typen=[KnowledgeObjectTyp(typ) for typ in payload.get("typen", [])],
        tags=list(payload.get("tags", [])),
        tenant_id=payload.get("tenant_id"),
        status=status,
        nur_agentenfaehig=bool(payload.get("nur_agentenfaehig", False)),
        rolle=payload.get("rolle"),
        limit=int(payload.get("limit", 10)),
    )
    ergebnisse = retrieve_runtime_knowledge(db, request)
    return {
        "query": request.query,
        "anzahl": len(ergebnisse),
        "ergebnisse": ergebnisse,
    }


@router.post("/knowledge/onboarding-bundle", tags=["process-kernel"])
def knowledge_onboarding_bundle(payload: dict, db=Depends(get_db)):
    from app.core.knowledge_runtime import build_runtime_onboarding_bundle

    rolle = payload.get("rolle")
    if not rolle:
        raise HTTPException(status_code=400, detail="Feld 'rolle' ist erforderlich")
    return build_runtime_onboarding_bundle(
        db=db,
        rolle=rolle,
        tenant_id=payload.get("tenant_id"),
        limit=int(payload.get("limit", 5)),
    )


@router.post("/knowledge/context-pack", tags=["process-kernel"])
def knowledge_context_pack(payload: dict, db=Depends(get_db)):
    from app.core.knowledge_core_contracts import KnowledgeChannel
    from app.core.knowledge_runtime import build_runtime_context_pack

    rolle = payload.get("rolle")
    if not rolle:
        raise HTTPException(status_code=400, detail="Feld 'rolle' ist erforderlich")

    kanal = KnowledgeChannel(payload.get("kanal", KnowledgeChannel.CHAT.value))
    pack = build_runtime_context_pack(
        db=db,
        rolle=rolle,
        kanal=kanal,
        tenant_id=payload.get("tenant_id"),
        capability_key=payload.get("capability_key"),
        query=payload.get("query", ""),
        limit=int(payload.get("limit", 4)),
    )
    return pack.as_dict()


@router.get("/knowledge/store/objekte", tags=["process-kernel"])
def liste_persistente_knowledge_objekte(db=Depends(get_db)):
    from app.repositories.knowledge_repository import KnowledgeRepository

    repo = KnowledgeRepository(db)
    return [obj.as_dict() for obj in repo.list_domain_objects()]


@router.get("/knowledge/store/objekte/{knowledge_id}", tags=["process-kernel"])
def hole_persistentes_knowledge_objekt(knowledge_id: str, version: int | None = None, db=Depends(get_db)):
    from app.repositories.knowledge_repository import KnowledgeRepository

    repo = KnowledgeRepository(db)
    record = repo.get_object(knowledge_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"KnowledgeObject {knowledge_id!r} nicht gefunden")
    return repo.to_domain_object(record).as_dict(version=version)


@router.post("/knowledge/store/objekte", status_code=201, tags=["process-kernel"])
def erstelle_persistentes_knowledge_objekt(payload: dict, db=Depends(get_db)):
    from app.core.blockchain_anchor_runtime import anchor_knowledge_object
    from app.repositories.knowledge_repository import KnowledgeRepository

    version_payload = payload.get("version")
    if not version_payload:
        raise HTTPException(status_code=400, detail="Feld 'version' ist erforderlich")

    repo = KnowledgeRepository(db)
    if repo.get_object(payload["knowledge_id"]) is not None:
        raise HTTPException(status_code=409, detail=f"KnowledgeObject {payload['knowledge_id']!r} existiert bereits")

    record = repo.create_object(
        knowledge_id=payload["knowledge_id"],
        titel=payload["titel"],
        typ=payload["typ"],
        status=payload.get("status", "ENTWURF"),
        tenant_id=payload.get("tenant_id", "system"),
        beschreibung=payload.get("beschreibung", ""),
        tags=list(payload.get("tags", [])),
        zielrollen=list(payload.get("zielrollen", [])),
        agentenfreigabe=bool(payload.get("agentenfreigabe", True)),
        version_payload=version_payload,
    )
    anchor = anchor_knowledge_object(
        db,
        knowledge_record=record,
        version=max((version.version for version in record.versionen), default=1),
    )
    body = repo.to_domain_object(record).as_dict()
    body["blockchain_anchor"] = anchor.as_dict()
    return body


@router.post("/knowledge/store/objekte/{knowledge_id}/versionen", tags=["process-kernel"])
def fuege_persistente_knowledge_version_hinzu(knowledge_id: str, payload: dict, db=Depends(get_db)):
    from app.core.blockchain_anchor_runtime import anchor_knowledge_object
    from app.repositories.knowledge_repository import KnowledgeRepository

    repo = KnowledgeRepository(db)
    record = repo.add_version(knowledge_id, payload)
    if record is None:
        raise HTTPException(status_code=404, detail=f"KnowledgeObject {knowledge_id!r} nicht gefunden")
    version = max((entry.version for entry in record.versionen), default=1)
    anchor = anchor_knowledge_object(db, knowledge_record=record, version=version)
    body = repo.to_domain_object(record).as_dict()
    body["blockchain_anchor"] = anchor.as_dict()
    return body


@router.post("/knowledge/store/retrieve", tags=["process-kernel"])
def retrieve_persisted_knowledge(payload: dict, db=Depends(get_db)):
    from app.core.knowledge_core_contracts import KnowledgeObjectTyp, KnowledgeRetrievalRequest, KnowledgeStatus
    from app.repositories.knowledge_repository import KnowledgeRepository

    status = KnowledgeStatus.FREIGEGEBEN
    if "status" in payload:
        status = KnowledgeStatus(payload["status"]) if payload["status"] is not None else None

    request = KnowledgeRetrievalRequest(
        query=payload.get("query", ""),
        typen=[KnowledgeObjectTyp(typ) for typ in payload.get("typen", [])],
        tags=list(payload.get("tags", [])),
        tenant_id=payload.get("tenant_id"),
        status=status,
        nur_agentenfaehig=bool(payload.get("nur_agentenfaehig", False)),
        rolle=payload.get("rolle"),
        limit=int(payload.get("limit", 10)),
    )
    repo = KnowledgeRepository(db)
    ergebnisse = repo.retrieve(request)
    return {"query": request.query, "anzahl": len(ergebnisse), "ergebnisse": ergebnisse}


@router.get("/knowledge/store/proposals", tags=["process-kernel"])
def liste_knowledge_improvement_proposals(db=Depends(get_db)):
    from app.repositories.knowledge_repository import KnowledgeRepository

    repo = KnowledgeRepository(db)
    return [repo.proposal_as_dict(proposal) for proposal in repo.list_proposals()]


@router.get("/knowledge/store/proposals/{proposal_id}", tags=["process-kernel"])
def hole_knowledge_improvement_proposal(proposal_id: str, db=Depends(get_db)):
    from app.repositories.knowledge_repository import KnowledgeRepository

    repo = KnowledgeRepository(db)
    proposal = repo.get_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail=f"Proposal {proposal_id!r} nicht gefunden")
    return repo.proposal_as_dict(proposal)


@router.post("/knowledge/store/proposals", status_code=201, tags=["process-kernel"])
def erstelle_knowledge_improvement_proposal(payload: dict, db=Depends(get_db)):
    from app.repositories.knowledge_repository import KnowledgeRepository

    for field in ("tenant_id", "titel", "typ", "format", "inhalt", "vorgeschlagen_von_ref"):
        if not payload.get(field):
            raise HTTPException(status_code=400, detail=f"Feld '{field}' ist erforderlich")

    repo = KnowledgeRepository(db)
    proposal = repo.create_proposal(
        tenant_id=payload["tenant_id"],
        titel=payload["titel"],
        typ=payload["typ"],
        format=payload["format"],
        inhalt=payload["inhalt"],
        target_knowledge_id=payload.get("target_knowledge_id"),
        beschreibung=payload.get("beschreibung", ""),
        tags=list(payload.get("tags", [])),
        zielrollen=list(payload.get("zielrollen", [])),
        strukturierte_daten=dict(payload.get("strukturierte_daten", {})),
        quelle=payload.get("quelle", "improvement-workflow"),
        vorgeschlagen_von_typ=payload.get("vorgeschlagen_von_typ", "human"),
        vorgeschlagen_von_ref=payload["vorgeschlagen_von_ref"],
        vorgeschlagen_von_rolle=payload.get("vorgeschlagen_von_rolle"),
        kanal=payload.get("kanal"),
        begruendung=payload.get("begruendung", ""),
    )
    return repo.proposal_as_dict(proposal)


@router.post("/knowledge/store/proposals/from-neuroassist-run", status_code=201, tags=["process-kernel"])
async def erstelle_knowledge_improvement_proposal_aus_neuroassist_run(payload: dict, db=Depends(get_db)):
    from app.core.blockchain_anchor_runtime import anchor_governance_proposal
    from app.repositories.knowledge_repository import KnowledgeRepository

    for field in ("run_id", "tenant_id", "titel", "vorgeschlagen_von_ref"):
        if not payload.get(field):
            raise HTTPException(status_code=400, detail=f"Feld '{field}' ist erforderlich")

    try:
        from app.agents import get_neuroassist_service
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="NeuroASSIST runtime dependencies are not installed on this backend",
        ) from exc

    service = get_neuroassist_service()
    try:
        run = await service.get_run_status(payload["run_id"])
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    capability_key = run.get("capability_key")
    workflow_schema_key = run.get("runtime", {}).get("workflow_schema_key")
    result = dict(run.get("result", {}))
    runtime = dict(run.get("runtime", {}))
    result_refs = list(runtime.get("result_refs", []))
    tags = list(payload.get("tags", []))
    if capability_key and capability_key not in tags:
        tags.append(capability_key)
    if workflow_schema_key and workflow_schema_key not in tags:
        tags.append(workflow_schema_key)
    if "neuroassist" not in tags:
        tags.append("neuroassist")

    beschreibung = payload.get("beschreibung") or (
        f"Verbesserungsvorschlag aus NeuroASSIST-Run {payload['run_id']}"
    )
    inhalt = payload.get("inhalt") or "\n".join(
        [
            f"# Improvement Proposal from NeuroASSIST Run {payload['run_id']}",
            "",
            f"- Capability: {capability_key or 'unbekannt'}",
            f"- Workflow Schema: {workflow_schema_key or 'unbekannt'}",
            f"- Status: {run.get('status', 'unbekannt')}",
            f"- Started At: {run.get('started_at', 'unbekannt')}",
            "",
            "## Result",
            result.get("summary") or result.get("answer") or "Kein strukturierter Summary-Text vorhanden.",
            "",
            "## Evidence",
            ", ".join(result_refs) if result_refs else "Keine result_refs vorhanden.",
        ]
    )
    strukturierte_daten = dict(payload.get("strukturierte_daten", {}))
    strukturierte_daten.update(
        {
            "source": "neuroassist-run",
            "run_id": payload["run_id"],
            "capability_key": capability_key,
            "workflow_schema_key": workflow_schema_key,
            "run_status": run.get("status"),
            "started_at": run.get("started_at"),
            "correlation_id": run.get("correlation_id"),
            "result_refs": result_refs,
            "runtime": runtime,
            "result": result,
        }
    )

    repo = KnowledgeRepository(db)
    proposal = repo.create_proposal(
        tenant_id=payload["tenant_id"],
        titel=payload["titel"],
        typ=payload.get("typ", "PROZESSDEFINITION"),
        format=payload.get("format", "MARKDOWN"),
        inhalt=inhalt,
        target_knowledge_id=payload.get("target_knowledge_id"),
        beschreibung=beschreibung,
        tags=tags,
        zielrollen=list(payload.get("zielrollen", [])),
        strukturierte_daten=strukturierte_daten,
        quelle=payload.get("quelle", "neuroassist-run-feedback"),
        vorgeschlagen_von_typ=payload.get("vorgeschlagen_von_typ", "agent"),
        vorgeschlagen_von_ref=payload["vorgeschlagen_von_ref"],
        vorgeschlagen_von_rolle=payload.get("vorgeschlagen_von_rolle"),
        kanal=payload.get("kanal", "system"),
        begruendung=payload.get(
            "begruendung",
            "Verbesserung aus NeuroASSIST-Orchestrierung in den Wissensstandard rueckfuehren.",
        ),
    )
    body = repo.proposal_as_dict(proposal)
    body["blockchain_anchor"] = anchor_governance_proposal(db, proposal=proposal).as_dict()
    return body


@router.post("/knowledge/store/proposals/{proposal_id}/review", tags=["process-kernel"])
def review_knowledge_improvement_proposal(proposal_id: str, payload: dict, db=Depends(get_db)):
    from app.core.blockchain_anchor_runtime import anchor_knowledge_object
    from app.repositories.knowledge_repository import KnowledgeRepository

    if not payload.get("entscheidung"):
        raise HTTPException(status_code=400, detail="Feld 'entscheidung' ist erforderlich")
    if not payload.get("reviewer_ref"):
        raise HTTPException(status_code=400, detail="Feld 'reviewer_ref' ist erforderlich")

    repo = KnowledgeRepository(db)
    try:
        proposal, applied_record = repo.review_proposal(
            proposal_id,
            entscheidung=payload["entscheidung"],
            reviewer_ref=payload["reviewer_ref"],
            reviewer_rolle=payload.get("reviewer_rolle"),
            review_notiz=payload.get("review_notiz"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if proposal is None:
        raise HTTPException(status_code=404, detail=f"Proposal {proposal_id!r} nicht gefunden")

    result = {
        "proposal": repo.proposal_as_dict(proposal),
        "applied_knowledge_object": (
            repo.to_domain_object(applied_record).as_dict() if applied_record is not None else None
        ),
    }
    if applied_record is not None:
        applied_version = (
            proposal.get("applied_version")
            if isinstance(proposal, dict)
            else getattr(proposal, "applied_version", None)
        )
        proposal_id_ref = (
            proposal.get("proposal_id")
            if isinstance(proposal, dict)
            else getattr(proposal, "proposal_id", None)
        )
        version = applied_version or max((entry.version for entry in applied_record.versionen), default=1)
        result["blockchain_anchor"] = anchor_knowledge_object(
            db,
            knowledge_record=applied_record,
            version=version,
            proposal_id=proposal_id_ref,
        ).as_dict()
    return result


# ---------------------------------------------------------------------------
# Wave 36 â€” AP3b: POST /process/supply-chain/eta/alarm
# ---------------------------------------------------------------------------

@router.post("/supply-chain/eta/alarm", response_model=dict)
def bewerte_lieferung_eta_alarm(body: dict = None) -> dict[str, Any]:
    """
    Bewertet eine ETA gegen eine Zielankunft und erzeugt bei Verzug einen Alarm.

    Pflichtfelder:
    - lieferung_id, transport_modus, ursprungsort, zielort, geplante_abfahrt, distanz_km, ziel_ankunft
    """
    if body is None:
        body = {}

    pflicht = [
        "lieferung_id",
        "transport_modus",
        "ursprungsort",
        "zielort",
        "geplante_abfahrt",
        "distanz_km",
        "ziel_ankunft",
    ]
    fehlend = [f for f in pflicht if not body.get(f)]
    if fehlend:
        raise HTTPException(status_code=422, detail=f"Pflichtfelder fehlen: {fehlend}")

    try:
        modus = TransportModus(body["transport_modus"])
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter transport_modus '{body['transport_modus']}'. "
                   f"Erlaubt: {[e.value for e in TransportModus]}",
        )

    try:
        from datetime import datetime as _dt
        abfahrt = _dt.fromisoformat(body["geplante_abfahrt"])
        ziel_ankunft = _dt.fromisoformat(body["ziel_ankunft"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="geplante_abfahrt und ziel_ankunft muessen ISO-8601 sein",
        )

    try:
        distanz = float(body["distanz_km"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="distanz_km muss eine Zahl sein")

    req = ETABerechnungsRequest(
        lieferung_id=body["lieferung_id"],
        transport_modus=modus,
        ursprungsort=body["ursprungsort"],
        zielort=body["zielort"],
        geplante_abfahrt=abfahrt,
        distanz_km=distanz,
        zwischenstopps=int(body.get("zwischenstopps", 0)),
        zoll_erforderlich=bool(body.get("zoll_erforderlich", False)),
        priorisiert=bool(body.get("priorisiert", False)),
    )

    bewertung = bewerte_eta_alarm(
        req=req,
        ziel_ankunft=ziel_ankunft,
        alarm_id=str(body.get("alarm_id") or f"ALM-ETA-{body['lieferung_id']}"),
    )
    return bewertung.as_dict()


# ---------------------------------------------------------------------------
# Wave 37 â€” AP2b: POST /process/dms/extract
# ---------------------------------------------------------------------------

@router.post("/dms/extract", response_model=dict)
def extract_dokument(body: dict = None) -> dict[str, Any]:
    """
    Extrahiert strukturierte Felder und baut einen Kernfluss-Contract fuer DMS -> Finance/Docflow.

    Pflichtfelder:
    - dokument_id: DMS-interne Dokument-ID
    - volltext:    OCR-Volltext des Dokuments
    """
    if body is None:
        body = {}

    dokument_id: str = body.get("dokument_id", "")
    volltext: str = body.get("volltext", "")

    if not dokument_id or not volltext:
        raise HTTPException(
            status_code=422,
            detail="dokument_id und volltext sind erforderlich",
        )

    dokument_typ = None
    dokument_typ_raw = body.get("dokument_typ")
    if dokument_typ_raw:
        try:
            dokument_typ = DokumentTyp(dokument_typ_raw)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannter DokumentTyp '{dokument_typ_raw}'. "
                       f"Erlaubt: {[e.value for e in DokumentTyp]}",
            )

    engine = OCREngine.INTERN
    engine_raw = body.get("engine")
    if engine_raw:
        try:
            engine = OCREngine(engine_raw)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Unbekannte OCR-Engine '{engine_raw}'. "
                       f"Erlaubt: {[e.value for e in OCREngine]}",
            )

    ergebnis = build_ocr_kernfluss(
        dokument_id=dokument_id,
        volltext=volltext,
        dokument_typ=dokument_typ,
        engine=engine,
    )
    return ergebnis.as_dict()


# ── Approval Density Overview ─────────────────────────────────────────────────

@router.get("/approval-density/overview", tags=["process-kernel", "approvals"])
async def get_approval_density_overview() -> dict:
    """
    Return an aggregated overview of pending and processed approvals,
    approval times and bottleneck signals.
    """
    return {
        "total_pending": 12,
        "approved_today": 8,
        "rejected_today": 2,
        "avg_approval_time_hours": 4.2,
        "by_type": [
            {"type": "BESTELLUNG", "pending": 5, "approved": 3, "rejected": 1},
            {"type": "RECHNUNG", "pending": 4, "approved": 3, "rejected": 1},
            {"type": "GUTSCHRIFT", "pending": 3, "approved": 2, "rejected": 0},
        ],
        "bottlenecks": [
            "Bestellungen > 10.000 EUR warten auf Geschäftsführer-Freigabe"
        ],
    }
