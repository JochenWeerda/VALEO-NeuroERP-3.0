"""Tests fuer P2.2 — AiEngineeringMetricsService."""

import pytest
from app.services.ai_engineering_metrics_service import AiEngineeringMetricsService


@pytest.fixture()
def svc() -> AiEngineeringMetricsService:
    return AiEngineeringMetricsService()


def test_slice_metrics_returns_list(svc: AiEngineeringMetricsService) -> None:
    metrics = svc.slice_metrics()
    assert isinstance(metrics, list)
    # Wir haben mehrere Slices committed
    # (kann auch 0 sein wenn Slices-Dir leer — Test bleibt robust)


def test_slice_metrics_structure(svc: AiEngineeringMetricsService) -> None:
    metrics = svc.slice_metrics()
    if not metrics:
        pytest.skip("Keine Slice-YAMLs vorhanden")
    m = metrics[0]
    assert "slice_id" in m
    assert "status" in m
    assert "has_tests" in m
    assert "has_all_harness_fields" in m


def test_cycle_time_summary_structure(svc: AiEngineeringMetricsService) -> None:
    summary = svc.cycle_time_summary()
    assert "total_slices" in summary
    assert "completed_slices" in summary
    assert "slices_without_tests" in summary
    assert "slices_missing_harness" in summary
    assert summary["total_slices"] >= 0


def test_coverage_summary_structure(svc: AiEngineeringMetricsService) -> None:
    summary = svc.coverage_summary()
    # coverage.xml muss nicht existieren — robuster Test
    assert isinstance(summary, dict)
    if "status" not in summary:
        assert "total_files" in summary
        assert "avg_coverage_pct" in summary


def test_gate_blocker_summary(svc: AiEngineeringMetricsService) -> None:
    summary = svc.gate_blocker_summary()
    assert "workboard_open_items" in summary
    assert "external_gate_mentions" in summary
    assert isinstance(summary["external_gate_mentions"], int)


def test_rework_indicator_structure(svc: AiEngineeringMetricsService) -> None:
    rework = svc.rework_indicator()
    assert "slices_with_incomplete_harness_or_tests" in rework
    assert "rework_rate_pct" in rework
    assert "details" in rework
    assert 0.0 <= rework["rework_rate_pct"] <= 100.0


def test_owner_distribution_is_dict(svc: AiEngineeringMetricsService) -> None:
    dist = svc.owner_distribution()
    assert isinstance(dist, dict)
    # Werte sind Zaehlungen (int >= 1)
    for owner, count in dist.items():
        assert isinstance(count, int)
        assert count >= 1


def test_full_dashboard_has_all_sections(svc: AiEngineeringMetricsService) -> None:
    dashboard = svc.full_dashboard()
    assert "generated_at" in dashboard
    assert "cycle_time" in dashboard
    assert "coverage" in dashboard
    assert "gate_blockers" in dashboard
    assert "rework" in dashboard
    assert "owner_distribution" in dashboard


def test_known_slices_detected(svc: AiEngineeringMetricsService) -> None:
    metrics = svc.slice_metrics()
    slice_ids = {m["slice_id"] for m in metrics}
    # Mindestens einer der bekannten Slices muss erkannt werden
    known = {"OPERATOR-AGENT-001", "DEV-HARNESS-CLI-001", "VALEO-WF-COCKPIT-001", "MCP-ERP-TOOLS-001"}
    assert len(known & slice_ids) >= 1, f"Bekannte Slices nicht gefunden: {known} nicht in {slice_ids}"
