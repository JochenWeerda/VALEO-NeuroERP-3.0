"""Paritaet Batch 24: Admin Suite Cockpit + Ops-Listen (Human/CI/MCP)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_listen import (
    build_admin_suite_compliance_liste,
    build_admin_suite_connectors_liste,
    build_admin_suite_devices_liste,
    build_admin_suite_diagnostics_liste,
    build_admin_suite_home_cockpit,
    build_admin_suite_operations_liste,
    build_admin_suite_setup_liste,
    build_admin_suite_system_status_liste,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"


@pytest.mark.unit
def test_admin_suite_home_is_cockpit():
    src = (PAGES / "admin-suite/index.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="admin-suite"' in src
    sd = build_admin_suite_home_cockpit()
    assert sd["mode"] == "cockpit"
    summary = {s["key"] for s in sd.get("summary") or []}
    assert {"score", "ready_count", "warning_count", "blocked_count"}.issubset(summary)
    sources = {d["key"]: d["endpoint"] for d in sd.get("dataSources") or []}
    assert sources["entity"] == "/api/v1/admin-suite/readiness"
    assert sources["evidence"] == "/api/v1/admin-suite/readiness/evidence"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("rel", "screen_id", "builder", "endpoint"),
    [
        ("admin-suite/connectors.tsx", "admin-suite/connectors", build_admin_suite_connectors_liste, "/api/v1/admin-suite/connectors"),
        ("admin-suite/devices.tsx", "admin-suite/devices", build_admin_suite_devices_liste, "/api/v1/admin-suite/devices"),
        ("admin-suite/operations.tsx", "admin-suite/operations", build_admin_suite_operations_liste, "/api/v1/admin-suite/operations"),
        ("admin-suite/compliance.tsx", "admin-suite/compliance", build_admin_suite_compliance_liste, "/api/v1/admin-suite/compliance"),
        ("admin-suite/system-status.tsx", "admin-suite/system-status", build_admin_suite_system_status_liste, "/api/v1/admin-suite/system-status"),
        ("admin-suite/diagnostics.tsx", "admin-suite/diagnostics", build_admin_suite_diagnostics_liste, "/api/v1/admin-suite/diagnostics"),
    ],
)
def test_admin_suite_ops_lists(rel, screen_id, builder, endpoint):
    src = (PAGES / rel).read_text(encoding="utf-8")
    assert "NativeListPage" in src
    assert screen_id in src
    sd = builder()
    assert sd["mode"] == "list"
    assert sd["id"] == screen_id
    # Stamm-List schreibt endpoint in dataSources[0]
    ds = (sd.get("dataSources") or [{}])[0]
    assert ds.get("endpoint") == endpoint


@pytest.mark.unit
def test_admin_suite_setup_actions_parity():
    src = (PAGES / "admin-suite/setup.tsx").read_text(encoding="utf-8")
    assert "NativeListPage" in src
    sd = build_admin_suite_setup_liste()
    tables = sd.get("tables") or []
    row_actions = {a["key"]: a for t in tables for a in (t.get("rowActions") or [])}
    assert "in_arbeit" in row_actions and "abschliessen" in row_actions
    assert row_actions["abschliessen"]["commandEndpoint"] == "/api/v1/admin-suite/setup/steps/{entity_id}"
    assert row_actions["abschliessen"]["method"] == "PATCH"


@pytest.mark.unit
def test_admin_suite_endpoints_declared():
    # Readiness/Evidence + Setup-Liste: admin_suite_parity (Godfile-Auslagerung).
    parity = (ROOT / "app/api/v1/endpoints/admin_suite_parity.py").read_text(encoding="utf-8")
    assert '"/readiness/evidence"' in parity
    assert '"/setup/steps"' in parity
