"""Paritaet Batch 23: Command-Monitor Cockpit + Rohware-Intake (Human/CI/MCP)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_intake_weighing import build_intake_rohware
from app.core.screen_definitions_stamm_batch13 import build_admin_command_monitor
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
SPECIALIZED = ROOT / "packages/frontend-web/src/components/mask-builder/specialized"


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
    # Listen/Overview liegen seit Godfile-Auslagerung in process_kernel_idempotency_lists.
    src = (ROOT / "app/api/v1/endpoints/process_kernel_idempotency_lists.py").read_text(encoding="utf-8")
    assert '"/actions/idempotency/commands"' in src
    assert '"/actions/idempotency/aggregates"' in src
    assert '"/actions/idempotency/lookup-paths"' in src
    assert "total_commands" in src and "idempotent_coverage_pct" in src


@pytest.mark.unit
def test_rohware_page_is_intake_weighing():
    src = (PAGES / "annahme/rohware.tsx").read_text(encoding="utf-8")
    assert "IntakeWeighingPage" in src
    assert 'screenId="annahme/rohware"' in src
    intake = (SPECIALIZED / "intake/intake.tsx").read_text(encoding="utf-8")
    assert "'annahme/rohware'" in intake
    assert "RohwareSurface" in intake
    assert "annahme/rohware" in SPECIALIZED_SCREENS["intake"]


@pytest.mark.unit
def test_rohware_intake_field_and_endpoint_parity():
    sd = build_intake_rohware()
    assert sd["mode"] == "wizard"
    assert sd["specialized"] == {"type": "intake", "id": "annahme/rohware"}
    field_keys = {f["key"] for f in sd.get("fields") or []}
    assert {
        "lieferant",
        "kennzeichen",
        "lieferscheinNr",
        "datum",
        "artikel",
        "bruttoKg",
        "taraKg",
        "lagerZiel",
        "feuchtePct",
        "besatzPct",
        "fallzahl",
        "customer_id",
    }.issubset(field_keys)
    submit = next(a for a in sd["actions"] if a["key"] == "submit")
    flow = submit.get("inputFlow") or {}
    assert flow.get("submitEndpoint") == "/api/v1/agrar/harvest-acceptance/rohware"
    assert flow.get("method") == "POST"

    api_src = (ROOT / "app/api/v1/endpoints/harvest_acceptance.py").read_text(encoding="utf-8")
    assert '"/rohware"' in api_src
    assert "class RohwareAcceptanceCreate" in api_src
    ctrl = (SPECIALIZED / "intake/rohware-controller.ts").read_text(encoding="utf-8")
    assert "/api/v1/agrar/harvest-acceptance/rohware" in ctrl
