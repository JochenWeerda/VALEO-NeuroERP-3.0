"""AI-ENGINEERING-METRICS-001 — Tests für den Metrics-Script."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scripts.ai_engineering_metrics import (
    CommitRecord,
    EngMetricsReport,
    SliceMetric,
    _agent_commit_counts,
    _build_claim_map,
    _build_feat_map,
    _build_rework_map,
    _extract_slice_ids,
    _median,
    _percentile,
    _to_csv,
    compute_report,
)

pytestmark = pytest.mark.unit


def _ts(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


# ── _extract_slice_ids ─────────────────────────────────────────────────────────

class TestExtractSliceIds:
    def test_single_id(self):
        assert _extract_slice_ids("feat(fin): FIN-004-001 fertig") == ["FIN-004-001"]

    def test_multiple_ids(self):
        ids = _extract_slice_ids("feat: SEMANTIC-E2E-MATRIX-001 + O2C-001 done")
        assert "SEMANTIC-E2E-MATRIX-001" in ids
        assert "O2C-001" in ids

    def test_dotted_id(self):
        assert "DOM-FIN-004.5" in _extract_slice_ids("feat: DOM-FIN-004.5 abgeschlossen")

    def test_no_match(self):
        assert _extract_slice_ids("chore: update readme") == []

    def test_claim_message(self):
        ids = _extract_slice_ids("chore(workboard): claim WA-NOTIFY-001")
        assert "WA-NOTIFY-001" in ids


# ── _build_claim_map ───────────────────────────────────────────────────────────

class TestBuildClaimMap:
    def test_claim_extracted(self):
        commits = [
            CommitRecord("a1", _ts("2026-06-01T08:00:00+00:00"), "chore(workboard): claim MY-SLICE-001"),
        ]
        m = _build_claim_map(commits)
        assert "MY-SLICE-001" in m

    def test_first_claim_wins(self):
        commits = [
            CommitRecord("a1", _ts("2026-06-01T08:00:00+00:00"), "chore: claim MY-SLICE-001"),
            CommitRecord("a2", _ts("2026-06-02T08:00:00+00:00"), "chore: claim MY-SLICE-001"),
        ]
        m = _build_claim_map(commits)
        assert m["MY-SLICE-001"] == _ts("2026-06-01T08:00:00+00:00")

    def test_non_claim_ignored(self):
        commits = [
            CommitRecord("a1", _ts("2026-06-01T08:00:00+00:00"), "feat(fin): MY-SLICE-001 fertig"),
        ]
        m = _build_claim_map(commits)
        assert "MY-SLICE-001" not in m


# ── _build_feat_map ────────────────────────────────────────────────────────────

class TestBuildFeatMap:
    def test_feat_extracted(self):
        commits = [
            CommitRecord("b1", _ts("2026-06-05T10:00:00+00:00"), "feat(sales): MY-SLICE-001 done"),
        ]
        m = _build_feat_map(commits)
        assert "MY-SLICE-001" in m

    def test_chore_not_feat(self):
        commits = [
            CommitRecord("b1", _ts("2026-06-05T10:00:00+00:00"), "chore: MY-SLICE-001 docs"),
        ]
        m = _build_feat_map(commits)
        assert "MY-SLICE-001" not in m


# ── _build_rework_map ──────────────────────────────────────────────────────────

class TestBuildReworkMap:
    def test_fix_counted(self):
        commits = [
            CommitRecord("c1", _ts("2026-06-06T09:00:00+00:00"), "fix(fin): MY-SLICE-001 Fehler behoben"),
            CommitRecord("c2", _ts("2026-06-07T09:00:00+00:00"), "fix(fin): MY-SLICE-001 weiterer Fix"),
        ]
        m = _build_rework_map(commits)
        assert m.get("MY-SLICE-001") == 2

    def test_revert_counted(self):
        commits = [
            CommitRecord("c3", _ts("2026-06-06T09:00:00+00:00"), 'revert "feat: MY-SLICE-002 done"'),
        ]
        m = _build_rework_map(commits)
        assert m.get("MY-SLICE-002", 0) >= 1

    def test_feat_not_rework(self):
        commits = [
            CommitRecord("c4", _ts("2026-06-06T09:00:00+00:00"), "feat: MY-SLICE-003 fertig"),
        ]
        m = _build_rework_map(commits)
        assert "MY-SLICE-003" not in m


# ── Statistik ──────────────────────────────────────────────────────────────────

class TestStatistics:
    def test_median_odd(self):
        assert _median([1, 3, 5]) == 3

    def test_median_even(self):
        assert _median([2, 4]) == 3.0

    def test_median_empty(self):
        assert _median([]) is None

    def test_p90(self):
        values = list(range(1, 11))
        p90 = _percentile(values, 90)
        assert p90 is not None
        assert p90 >= 9

    def test_percentile_empty(self):
        assert _percentile([], 90) is None


# ── _agent_commit_counts ───────────────────────────────────────────────────────

class TestAgentCommitCounts:
    def test_counts_by_owner(self):
        slices = [
            {"slice_id": "A-001", "owner": "Claude"},
            {"slice_id": "A-002", "owner": "Claude"},
            {"slice_id": "B-001", "owner": "Codex"},
        ]
        counts = _agent_commit_counts(slices)
        assert counts["Claude"] == 2
        assert counts["Codex"] == 1

    def test_unknown_owner_fallback(self):
        slices = [{"slice_id": "X-001"}]
        counts = _agent_commit_counts(slices)
        assert "unknown" in counts


# ── _to_csv ────────────────────────────────────────────────────────────────────

class TestToCsv:
    def _make_report(self):
        return EngMetricsReport(
            generated_at="2026-06-26T00:00:00+00:00",
            since="2026-06-01",
            total_slices=1,
            completed_slices=1,
            slices_with_external_gates=0,
            median_cycle_time_hours=24.0,
            p90_cycle_time_hours=48.0,
            overall_rework_rate=0.1,
            slices_without_doc_files=0,
            agent_commit_counts={"Claude": 1},
            slice_details=[
                SliceMetric(
                    slice_id="TEST-001",
                    title="Test Slice",
                    owner="Claude",
                    status="completed",
                    updated="2026-06-26",
                    has_external_gates=False,
                    cycle_time_hours=24.0,
                    rework_commits=1,
                    has_doc_files=True,
                )
            ],
        )

    def test_csv_has_header(self):
        csv_out = _to_csv(self._make_report())
        assert "slice_id" in csv_out
        assert "cycle_time_hours" in csv_out

    def test_csv_has_data_row(self):
        csv_out = _to_csv(self._make_report())
        assert "TEST-001" in csv_out
        assert "24.0" in csv_out


# ── compute_report (Smoke gegen echtes Repo) ───────────────────────────────────

class TestComputeReport:
    def test_report_runs_without_error(self):
        report = compute_report(since="2026-06-01")
        assert report.total_slices > 0
        assert report.generated_at != ""

    def test_completed_slices_subset_of_total(self):
        report = compute_report(since="2026-06-01")
        assert report.completed_slices <= report.total_slices

    def test_rework_rate_between_0_and_1(self):
        report = compute_report(since="2026-06-01")
        assert 0.0 <= report.overall_rework_rate <= 1.0

    def test_agent_counts_non_empty(self):
        report = compute_report(since="2026-06-01")
        assert len(report.agent_commit_counts) > 0

    def test_slice_details_have_ids(self):
        report = compute_report(since="2026-06-01")
        for d in report.slice_details:
            assert d.slice_id != ""

    def test_no_negative_cycle_times(self):
        report = compute_report(since="2026-06-01")
        for d in report.slice_details:
            if d.cycle_time_hours is not None:
                assert d.cycle_time_hours >= 0

    def test_median_cycle_time_type(self):
        report = compute_report(since="2026-06-01")
        if report.median_cycle_time_hours is not None:
            assert isinstance(report.median_cycle_time_hours, float)

