"""Paritaet Batch 23: admin/command-monitor Cockpit (Human/CI/MCP)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_stamm_batch13 import build_admin_command_monitor

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"


@pytest.mark.unit
def test_command_monitor_page_is_native_cockpit():
    src = (PAGES / "admin/command-monitor.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert "admin/command-monitor" in src
    assert "command-monitor-legacy" not in src


@pytest.mark.unit
def test_command_monitor_cockpit_parity():
    sd = build_admin_command_monitor()
    assert sd["mode"] == "cockpit"
    assert sd["id"] == "admin/command-monitor"
    assert (sd.get("layout") or {}).get("floorplan") == "cockpit"

    summary_keys = {s["key"] for s in sd.get("summary") or []}
    assert {
        "confidence_score",
        "total_commands",
        "idempotent_commands",
        "idempotent_coverage_pct",
        "human_confirmation_commands",
        "agent_ready_commands",
        "total_records",
        "execution_count",
        "tenant_count",
        "aggregate_count",
    }.issubset(summary_keys)

    tables = {t["key"]: t for t in sd.get("tables") or []}
    assert {"commands", "aggregates", "lookup_paths"}.issubset(tables)
    assert {c["key"] for c in tables["commands"]["columns"]} >= {"name"}
    assert {c["key"] for c in tables["aggregates"]["columns"]} >= {"name"}
    assert {c["key"] for c in tables["lookup_paths"]["columns"]} >= {"path"}

    sources = {d["key"]: d["endpoint"] for d in sd.get("dataSources") or []}
    assert sources.get("entity") == "/api/v1/process/actions/idempotency/overview"
    assert sources.get("commands") == "/api/v1/process/actions/idempotency/commands"
    assert sources.get("aggregates") == "/api/v1/process/actions/idempotency/aggregates"
    assert sources.get("lookup_paths") == "/api/v1/process/actions/idempotency/lookup-paths"

    # Kein gefaehrlicher Stamm-Stub (Artikel-Detail / Bearbeiten ohne Endpunkt).
    assert sd.get("identityField") is None
    action_keys = {a["key"] for a in sd.get("actions") or []}
    assert "bearbeiten" not in action_keys
    assert "refresh" in action_keys


@pytest.mark.unit
def test_idempotency_list_endpoints_declared_in_source():
    src = (ROOT / "app/api/v1/endpoints/process_kernel_api.py").read_text(encoding="utf-8")
    assert '"/actions/idempotency/commands"' in src
    assert '"/actions/idempotency/aggregates"' in src
    assert '"/actions/idempotency/lookup-paths"' in src
    assert "total_commands" in src and "idempotent_coverage_pct" in src
