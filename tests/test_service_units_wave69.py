"""Wave 69 — Unit-Tests fuer AiEngineeringMetricsService und FiBuChain (pure logic)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# AiEngineeringMetricsService  (reads git/docs — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_coverage_summary_structure() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    s = svc.coverage_summary()
    assert "total_files" in s
    assert "avg_coverage_pct" in s
    assert isinstance(s["total_files"], int)


@pytest.mark.unit
def test_cycle_time_summary_structure() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    s = svc.cycle_time_summary()
    assert "total_slices" in s
    assert "completed_slices" in s
    assert "avg_cycle_time_days" in s


@pytest.mark.unit
def test_gate_blocker_summary_structure() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    s = svc.gate_blocker_summary()
    assert "workboard_open_items" in s
    assert "hinweis" in s


@pytest.mark.unit
def test_owner_distribution_returns_dict() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    dist = svc.owner_distribution()
    assert isinstance(dist, dict)
    assert len(dist) > 0
    # All values should be counts
    assert all(isinstance(v, int) for v in dist.values())


@pytest.mark.unit
def test_rework_indicator_structure() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    r = svc.rework_indicator()
    assert "rework_rate_pct" in r
    assert isinstance(r["rework_rate_pct"], (int, float))


@pytest.mark.unit
def test_slice_metrics_returns_list() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    metrics = svc.slice_metrics()
    assert isinstance(metrics, list)


@pytest.mark.unit
def test_full_dashboard_contains_all_sections() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    dashboard = svc.full_dashboard()
    for key in ("generated_at", "cycle_time", "coverage", "gate_blockers", "rework", "owner_distribution"):
        assert key in dashboard


@pytest.mark.unit
def test_full_dashboard_generated_at_is_timestamp() -> None:
    from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService
    svc = AiEngineeringMetricsService()
    dashboard = svc.full_dashboard()
    assert "T" in dashboard["generated_at"]  # ISO timestamp format


# ---------------------------------------------------------------------------
# FiBuChain (semantic_e2e_chain_service)  — pure in-memory chain execution
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fibu_chain_run_returns_result() -> None:
    from app.services.semantic_e2e_chain_service import FiBuChain, ChainResult
    chain = FiBuChain()
    result = chain.run({"tenant_id": "T001", "document_id": "INV-001"})
    assert isinstance(result, ChainResult)


@pytest.mark.unit
def test_fibu_chain_result_has_steps() -> None:
    from app.services.semantic_e2e_chain_service import FiBuChain
    chain = FiBuChain()
    result = chain.run({"tenant_id": "T001"})
    # failed_steps is a list (empty if all OK, else contains failed step names)
    assert isinstance(result.failed_steps, list)


@pytest.mark.unit
def test_fibu_chain_result_has_invariant_violations() -> None:
    from app.services.semantic_e2e_chain_service import FiBuChain
    chain = FiBuChain()
    result = chain.run({"tenant_id": "T001"})
    assert isinstance(result.invariant_violations, list)


@pytest.mark.unit
def test_fibu_chain_all_ok_type() -> None:
    from app.services.semantic_e2e_chain_service import FiBuChain
    chain = FiBuChain()
    result = chain.run({"tenant_id": "T001"})
    assert isinstance(result.all_ok, bool)


@pytest.mark.unit
def test_fibu_chain_empty_context_runs_without_exception() -> None:
    from app.services.semantic_e2e_chain_service import FiBuChain
    chain = FiBuChain()
    # Should not raise even with minimal context
    result = chain.run({})
    assert result is not None
