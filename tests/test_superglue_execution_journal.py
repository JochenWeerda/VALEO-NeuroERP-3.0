"""COV-INT-002: Tests fuer superglue_execution_journal.py.

Abdeckung: append_execution_journal_entry, list, build_summary,
find_latest_by_idempotency_key.
"""
from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from app.integrations.services.superglue_execution_journal import (
    append_execution_journal_entry,
    list_execution_journal_entries,
    build_execution_journal_summary,
    find_latest_execution_by_idempotency_key,
)


def _ts(offset_s: float = 0.0) -> datetime:
    from datetime import timedelta
    return datetime(2026, 5, 8, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=offset_s)


# ---------------------------------------------------------------------------
# append + list round-trip
# ---------------------------------------------------------------------------

def test_append_and_list(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        entry = append_execution_journal_entry(
            tenant_id="t1",
            correlation_id="corr-001",
            tool_id="tool-A",
            execution_mode="sync",
            target_kind="api",
            result_status="success",
            started_at=_ts(0),
            finished_at=_ts(1),
        )
        entries = list_execution_journal_entries(limit=10)

    assert isinstance(entry, dict)
    assert entry["tenant_id"] == "t1"
    assert entry["result_status"] == "success"
    assert entry["latency_ms"] == 1000
    assert len(entries) == 1


def test_append_multiple_entries(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        for i in range(5):
            append_execution_journal_entry(
                tenant_id="t1",
                correlation_id=f"corr-{i:03d}",
                tool_id="tool-A",
                execution_mode="sync",
                target_kind="api",
                result_status="success",
                started_at=_ts(i),
                finished_at=_ts(i + 0.5),
            )
        entries = list_execution_journal_entries(limit=10)

    assert len(entries) == 5


def test_list_respects_limit(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        for i in range(10):
            append_execution_journal_entry(
                tenant_id="t1", correlation_id=f"c{i}", tool_id="t", execution_mode="sync",
                target_kind="api", result_status="success", started_at=_ts(i), finished_at=_ts(i + 0.1),
            )
        entries = list_execution_journal_entries(limit=3)

    assert len(entries) <= 3


# ---------------------------------------------------------------------------
# latency_ms computation
# ---------------------------------------------------------------------------

def test_latency_ms_computed_correctly(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        entry = append_execution_journal_entry(
            tenant_id="t1", correlation_id="c1", tool_id="t", execution_mode="sync",
            target_kind="api", result_status="success",
            started_at=_ts(0), finished_at=_ts(2.5),
        )
    assert entry["latency_ms"] == 2500


def test_latency_ms_non_negative_for_same_timestamps(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        entry = append_execution_journal_entry(
            tenant_id="t1", correlation_id="c1", tool_id="t", execution_mode="sync",
            target_kind="api", result_status="success",
            started_at=_ts(0), finished_at=_ts(0),
        )
    assert entry["latency_ms"] >= 0


# ---------------------------------------------------------------------------
# build_execution_journal_summary
# ---------------------------------------------------------------------------

def test_summary_error_count(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        for status in ("success", "error", "error"):
            append_execution_journal_entry(
                tenant_id="t1", correlation_id=f"c-{status}", tool_id="t", execution_mode="sync",
                target_kind="api", result_status=status, started_at=_ts(0), finished_at=_ts(1),
            )
        summary = build_execution_journal_summary(limit=10)

    assert summary["entry_count"] == 3
    assert summary["error_count"] == 2


def test_summary_empty_journal(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        summary = build_execution_journal_summary()
    assert summary["entry_count"] == 0
    assert summary["error_count"] == 0


# ---------------------------------------------------------------------------
# find_latest_execution_by_idempotency_key
# ---------------------------------------------------------------------------

def test_find_by_idempotency_key_returns_latest(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        append_execution_journal_entry(
            tenant_id="t1", correlation_id="c1", tool_id="tool-A", execution_mode="sync",
            target_kind="api", result_status="success", started_at=_ts(0), finished_at=_ts(1),
            idempotency_key="ikey-001",
        )
        found = find_latest_execution_by_idempotency_key(
            tenant_id="t1", tool_id="tool-A", idempotency_key="ikey-001"
        )

    assert found is not None
    assert found["idempotency_key"] == "ikey-001"


def test_find_by_idempotency_key_returns_none_when_missing(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    with patch("app.integrations.services.superglue_execution_journal._storage_path", return_value=journal_path):
        result = find_latest_execution_by_idempotency_key(
            tenant_id="t1", tool_id="tool-A", idempotency_key="nonexistent"
        )
    assert result is None
