"""Paritaet Batch 25: Rest Admin-Suite Cockpits (Migration/Security/KI/Connectoren/POS)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_listen import (
    build_admin_suite_connectoren_cockpit,
    build_admin_suite_ki_anbieter_cockpit,
    build_admin_suite_migration_cockpit,
    build_admin_suite_pos_fiscalization_cockpit,
    build_admin_suite_security_cockpit,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
ADMIN_API = ROOT / "app/api/v1/endpoints/admin_suite.py"
ADMIN_PARITY_API = ROOT / "app/api/v1/endpoints/admin_suite_parity.py"
POS_API = ROOT / "app/api/v1/endpoints/pos_fiscalization.py"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("rel", "screen_id", "builder"),
    [
        ("admin-suite/migration.tsx", "admin-suite/migration", build_admin_suite_migration_cockpit),
        ("admin-suite/security.tsx", "admin-suite/security", build_admin_suite_security_cockpit),
        ("admin-suite/ki-anbieter.tsx", "admin-suite/ki-anbieter", build_admin_suite_ki_anbieter_cockpit),
        ("admin-suite/connectoren.tsx", "admin-suite/connectoren", build_admin_suite_connectoren_cockpit),
        ("admin-suite/pos-fiscalization.tsx", "admin-suite/pos-fiscalization", build_admin_suite_pos_fiscalization_cockpit),
    ],
)
def test_admin_suite_batch25_pages_are_cockpits(rel, screen_id, builder):
    src = (PAGES / rel).read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert f'screenId="{screen_id}"' in src
    sd = builder()
    assert sd["mode"] == "cockpit"
    assert sd["id"] == screen_id


@pytest.mark.unit
def test_migration_actions_and_endpoints():
    sd = build_admin_suite_migration_cockpit()
    actions = {a["key"]: a for a in sd.get("actions") or []}
    assert actions["dry_run_anlegen"]["commandEndpoint"] == "/api/v1/admin-suite/migration/batches"
    assert actions["dry_run_anlegen"]["method"] == "POST"
    sources = {d["key"]: d["endpoint"] for d in sd.get("dataSources") or []}
    assert sources["entity"] == "/api/v1/admin-suite/migration/overview"
    assert sources["profiles"] == "/api/v1/admin-suite/migration/profiles"
    assert sources["batches"] == "/api/v1/admin-suite/migration/batches"
    row_actions = {
        a["key"]: a
        for t in (sd.get("tables") or [])
        for a in (t.get("rowActions") or [])
    }
    assert row_actions["freigeben"]["commandEndpoint"] == (
        "/api/v1/admin-suite/migration/batches/{entity_id}/approve"
    )
    api = ADMIN_PARITY_API.read_text(encoding="utf-8") + ADMIN_API.read_text(encoding="utf-8")
    assert '"/migration/profiles"' in api
    assert '"/migration/batches"' in api
    assert '"/migration/overview"' in api


@pytest.mark.unit
def test_security_simulate_parity():
    sd = build_admin_suite_security_cockpit()
    actions = {a["key"]: a for a in sd.get("actions") or []}
    assert actions["simulieren"]["commandEndpoint"] == "/api/v1/admin-suite/security/simulate"
    assert actions["simulieren"]["method"] == "POST"
    sources = {d["key"]: d["endpoint"] for d in sd.get("dataSources") or []}
    assert sources["roles"] == "/api/v1/admin-suite/security/roles"
    assert sources["agent_roles"] == "/api/v1/admin-suite/security/agent-roles"
    api = ADMIN_PARITY_API.read_text(encoding="utf-8") + ADMIN_API.read_text(encoding="utf-8")
    assert '"/security/roles"' in api
    assert '"/security/agent-roles"' in api
    assert "resolved_roles" in api


@pytest.mark.unit
def test_ki_anbieter_put_and_test():
    sd = build_admin_suite_ki_anbieter_cockpit()
    actions = {a["key"]: a for a in sd.get("actions") or []}
    assert actions["speichern"]["commandEndpoint"] == "/api/v1/admin-suite/llm-gateway"
    assert actions["speichern"]["method"] == "PUT"
    assert actions["testen"]["commandEndpoint"] == "/api/v1/admin-suite/llm-gateway/test"
    assert actions["testen"]["method"] == "POST"
    field_keys = {f["key"] for f in actions["speichern"]["inputFields"]}
    assert {"provider", "base_url", "model", "api_key", "temperature", "enabled"} <= field_keys


@pytest.mark.unit
def test_connectoren_flat_endpoints():
    sd = build_admin_suite_connectoren_cockpit()
    actions = {a["key"]: a for a in sd.get("actions") or []}
    assert actions["stt_speichern"]["commandEndpoint"] == "/api/v1/admin-suite/capture-connectors/stt"
    assert actions["imap_speichern"]["commandEndpoint"] == "/api/v1/admin-suite/capture-connectors/imap"
    assert actions["stt_testen"]["commandEndpoint"] == "/api/v1/admin-suite/capture-connectors/stt/test"
    assert actions["imap_testen"]["commandEndpoint"] == "/api/v1/admin-suite/capture-connectors/imap/test"
    assert actions["imap_abrufen"]["commandEndpoint"] == "/api/v1/admin-suite/capture-connectors/imap/poll"
    api = ADMIN_PARITY_API.read_text(encoding="utf-8") + ADMIN_API.read_text(encoding="utf-8")
    assert '"/capture-connectors/stt"' in api
    assert '"/capture-connectors/imap"' in api
    assert '"/capture-connectors/overview"' in api


@pytest.mark.unit
def test_pos_fiscalization_parity():
    sd = build_admin_suite_pos_fiscalization_cockpit()
    actions = {a["key"]: a for a in sd.get("actions") or []}
    assert actions["speichern"]["commandEndpoint"] == "/api/v1/pos/fiscalization/config"
    assert actions["speichern"]["method"] == "PUT"
    field_keys = {f["key"] for f in actions["speichern"]["inputFields"]}
    assert {"provider", "cash_register_id", "client_id", "terminal_id"} <= field_keys
    sources = {d["key"]: d["endpoint"] for d in sd.get("dataSources") or []}
    assert sources["entity"] == "/api/v1/pos/fiscalization/overview"
    assert sources["products"] == "/api/v1/pos/fiscalization/products"
    api = POS_API.read_text(encoding="utf-8")
    assert '"/overview"' in api
    assert '"/products"' in api
