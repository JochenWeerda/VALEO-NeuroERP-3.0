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
from ....core.settlement_audit_chain import build_genesis_chain, CHAIN_GENESIS_HASH
from ....core.gobd_settlement_check import build_stub_gobd_check
from ....core.price_formula_engine import (
    FixedPriceSpec,
    FormulaPriceSpec,
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
    SchrittOverride,
    SchrittStatus,
    TenantProzessVariante,
    build_default_tenant_variante,
    get_default_agrar_settlement_schritte,
    resolve_process_steps,
    validate_prozess_variante,
)
from ....core.sla_eskalation_engine import (
    evaluate_sla_breach,
    get_default_sla_eskalations_policies,
    validate_sla_policy,
)
from ....core.otel_span_contracts import get_process_kernel_spans
from ....core.policy_code_engine import (
    evaluate_policy_set,
    get_default_agrar_policy_sets,
    validate_policy_set,
)
from ....core.query_contracts import get_process_kernel_queries
from ....core.human_approval_gate import (
    evaluate_approval_requirement,
    get_default_approval_rules,
    record_approval_decision,
    ApprovalDecision,
    ApprovalRisikostufe,
)
from ....core.slo_definitions import (
    check_slo_compliance,
    get_process_kernel_slos,
    validate_slo_definition,
)
from ....core.mcp_tool_contracts import get_process_kernel_mcp_tools
from ....core.data_quality_rules import (
    DQRuleSet,
    validate_datensatz,
    get_default_dq_rulesets,
)
from ....core.bulk_operations import (
    BulkItem,
    BulkOperationTyp,
    BulkRequest,
    get_bulk_limit_by_domain,
    get_default_bulk_limits,
    validate_bulk_request,
)
from ....core.background_jobs import (
    JobEnqueueRequest,
    JobStatus,
    JobTyp,
    create_job_from_request,
    evaluate_job_routing,
    get_default_job_types,
)
from ....core.dashboard_snapshots import (
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
