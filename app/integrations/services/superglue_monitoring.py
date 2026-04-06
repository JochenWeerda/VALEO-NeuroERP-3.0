"""Monitoring and admin summaries for Superglue connector operations."""

from __future__ import annotations

from typing import Any

from app.integrations.services.superglue_connector_registry import list_superglue_connector_bindings
from app.integrations.services.superglue_execution_journal import build_execution_journal_summary, list_execution_journal_entries
from app.integrations.services.superglue_quarantine import build_quarantine_summary


def build_superglue_admin_overview(tenant_id: str) -> dict[str, Any]:
    bindings = list_superglue_connector_bindings(tenant_id)
    journal = build_execution_journal_summary(limit=50)
    quarantine = build_quarantine_summary()
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "connector_count": len(bindings),
        "connectors": [
            {
                "connector_key": binding.connector_key,
                "tool_id": binding.tool_id,
                "target_kind": binding.target_kind,
                "execution_modes": list(binding.execution_modes),
            }
            for binding in bindings
        ],
        "journal": {
            "entry_count": journal["entry_count"],
            "error_count": journal["error_count"],
            "artifact_count": journal.get("artifact_count", 0),
        },
        "quarantine": {
            "open_count": quarantine["open_count"],
            "dead_letter_count": quarantine.get("dead_letter_count", 0),
        },
        "schema_version": 1,
    }


def build_superglue_monitoring_summary(tenant_id: str | None = None) -> dict[str, Any]:
    journal_entries = list_execution_journal_entries(limit=1000)
    if tenant_id:
        journal_entries = [entry for entry in journal_entries if str(entry.get("tenant_id")) == tenant_id]
    total_latency = sum(int(entry.get("latency_ms") or 0) for entry in journal_entries)
    connector_metrics: dict[str, dict[str, Any]] = {}
    for entry in journal_entries:
        tool_id = str(entry.get("tool_id") or "unknown")
        bucket = connector_metrics.setdefault(
            tool_id,
            {
                "tool_id": tool_id,
                "runs": 0,
                "errors": 0,
                "replays": 0,
                "total_cost_cents": 0,
                "average_latency_ms": 0,
            },
        )
        bucket["runs"] += 1
        if entry.get("result_status") != "success":
            bucket["errors"] += 1
        if entry.get("replayed_from_correlation_id"):
            bucket["replays"] += 1
        bucket["total_cost_cents"] += int(entry.get("cost_cents") or 0)
        bucket["average_latency_ms"] += int(entry.get("latency_ms") or 0)
    for bucket in connector_metrics.values():
        if bucket["runs"]:
            bucket["average_latency_ms"] = int(bucket["average_latency_ms"] / bucket["runs"])
            bucket["error_rate_pct"] = round((bucket["errors"] / bucket["runs"]) * 100, 1)
        else:
            bucket["error_rate_pct"] = 0.0
    quarantine = build_quarantine_summary()
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "run_count": len(journal_entries),
        "average_latency_ms": int(total_latency / len(journal_entries)) if journal_entries else 0,
        "total_cost_cents": sum(int(entry.get("cost_cents") or 0) for entry in journal_entries),
        "artifact_count": sum(len(entry.get("artifacts") or []) for entry in journal_entries),
        "connectors": list(connector_metrics.values()),
        "quarantine": {
            "open_count": quarantine["open_count"],
            "dead_letter_count": quarantine.get("dead_letter_count", 0),
        },
        "schema_version": 1,
    }
