from __future__ import annotations
"""
Wave 5 Paket B — E2E-Referenzkette & Workflow-Simulation
Tests ohne DB-Zugriff und ohne FastAPI-Client.
"""
import pytest

from app.core.e2e_chain import (
    E2EChainLink,
    E2EProcessChain,
    ChainCompletenessReport,
)
from app.core.workflow_simulation import (
    SimulationScenario,
    SimulationInput,
    SimulationResult,
    SimulationStepResult,
    simulate_workflow,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _full_chain(tenant_id: str = "T1") -> E2EProcessChain:
    """Eine vollstaendige E2E-Kette mit allen Gliedern."""
    return E2EProcessChain(
        tenant_id=tenant_id,
        contract_id="CTR-001",
        harvest_acceptance_id="HA-001",
        quality_protocol_id="QP-001",
        settlement_id="SET-001",
        ap_invoice_id="INV-001",
        journal_entry_id="JE-001",
    )


def _empty_chain(tenant_id: str = "T1") -> E2EProcessChain:
    """Eine leere E2E-Kette ohne gesetzte IDs."""
    return E2EProcessChain(tenant_id=tenant_id)


def _sim_input(scenario: SimulationScenario) -> SimulationInput:
    return SimulationInput(
        tenant_id="T1",
        process_key="ap_invoice_approval",
        scenario=scenario,
    )


# ── E2EProcessChain Tests ──────────────────────────────────────────────────────

def test_e2e_chain_schema_version():
    chain = E2EProcessChain(tenant_id="T1")
    assert chain.schema_version == 1


def test_e2e_chain_links_returns_six():
    chain = _full_chain()
    assert len(chain.links()) == 6


def test_e2e_chain_completeness_pct_empty():
    chain = _empty_chain()
    assert chain.completeness_pct() == 0


def test_e2e_chain_completeness_pct_full():
    chain = _full_chain()
    assert chain.completeness_pct() == 100


def test_e2e_chain_completeness_pct_half():
    chain = E2EProcessChain(
        tenant_id="T1",
        contract_id="CTR-001",
        harvest_acceptance_id="HA-001",
        quality_protocol_id="QP-001",
        # settlement_id, ap_invoice_id, journal_entry_id fehlen
    )
    assert chain.completeness_pct() == 50


def test_e2e_chain_is_complete_true():
    chain = _full_chain()
    assert chain.is_complete() is True


def test_e2e_chain_is_complete_false():
    chain = _empty_chain()
    assert chain.is_complete() is False


def test_e2e_chain_missing_links_correct():
    chain = E2EProcessChain(
        tenant_id="T1",
        contract_id="CTR-001",
        # Alle anderen fehlen
    )
    missing = chain.missing_links()
    assert "contract" not in missing
    assert "harvest_acceptance" in missing
    assert "quality_protocol" in missing
    assert "settlement" in missing
    assert "ap_invoice" in missing
    assert "journal_entry" in missing


# ── ChainCompletenessReport Tests ─────────────────────────────────────────────

def test_chain_completeness_report_schema_version():
    report = ChainCompletenessReport.build("T1", [])
    assert report.schema_version == 1


def test_chain_completeness_report_build_empty():
    report = ChainCompletenessReport.build("T1", [])
    assert report.total_chains == 0
    assert report.complete_count == 0
    assert report.incomplete_count == 0
    assert report.completeness_pct == 0
    assert report.gaps == []


def test_chain_completeness_report_build_mixed():
    chains = [_full_chain("T1"), _empty_chain("T1")]
    report = ChainCompletenessReport.build("T1", chains)
    assert report.total_chains == 2
    assert report.complete_count == 1
    assert report.incomplete_count == 1
    assert report.completeness_pct == 50
    assert len(report.gaps) == 1


def test_chain_completeness_report_all_complete():
    chains = [_full_chain("T1"), _full_chain("T1")]
    report = ChainCompletenessReport.build("T1", chains)
    assert report.total_chains == 2
    assert report.complete_count == 2
    assert report.incomplete_count == 0
    assert report.completeness_pct == 100
    assert report.gaps == []


# ── WorkflowSimulation Tests ───────────────────────────────────────────────────

def test_simulate_standard_approval_returns_completed():
    result = simulate_workflow(_sim_input(SimulationScenario.STANDARD_APPROVAL))
    assert result.final_status == "completed"
    assert len(result.steps) == 3


def test_simulate_rejection_returns_rejected():
    result = simulate_workflow(_sim_input(SimulationScenario.REJECTION))
    assert result.final_status == "rejected"
    assert any(s.outcome == "rejected" for s in result.steps)


def test_simulate_escalation_returns_escalated():
    result = simulate_workflow(_sim_input(SimulationScenario.ESCALATION))
    assert result.final_status == "escalated"
    assert any(s.outcome == "escalated" for s in result.steps)


def test_simulate_four_eyes_exception_completed():
    result = simulate_workflow(_sim_input(SimulationScenario.FOUR_EYES_EXCEPTION))
    assert result.final_status == "completed"
    assert any(s.step_name == "second_approval" for s in result.steps)


def test_simulate_sla_breach_escalated():
    result = simulate_workflow(_sim_input(SimulationScenario.SLA_BREACH))
    assert result.final_status == "escalated"
    # SLA breach step should have 96 hours
    breach_step = next(s for s in result.steps if s.elapsed_hours == 96.0)
    assert breach_step is not None


def test_simulation_result_schema_version():
    result = simulate_workflow(_sim_input(SimulationScenario.STANDARD_APPROVAL))
    assert result.schema_version == 1


def test_simulation_explainability_has_step_count():
    result = simulate_workflow(_sim_input(SimulationScenario.STANDARD_APPROVAL))
    assert "step_count" in result.explainability
    assert result.explainability["step_count"] == len(result.steps)


def test_simulation_steps_elapsed_hours_nonzero_for_approval():
    result = simulate_workflow(_sim_input(SimulationScenario.STANDARD_APPROVAL))
    total = sum(s.elapsed_hours for s in result.steps)
    assert total > 0
    # Standard approval: 0.0 + 12.0 + 0.5 = 12.5
    assert total == 12.5
