"""
Wave-15 Contract Tests: AP-Approval-Status, Workflow-Simulation, Silo-Quality, E2E-Chain

AP1: ApprovalStatusResponse — build_approval_status_response(), status mappings, can_post/can_pay
AP2: build_ap_approval_outbox_event() — alle 4 Aktionspfade
AP3: simulate_workflow() — alle 5 Szenarien (standard, rejection, escalation, four_eyes, sla_breach)
AP4: weighted_quality_snapshot() — gewichtete Durchschnitte, Leerfall, inactive lots
AP5: E2EProcessChain — links(), completeness_pct(), missing_links(), is_complete()
AP6: ChainCompletenessReport.build() — Vollständigkeitsbericht
"""
from __future__ import annotations

import pytest

from app.core.ap_approval_status import (
    APPROVAL_STATUS_TO_DOCUMENT_STATUS,
    APPROVAL_STATUS_TO_INSTANCE_STATUS,
    DOCUMENT_STATUS_TO_APPROVAL_STATUS,
    build_approval_override_resolution,
    build_approval_status_response,
)
from app.core.ap_approval_events import build_ap_approval_outbox_event
from app.domains.shared.process_events import (
    APInvoiceApprovalGranted,
    APInvoiceApprovalRequested,
    APInvoiceApproved,
    APInvoiceRejected,
)
from app.core.workflow_simulation import (
    SimulationInput,
    SimulationScenario,
    SimulationResult,
    simulate_workflow,
)
from app.core.silo_quality import weighted_quality_snapshot
from app.core.e2e_chain import (
    ChainCompletenessReport,
    E2EChainLink,
    E2EProcessChain,
)


# ---------------------------------------------------------------------------
# AP1: build_approval_status_response + status mappings
# ---------------------------------------------------------------------------

def test_approval_status_response_approved_can_post_and_pay():
    resp = build_approval_status_response(
        invoice_id="INV-1",
        tenant_id="t1",
        status="approved",
        required_approvals=1,
        approvals=[{"approved_by": "user-1"}],
        rejections=[],
        applicable_rule=None,
    )
    assert resp.can_post is True
    assert resp.can_pay is True
    assert resp.status == "approved"
    assert resp.current_approvals == 1


def test_approval_status_response_pending_cannot_post_or_pay():
    resp = build_approval_status_response(
        invoice_id="INV-2",
        tenant_id="t1",
        status="pending",
        required_approvals=2,
        approvals=[],
        rejections=[],
        applicable_rule=None,
    )
    assert resp.can_post is False
    assert resp.can_pay is False


def test_approval_status_response_rejected_cannot_post_or_pay():
    resp = build_approval_status_response(
        invoice_id="INV-3",
        tenant_id="t1",
        status="rejected",
        required_approvals=1,
        approvals=[],
        rejections=[{"approved_by": "mgr-1"}],
        applicable_rule=None,
    )
    assert resp.can_post is False
    assert resp.can_pay is False
    assert resp.explainability.status == "blocked"


def test_approval_status_to_document_status_all_states():
    assert APPROVAL_STATUS_TO_DOCUMENT_STATUS["not_requested"] == "ENTWURF"
    assert APPROVAL_STATUS_TO_DOCUMENT_STATUS["pending"] == "ZUR_FREIGABE"
    assert APPROVAL_STATUS_TO_DOCUMENT_STATUS["partially_approved"] == "TEILWEISE_FREIGEGEBEN"
    assert APPROVAL_STATUS_TO_DOCUMENT_STATUS["approved"] == "FREIGEGEBEN"
    assert APPROVAL_STATUS_TO_DOCUMENT_STATUS["rejected"] == "ABGELEHNT"


def test_document_status_to_approval_status_verbucht_is_approved():
    assert DOCUMENT_STATUS_TO_APPROVAL_STATUS["VERBUCHT"] == "approved"
    assert DOCUMENT_STATUS_TO_APPROVAL_STATUS["BEZAHLT"] == "approved"


def test_approval_override_resolution_default_scope():
    res = build_approval_override_resolution("INV-4", "t1", None)
    assert res.effective_scope == "global"
    assert res.rule_id == "ap.approval.default"


def test_approval_override_resolution_tenant_scope_with_rule():
    rule = {"id": "rule-99", "name": "Hochwert-Freigabe", "required_approvals": 2, "approval_roles": ["cfo"]}
    res = build_approval_override_resolution("INV-5", "t1", rule)
    assert res.effective_scope == "tenant"
    assert res.rule_id == "rule-99"
    assert res.effective_params["required_approvals"] == 2


def test_approval_explainability_summary_for_approved():
    resp = build_approval_status_response(
        invoice_id="INV-6",
        tenant_id="t1",
        status="approved",
        required_approvals=1,
        approvals=[{"approved_by": "boss"}],
        rejections=[],
        applicable_rule=None,
    )
    assert "freigegeben" in resp.explainability.summary.lower()


# ---------------------------------------------------------------------------
# AP2: build_ap_approval_outbox_event
# ---------------------------------------------------------------------------

class _MockOverride:
    rule_id = None


class _MockResponse:
    status: str
    required_approvals: int
    current_approvals: int
    override_resolution = _MockOverride()

    def __init__(self, status, required, current):
        self.status = status
        self.required_approvals = required
        self.current_approvals = current


def test_approval_requested_event_type():
    resp = _MockResponse("pending", 2, 0)
    event = build_ap_approval_outbox_event(
        action="approval_requested",
        invoice_id="INV-10",
        tenant_id="t1",
        actor="user-1",
        response=resp,
    )
    assert isinstance(event, APInvoiceApprovalRequested)
    assert event.invoice_id == "INV-10"
    assert event.required_approvals == 2


def test_approval_approve_when_fully_approved_returns_approved_event():
    resp = _MockResponse("approved", 1, 1)
    event = build_ap_approval_outbox_event(
        action="approval_approve",
        invoice_id="INV-11",
        tenant_id="t1",
        actor="mgr-1",
        response=resp,
    )
    assert isinstance(event, APInvoiceApproved)
    assert event.approved_by == "mgr-1"


def test_approval_approve_when_partial_returns_granted_event():
    resp = _MockResponse("partially_approved", 2, 1)
    event = build_ap_approval_outbox_event(
        action="approval_approve",
        invoice_id="INV-12",
        tenant_id="t1",
        actor="user-2",
        response=resp,
    )
    assert isinstance(event, APInvoiceApprovalGranted)
    assert event.current_approvals == 1
    assert event.required_approvals == 2


def test_approval_reject_returns_rejected_event():
    resp = _MockResponse("rejected", 1, 0)
    event = build_ap_approval_outbox_event(
        action="approval_reject",
        invoice_id="INV-13",
        tenant_id="t1",
        actor="cfo-1",
        response=resp,
    )
    assert isinstance(event, APInvoiceRejected)
    assert event.rejected_by == "cfo-1"


def test_unknown_action_returns_none():
    resp = _MockResponse("pending", 1, 0)
    event = build_ap_approval_outbox_event(
        action="invalid_action",
        invoice_id="INV-14",
        tenant_id="t1",
        actor="user-1",
        response=resp,
    )
    assert event is None


# ---------------------------------------------------------------------------
# AP3: simulate_workflow() — alle 5 Szenarien
# ---------------------------------------------------------------------------

def test_simulate_standard_approval_completes():
    inp = SimulationInput(tenant_id="t1", process_key="ap_invoice_approval",
                          scenario=SimulationScenario.STANDARD_APPROVAL)
    result = simulate_workflow(inp)
    assert result.final_status == "completed"
    assert result.schema_version == 1
    assert len(result.steps) == 3
    assert result.steps[-1].step_name == "post"


def test_simulate_rejection_final_status():
    inp = SimulationInput(tenant_id="t1", process_key="ap_invoice_approval",
                          scenario=SimulationScenario.REJECTION)
    result = simulate_workflow(inp)
    assert result.final_status == "rejected"
    assert any(s.outcome == "rejected" for s in result.steps)


def test_simulate_escalation_final_status():
    inp = SimulationInput(tenant_id="t1", process_key="ap_invoice_approval",
                          scenario=SimulationScenario.ESCALATION)
    result = simulate_workflow(inp)
    assert result.final_status == "escalated"
    assert result.explainability["total_simulated_hours"] == 72.0


def test_simulate_four_eyes_exception_completes_with_extra_step():
    inp = SimulationInput(tenant_id="t1", process_key="ap_invoice_approval",
                          scenario=SimulationScenario.FOUR_EYES_EXCEPTION)
    result = simulate_workflow(inp)
    assert result.final_status == "completed"
    assert len(result.steps) == 4
    step_names = [s.step_name for s in result.steps]
    assert "second_approval" in step_names


def test_simulate_sla_breach_escalates():
    inp = SimulationInput(tenant_id="t1", process_key="ap_invoice_approval",
                          scenario=SimulationScenario.SLA_BREACH)
    result = simulate_workflow(inp)
    assert result.final_status == "escalated"
    assert result.explainability["total_simulated_hours"] == 96.0


def test_simulate_result_carries_tenant_and_process_key():
    inp = SimulationInput(tenant_id="tenant-x", process_key="harvest_acceptance",
                          scenario=SimulationScenario.STANDARD_APPROVAL)
    result = simulate_workflow(inp)
    assert result.tenant_id == "tenant-x"
    assert result.process_key == "harvest_acceptance"


# ---------------------------------------------------------------------------
# AP4: weighted_quality_snapshot
# ---------------------------------------------------------------------------

class _Lot:
    def __init__(self, qty, moisture=None, protein=None, impurities=None, hl=None, status="active"):
        self.quantity_tons = qty
        self.moisture_pct = moisture
        self.protein_pct = protein
        self.impurities_pct = impurities
        self.hl_weight = hl
        self.status = status


def test_weighted_snapshot_empty_list():
    snap = weighted_quality_snapshot([])
    assert snap["total_quantity_tons"] == 0.0
    assert snap["lot_count"] == 0
    assert snap["moisture_avg_pct"] is None


def test_weighted_snapshot_single_lot():
    lots = [_Lot(100.0, moisture=14.5, protein=11.0, impurities=1.0, hl=75.0)]
    snap = weighted_quality_snapshot(lots)
    assert snap["total_quantity_tons"] == 100.0
    assert snap["moisture_avg_pct"] == 14.5
    assert snap["protein_avg_pct"] == 11.0
    assert snap["lot_count"] == 1


def test_weighted_snapshot_two_lots_moisture_weighted():
    lots = [
        _Lot(100.0, moisture=14.0),
        _Lot(200.0, moisture=16.0),
    ]
    snap = weighted_quality_snapshot(lots)
    # expected: (14*100 + 16*200) / 300 = 4600/300 ≈ 15.33
    assert snap["moisture_avg_pct"] == pytest.approx(15.33, abs=0.01)
    assert snap["total_quantity_tons"] == 300.0


def test_weighted_snapshot_excludes_inactive_lots():
    lots = [
        _Lot(500.0, moisture=20.0, status="inactive"),
        _Lot(100.0, moisture=14.0, status="active"),
    ]
    snap = weighted_quality_snapshot(lots)
    assert snap["lot_count"] == 1
    assert snap["moisture_avg_pct"] == 14.0


def test_weighted_snapshot_partial_metrics_are_none():
    lots = [_Lot(50.0)]  # no moisture/protein/etc.
    snap = weighted_quality_snapshot(lots)
    assert snap["moisture_avg_pct"] is None
    assert snap["protein_avg_pct"] is None


# ---------------------------------------------------------------------------
# AP5: E2EProcessChain — links, completeness, missing
# ---------------------------------------------------------------------------

def test_e2e_chain_empty_is_not_complete():
    chain = E2EProcessChain(tenant_id="t1")
    assert chain.is_complete() is False
    assert chain.completeness_pct() == 0


def test_e2e_chain_full_is_complete():
    chain = E2EProcessChain(
        tenant_id="t1",
        contract_id="C-1",
        harvest_acceptance_id="HA-1",
        quality_protocol_id="QP-1",
        settlement_id="S-1",
        ap_invoice_id="INV-1",
        journal_entry_id="JE-1",
    )
    assert chain.is_complete() is True
    assert chain.completeness_pct() == 100


def test_e2e_chain_partial_missing_links():
    chain = E2EProcessChain(
        tenant_id="t1",
        contract_id="C-1",
        harvest_acceptance_id="HA-1",
    )
    missing = chain.missing_links()
    assert "quality_protocol" in missing
    assert "settlement" in missing
    assert "ap_invoice" in missing
    assert "journal_entry" in missing
    assert "contract" not in missing


def test_e2e_chain_links_returns_six_items():
    chain = E2EProcessChain(tenant_id="t1")
    links = chain.links()
    assert len(links) == 6
    assert all(isinstance(l, E2EChainLink) for l in links)


def test_e2e_chain_completeness_pct_half():
    chain = E2EProcessChain(
        tenant_id="t1",
        contract_id="C-1",
        harvest_acceptance_id="HA-1",
        quality_protocol_id="QP-1",
    )
    # 3 of 6 present
    assert chain.completeness_pct() == 50


def test_e2e_chain_schema_version():
    chain = E2EProcessChain(tenant_id="t1")
    assert chain.schema_version == 1


# ---------------------------------------------------------------------------
# AP6: ChainCompletenessReport.build()
# ---------------------------------------------------------------------------

def test_chain_completeness_report_all_complete():
    chains = [
        E2EProcessChain(
            tenant_id="t1",
            contract_id="C-1", harvest_acceptance_id="HA-1", quality_protocol_id="QP-1",
            settlement_id="S-1", ap_invoice_id="INV-1", journal_entry_id="JE-1",
        ),
        E2EProcessChain(
            tenant_id="t1",
            contract_id="C-2", harvest_acceptance_id="HA-2", quality_protocol_id="QP-2",
            settlement_id="S-2", ap_invoice_id="INV-2", journal_entry_id="JE-2",
        ),
    ]
    report = ChainCompletenessReport.build("t1", chains)
    assert report.total_chains == 2
    assert report.complete_count == 2
    assert report.incomplete_count == 0
    assert report.completeness_pct == 100
    assert report.gaps == []


def test_chain_completeness_report_mixed():
    chains = [
        E2EProcessChain(
            tenant_id="t1",
            contract_id="C-1", harvest_acceptance_id="HA-1", quality_protocol_id="QP-1",
            settlement_id="S-1", ap_invoice_id="INV-1", journal_entry_id="JE-1",
        ),
        E2EProcessChain(tenant_id="t1", contract_id="C-2"),
    ]
    report = ChainCompletenessReport.build("t1", chains)
    assert report.complete_count == 1
    assert report.incomplete_count == 1
    assert report.completeness_pct == 50
    assert len(report.gaps) == 1
    assert "ap_invoice" in report.gaps[0]["missing"]


def test_chain_completeness_report_empty():
    report = ChainCompletenessReport.build("t1", [])
    assert report.total_chains == 0
    assert report.completeness_pct == 0
    assert report.schema_version == 1


def test_chain_completeness_report_schema_version():
    report = ChainCompletenessReport.build("t1", [])
    assert report.schema_version == 1
