"""Executable Unit-Tests: Admin-Suite Parity-Endpunkte (Sonar New-Code-Coverage)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.api.v1.endpoints import admin_suite_parity as parity


def test_list_readiness_evidence_flacht_details():
    evidence = SimpleNamespace(
        key="k1",
        label="Label",
        status="ok",
        source="src",
        evidence="ev",
        details=["a", "b"],
        checked_at=datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc),
    )
    readiness = SimpleNamespace(evidence=[evidence])
    with patch.object(parity.suite, "build_admin_suite_readiness", return_value=readiness):
        rows = asyncio.run(parity.list_admin_suite_readiness_evidence())
    assert rows == [
        {
            "id": "k1",
            "key": "k1",
            "label": "Label",
            "status": "ok",
            "source": "src",
            "evidence": "ev",
            "details": "a; b",
            "checked_at": evidence.checked_at.isoformat(),
        }
    ]


def test_list_setup_steps_and_migration_profiles():
    step = SimpleNamespace(
        key="s1",
        label="Schritt",
        status="open",
        target_path="/x",
        evidence="e",
        responsible="ops",
        updated_at=None,
    )
    session = SimpleNamespace(steps=[step])
    db = MagicMock()
    with patch.object(parity.suite, "_load_tenant_settings", return_value={}), patch.object(
        parity.suite, "_build_setup_session", return_value=session
    ):
        steps = asyncio.run(parity.list_setup_steps(tenant_id="t1", db=db))
    assert steps[0]["id"] == "s1"
    assert steps[0]["updated_at"] is None

    with patch.object(
        parity.suite,
        "MIGRATION_PROFILES",
        [{"key": "p1", "label": "P", "status": "available", "adapter": "x", "notes": "n"}],
    ):
        profiles = asyncio.run(parity.list_migration_profiles())
    assert profiles[0]["id"] == "p1"
    assert profiles[0]["adapter"] == "x"


def test_migration_batches_and_overview():
    db = MagicMock()
    settings = {"admin_suite_migration": {}}
    store = {
        "batches": [
            {
                "id": "b1",
                "tenant_id": "t1",
                "source_profile": "p",
                "source_ref": "r",
                "source_hash": "h",
                "mapping_version": "1",
                "dry_run": True,
                "status": "approved",
                "reconciliation": {"a": True, "b": True},
                "created_at": "c",
                "updated_at": "u",
            },
            "skip-me",
        ]
    }
    cockpit = SimpleNamespace(
        profiles=[
            SimpleNamespace(status="available"),
            SimpleNamespace(status="blocked"),
        ],
        batches=[SimpleNamespace(status="approved"), SimpleNamespace(status="draft")],
    )
    with patch.object(parity.suite, "_load_tenant_settings", return_value=settings), patch.object(
        parity.suite, "_migration_store", return_value=store
    ), patch.object(parity.suite, "_migration_cockpit", return_value=cockpit):
        batches = asyncio.run(parity.list_migration_batches(tenant_id="t1", db=db))
        overview = asyncio.run(parity.get_migration_overview(tenant_id="t1", db=db))
    assert batches[0]["id"] == "b1"
    assert batches[0]["reconciliation_ok"] is True
    assert overview["available_profiles"] == 1
    assert overview["blocked_profiles"] == 1
    assert overview["approved_batches"] == 1
    assert overview["execute_locked"] is True


def test_security_and_connectors_overview():
    humans = [SimpleNamespace(key="h", actor_type="human", notes=None, permissions=["a", "b"])]
    agents = [SimpleNamespace(key="ag", actor_type="agent", notes="n", permissions=["x"])]
    with patch.object(parity.suite, "_security_roles", return_value=humans), patch.object(
        parity.suite, "_agent_roles", return_value=agents
    ):
        sec = asyncio.run(parity.get_security_overview())
        human_rows = asyncio.run(parity.list_security_roles())
        agent_rows = asyncio.run(parity.list_security_agent_roles())
    assert sec["human_role_count"] == 1
    assert sec["agent_role_count"] == 1
    assert human_rows[0]["permission_count"] == 2
    assert agent_rows[0]["notes"] == "n"

    stt = SimpleNamespace(
        enabled=True,
        configured=True,
        base_url="http://stt",
        model="m",
        language="de",
        api_key_set=True,
    )
    imap = SimpleNamespace(
        enabled=False,
        configured=False,
        host="h",
        port=993,
        ssl=True,
        user="u",
        inbox="INBOX",
        sent="Sent",
        own_addresses=["a@b.c"],
        poll_seconds=60,
        password_set=False,
    )
    out = SimpleNamespace(stt=stt, imap=imap)
    db = MagicMock()
    with patch.object(parity.suite, "_connectors_out", return_value=out):
        capt = asyncio.run(parity.get_capture_connectors_overview(tenant_id="t1", db=db))
    assert capt["stt_enabled"] is True
    assert capt["imap_port"] == 993
    assert capt["imap_password_set"] is False


def test_update_connector_stt_and_imap():
    db = MagicMock()
    payload_stt = MagicMock()
    payload_stt.model_dump.return_value = {"enabled": True}
    payload_imap = MagicMock()
    payload_imap.model_dump.return_value = {"host": "mail"}
    out = SimpleNamespace(ok=True)
    with patch.object(parity, "save_connectors") as save, patch.object(
        parity.suite, "_connectors_out", return_value=out
    ):
        r1 = asyncio.run(parity.update_connector_stt(payload_stt, tenant_id="t1", db=db))
        r2 = asyncio.run(parity.update_connector_imap(payload_imap, tenant_id="t1", db=db))
    assert r1 is out and r2 is out
    assert save.call_count == 2
