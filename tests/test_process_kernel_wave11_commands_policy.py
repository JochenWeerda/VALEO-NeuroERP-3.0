"""
Wave-11 Contract Tests: Command-Catalog, Policy-Resolution, Exception-Catalog,
Prozessreferenzen, Finance-Follow-up-Contracts, Explainability
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.process_commands import get_process_command_catalog, ProcessCommandDefinition
from app.core.process_references import build_process_reference_context, ProcessReferenceContext
from app.core.agrar_process_references import build_agrar_settlement_reference_context
from app.core.policy_decisions import (
    PolicyOverrideLayer,
    PolicyOverrideResolution,
    resolve_policy_override_layers,
    POLICY_OVERRIDE_PRIORITY,
)
from app.core.exception_rules import (
    DEFAULT_SETTLEMENT_EXCEPTION_CATALOG,
    ProcessExceptionRule,
    ProcessExceptionCatalog,
)
from app.core.explainability import (
    ExplainabilityView,
    build_policy_explainability_view,
)
from app.core.finance_followup import (
    MahnwesenPreview,
    MahnwesenExportFormat,
    MahnwesenExportRequest,
    MahnwesenExportResult,
    LastschriftPreview,
    LastschriftExportResult,
)


# ---------------------------------------------------------------------------
# AP1: Command-Catalog
# ---------------------------------------------------------------------------

def test_process_command_catalog_contains_core_aggregates():
    catalog = get_process_command_catalog()
    aggregates = {cmd.aggregate for cmd in catalog}
    assert "contract" in aggregates
    assert "acceptance" in aggregates
    assert "quality-protocol" in aggregates
    assert "settlement" in aggregates


def test_process_command_catalog_settlement_commands_include_preview_and_post():
    catalog = get_process_command_catalog()
    settlement_ids = {cmd.command_id for cmd in catalog if cmd.aggregate == "settlement"}
    assert "settlement.preview" in settlement_ids
    assert "settlement.create" in settlement_ids
    assert "settlement.post" in settlement_ids


def test_process_command_preview_is_idempotent_and_non_mutating():
    catalog = get_process_command_catalog()
    preview = next(cmd for cmd in catalog if cmd.command_id == "settlement.preview")
    assert preview.mutating is False
    assert preview.idempotent is True


def test_process_command_catalog_schema_version_contract():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.get("/process/commands")
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["count"] >= 13
    assert isinstance(data["commands"], list)


def test_process_command_catalog_endpoint_includes_policy_evaluate():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.get("/process/commands")
    commands_by_id = {cmd["command_id"]: cmd for cmd in response.json()["commands"]}
    assert "policy.evaluate" in commands_by_id
    assert commands_by_id["policy.evaluate"]["mutating"] is False


# ---------------------------------------------------------------------------
# AP2: Policy-Override-Resolution
# ---------------------------------------------------------------------------

def test_policy_override_priority_order_is_global_tenant_role_process():
    assert POLICY_OVERRIDE_PRIORITY["global"] < POLICY_OVERRIDE_PRIORITY["tenant"]
    assert POLICY_OVERRIDE_PRIORITY["tenant"] < POLICY_OVERRIDE_PRIORITY["role"]
    assert POLICY_OVERRIDE_PRIORITY["role"] < POLICY_OVERRIDE_PRIORITY["process"]


def test_resolve_policy_override_tenant_beats_global():
    layers = [
        PolicyOverrideLayer(scope="global", scope_key="*", rule_id="price.limit", enabled=True, reason="Global default", source="system"),
        PolicyOverrideLayer(scope="tenant", scope_key="t1", rule_id="price.limit", enabled=False, reason="Disabled for t1", source="admin"),
    ]
    resolution = resolve_policy_override_layers("price.limit", layers)
    assert resolution.effective_scope == "tenant"
    assert resolution.effective_enabled is False
    assert resolution.effective_scope_key == "t1"


def test_resolve_policy_override_process_scope_is_highest_priority():
    layers = [
        PolicyOverrideLayer(scope="tenant", scope_key="t1", rule_id="approval.required", enabled=False, reason="Tenant skip", source="admin"),
        PolicyOverrideLayer(scope="process", scope_key="settlement", rule_id="approval.required", enabled=True, reason="Always required for settlement", source="compliance"),
    ]
    resolution = resolve_policy_override_layers("approval.required", layers)
    assert resolution.effective_scope == "process"
    assert resolution.effective_enabled is True


def test_resolve_policy_override_empty_layers_has_no_effective_scope():
    resolution = resolve_policy_override_layers("unknown.rule", [])
    assert resolution.effective_scope is None
    assert resolution.effective_enabled is None
    assert resolution.evaluated_layers == []


def test_resolve_policy_override_api_endpoint_returns_schema_version():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.post("/process/policy/resolve", json={
            "rule_id": "price.limit",
            "layers": [
                {"scope": "global", "scope_key": "*", "rule_id": "price.limit", "enabled": True, "reason": "Default", "source": "system"},
            ],
        })
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["rule_id"] == "price.limit"
    assert data["effective_scope"] == "global"


# ---------------------------------------------------------------------------
# AP3: Exception-Catalog
# ---------------------------------------------------------------------------

def test_default_settlement_exception_catalog_has_three_rules():
    assert DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.process_key == "settlement"
    assert len(DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.rules) == 3


def test_settlement_exception_quality_deviation_requires_approval():
    rule = next(r for r in DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.rules if r.rule_id == "settlement.quality.deviation")
    assert rule.requires_approval is True
    assert "qs" in rule.approver_roles
    assert rule.decision_mode == "workflow-approval"


def test_settlement_exception_complaint_is_policy_based():
    rule = next(r for r in DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.rules if r.rule_id == "settlement.complaint.open")
    assert rule.category == "complaint"
    assert rule.decision_mode == "policy"
    assert rule.policy_rule_id == "complaint.open"


def test_exception_catalog_api_returns_settlement_catalog_with_schema_version():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.get("/process/exceptions/settlement")
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["process_key"] == "settlement"
    assert data["rule_count"] == 3


def test_exception_catalog_api_returns_404_for_unknown_process():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.get("/process/exceptions/nonexistent-process")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# AP4: Prozessreferenz-Kontext
# ---------------------------------------------------------------------------

def test_build_process_reference_context_carries_all_chain_ids():
    ctx = build_process_reference_context(
        process_key="settlement",
        anchor_entity="settlement",
        anchor_id="SET-001",
        contract_id="KON-42",
        harvest_acceptance_id="ANH-77",
        quality_protocol_id="QP-11",
        settlement_id="SET-001",
    )
    assert ctx.chain.contract_id == "KON-42"
    assert ctx.chain.harvest_acceptance_id == "ANH-77"
    assert ctx.chain.quality_protocol_id == "QP-11"
    assert ctx.anchor_id == "SET-001"


def test_process_reference_context_partial_chain_is_valid():
    ctx = build_process_reference_context(
        process_key="acceptance",
        anchor_entity="harvest_acceptance",
        anchor_id="ANH-01",
        harvest_acceptance_id="ANH-01",
    )
    assert ctx.chain.contract_id is None
    assert ctx.chain.settlement_id is None
    assert ctx.process_key == "acceptance"


def test_process_reference_api_returns_schema_version():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.post("/process/references", json={
            "process_key": "settlement",
            "anchor_entity": "settlement",
            "anchor_id": "SET-99",
            "contract_id": "KON-10",
        })
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["anchor_id"] == "SET-99"
    assert data["chain"]["contract_id"] == "KON-10"


def test_process_reference_api_requires_mandatory_fields():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.post("/process/references", json={"process_key": "settlement"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# AP5: Finance Follow-up Contracts
# ---------------------------------------------------------------------------

def test_mahnwesen_preview_has_schema_version():
    preview = MahnwesenPreview(
        tenant_id="t1",
        open_items_count=5,
        total_overdue_amount=1234.56,
        dunning_level_counts={"1": 3, "2": 2},
        export_ready=True,
    )
    assert preview.schema_version == 1


def test_mahnwesen_export_format_enum_covers_pdf_and_sepa():
    formats = {e.value for e in MahnwesenExportFormat}
    assert "pdf" in formats
    assert len(formats) >= 2


def test_mahnwesen_export_result_schema_version_is_stable():
    result = MahnwesenExportResult(
        export_id="EXP-001",
        tenant_id="t1",
        format=MahnwesenExportFormat.PDF,
        record_count=3,
    )
    assert result.schema_version == 1


def test_lastschrift_preview_schema_version_contract():
    preview = LastschriftPreview(
        tenant_id="t1",
        direct_debit_run_id="DD-RUN-01",
        total_amount=2750.00,
        debitor_count=7,
        mandate_valid_count=6,
        mandate_expired_count=1,
        sepa_ready=False,
    )
    assert preview.schema_version == 1


def test_lastschrift_export_result_schema_version_contract():
    result = LastschriftExportResult(
        export_id="EXP-LS-01",
        tenant_id="t1",
        direct_debit_run_id="DD-RUN-01",
        record_count=4,
    )
    assert result.schema_version == 1


# ---------------------------------------------------------------------------
# AP6: Explainability
# ---------------------------------------------------------------------------

def test_explainability_blocked_status_maps_to_blocked():
    layers = [
        PolicyOverrideLayer(scope="tenant", scope_key="t1", rule_id="settlement.post", enabled=False, reason="Einfrierung", source="admin"),
    ]
    resolution = resolve_policy_override_layers("settlement.post", layers)
    view = build_policy_explainability_view(resolution, blocked=True)
    assert view.status == "blocked"
    assert "blockiert" in view.summary.lower()
    assert view.rule_id == "settlement.post"


def test_explainability_approval_required_status():
    layers = [
        PolicyOverrideLayer(scope="role", scope_key="fibu", rule_id="payment.approve", enabled=True, reason="Pflichtfreigabe", source="compliance"),
    ]
    resolution = resolve_policy_override_layers("payment.approve", layers)
    view = build_policy_explainability_view(resolution, needs_approval=True)
    assert view.status == "approval-required"
    assert view.source_scope == "role"


def test_explainability_allowed_when_no_override():
    resolution = resolve_policy_override_layers("nonexistent.rule", [])
    view = build_policy_explainability_view(resolution)
    assert view.status == "allowed"
    assert view.source_scope is None


def test_explainability_api_returns_schema_version():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.post("/process/explainability", json={
            "rule_id": "price.limit",
            "layers": [
                {"scope": "global", "scope_key": "*", "rule_id": "price.limit", "enabled": True, "reason": "Default", "source": "system"},
            ],
            "blocked": False,
            "needs_approval": False,
        })
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["status"] == "allowed"
    assert data["rule_id"] == "price.limit"


def test_agrar_settlement_reference_sets_correct_anchor_and_process_key():
    ctx = build_agrar_settlement_reference_context(
        settlement_id="SET-100",
        contract_id="KON-55",
        harvest_acceptance_id="ANH-22",
        quality_protocol_id="QP-9",
    )
    assert ctx.anchor_entity == "settlement"
    assert ctx.anchor_id == "SET-100"
    assert ctx.process_key == "settlement"
    assert ctx.chain.contract_id == "KON-55"
    assert ctx.chain.harvest_acceptance_id == "ANH-22"


def test_agrar_settlement_reference_api_returns_full_chain():
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    with TestClient(app) as client:
        response = client.post("/process/references/agrar/settlement", json={
            "settlement_id": "SET-200",
            "contract_id": "KON-77",
            "charge_id": "CHG-5",
        })
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["anchor_id"] == "SET-200"
    assert data["chain"]["contract_id"] == "KON-77"
    assert data["chain"]["charge_id"] == "CHG-5"
