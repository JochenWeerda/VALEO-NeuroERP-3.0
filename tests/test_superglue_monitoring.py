"""COV-INT-002: Tests fuer superglue_monitoring.py.

Abdeckung: build_superglue_admin_overview, build_superglue_monitoring_summary.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from app.integrations.services.superglue_monitoring import (
    build_superglue_admin_overview,
    build_superglue_monitoring_summary,
)


def _ts(offset_s: float = 0.0) -> datetime:
    from datetime import timedelta
    return datetime(2026, 5, 8, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=offset_s)


def _patch_journal(tmp_path: Path):
    return patch(
        "app.integrations.services.superglue_execution_journal._storage_path",
        return_value=tmp_path / "journal.jsonl",
    )


# ---------------------------------------------------------------------------
# build_superglue_monitoring_summary
# ---------------------------------------------------------------------------

def test_monitoring_summary_empty(tmp_path):
    with _patch_journal(tmp_path):
        summary = build_superglue_monitoring_summary()
    assert isinstance(summary, dict)
    assert summary.get("run_count", 0) == 0


def test_monitoring_summary_counts_runs(tmp_path):
    from app.integrations.services.superglue_execution_journal import append_execution_journal_entry
    with _patch_journal(tmp_path):
        for status in ("success", "error", "success"):
            append_execution_journal_entry(
                tenant_id="t1", correlation_id=f"c-{status}", tool_id="tool-A",
                execution_mode="sync", target_kind="api", result_status=status,
                started_at=_ts(0), finished_at=_ts(1),
            )
        summary = build_superglue_monitoring_summary()
    assert summary.get("run_count", 0) == 3


def test_monitoring_summary_tenant_filter(tmp_path):
    from app.integrations.services.superglue_execution_journal import append_execution_journal_entry
    with _patch_journal(tmp_path):
        append_execution_journal_entry(
            tenant_id="t1", correlation_id="c1", tool_id="tool-A",
            execution_mode="sync", target_kind="api", result_status="success",
            started_at=_ts(0), finished_at=_ts(1),
        )
        append_execution_journal_entry(
            tenant_id="t2", correlation_id="c2", tool_id="tool-B",
            execution_mode="sync", target_kind="api", result_status="error",
            started_at=_ts(0), finished_at=_ts(1),
        )
        summary_t1 = build_superglue_monitoring_summary(tenant_id="t1")
        summary_t2 = build_superglue_monitoring_summary(tenant_id="t2")
    assert summary_t1.get("run_count", 0) == 1
    assert summary_t2.get("run_count", 0) == 1


# ---------------------------------------------------------------------------
# build_superglue_admin_overview
# ---------------------------------------------------------------------------

def test_admin_overview_schema(tmp_path):
    mock_bindings = []
    with (
        _patch_journal(tmp_path),
        patch("app.integrations.services.superglue_monitoring.list_superglue_connector_bindings", return_value=mock_bindings),
        patch("app.integrations.services.superglue_quarantine.build_quarantine_summary", return_value={"open_count": 0, "dead_letter_count": 0}),
    ):
        overview = build_superglue_admin_overview("t1")
    assert overview["tenant_id"] == "t1"
    assert overview["provider_key"] == "superglue"
    assert "connector_count" in overview
    assert "journal" in overview
    assert "quarantine" in overview
    assert overview["schema_version"] == 1


def test_admin_overview_connector_count(tmp_path):
    mock_binding = MagicMock()
    mock_binding.connector_key = "erpnext"
    mock_binding.tool_id = "tool-1"
    mock_binding.target_kind = "api"
    mock_binding.execution_modes = {"sync"}
    with (
        _patch_journal(tmp_path),
        patch("app.integrations.services.superglue_monitoring.list_superglue_connector_bindings", return_value=[mock_binding]),
        patch("app.integrations.services.superglue_quarantine.build_quarantine_summary", return_value={"open_count": 0, "dead_letter_count": 0}),
    ):
        overview = build_superglue_admin_overview("t1")
    assert overview["connector_count"] == 1
    assert overview["connectors"][0]["connector_key"] == "erpnext"
