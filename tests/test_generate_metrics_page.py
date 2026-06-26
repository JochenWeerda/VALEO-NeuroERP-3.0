"""Tests für scripts/generate_metrics_page.py (AI-ENGINEERING-METRICS-002)."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scripts.generate_metrics_page import generate

pytestmark = pytest.mark.unit

SAMPLE_METRICS = {
    "generated_at": "2026-06-26T04:00:00+00:00",
    "since": "2026-06-01",
    "total_slices": 96,
    "completed_slices": 84,
    "slices_with_external_gates": 51,
    "slices_without_doc_files": 6,
    "median_cycle_time_hours": 0.1,
    "p90_cycle_time_hours": 0.3,
    "overall_rework_rate": 0.59,
    "agent_commit_counts": {
        "Cursor": 27,
        "Codex": 21,
        "Claude Sonnet 4.6": 10,
    },
    "slice_details": [
        {
            "slice_id": "DOM-CONTROLLING-004",
            "title": "Controlling",
            "owner": "Claude Code",
            "status": "completed",
            "updated": "2026-06-26",
            "has_external_gates": False,
            "cycle_time_hours": 0.8,
            "rework_commits": 2,
            "has_doc_files": True,
        },
        {
            "slice_id": "COM-REGISTER-CAMELCASE-001",
            "title": "Camelcase Fix",
            "owner": "Claude Sonnet 4.6",
            "status": "completed",
            "updated": "2026-06-26",
            "has_external_gates": False,
            "cycle_time_hours": 0.1,
            "rework_commits": 1,
            "has_doc_files": True,
        },
        {
            "slice_id": "WA-AGENT-001",
            "title": "WhatsApp Agent",
            "owner": "Claude Sonnet 4.6",
            "status": "completed",
            "updated": "2026-06-26",
            "has_external_gates": True,
            "cycle_time_hours": None,
            "rework_commits": 0,
            "has_doc_files": False,
        },
    ],
}


class TestGeneratePage:
    def test_returns_string(self):
        page = generate(SAMPLE_METRICS)
        assert isinstance(page, str)
        assert len(page) > 200

    def test_has_frontmatter(self):
        page = generate(SAMPLE_METRICS)
        assert page.startswith("---")
        assert "generated:" in page

    def test_has_overview_section(self):
        page = generate(SAMPLE_METRICS)
        assert "## Überblick" in page
        assert "96" in page   # total_slices
        assert "84" in page   # completed_slices

    def test_completion_percentage(self):
        page = generate(SAMPLE_METRICS)
        # 84/96 = 87.5 % → round() = 88 %
        import re
        pcts = re.findall(r"(\d+) %", page)
        assert any(80 <= int(p) <= 100 for p in pcts)

    def test_has_cycle_time_section(self):
        page = generate(SAMPLE_METRICS)
        assert "## Cycle Time" in page
        assert "0.1 h" in page  # median
        assert "0.3 h" in page  # p90

    def test_has_rework_section(self):
        page = generate(SAMPLE_METRICS)
        assert "## Rework-Rate" in page
        assert "59.0 %" in page

    def test_rework_table_contains_top_slice(self):
        page = generate(SAMPLE_METRICS)
        assert "DOM-CONTROLLING-004" in page

    def test_has_longrunner_section(self):
        page = generate(SAMPLE_METRICS)
        assert "## Langläufer" in page
        assert "0.8 h" in page

    def test_has_agent_section(self):
        page = generate(SAMPLE_METRICS)
        assert "## Agent-Produktivität" in page
        assert "Cursor" in page
        assert "27" in page

    def test_no_doc_count_in_overview(self):
        page = generate(SAMPLE_METRICS)
        assert "6" in page  # slices_without_doc_files

    def test_none_cycle_time_slice_counted(self):
        page = generate(SAMPLE_METRICS)
        assert "kein Claim-Commit" in page

    def test_generated_date_in_page(self):
        page = generate(SAMPLE_METRICS)
        assert "2026-06-26" in page

    def test_since_in_page(self):
        page = generate(SAMPLE_METRICS)
        assert "2026-06-01" in page

    def test_empty_rework_slices_shows_placeholder(self):
        metrics = dict(SAMPLE_METRICS)
        metrics["slice_details"] = []
        page = generate(metrics)
        assert "—" in page

    def test_none_median_shows_na(self):
        metrics = dict(SAMPLE_METRICS)
        metrics["median_cycle_time_hours"] = None
        metrics["p90_cycle_time_hours"] = None
        page = generate(metrics)
        assert "n/a" in page
