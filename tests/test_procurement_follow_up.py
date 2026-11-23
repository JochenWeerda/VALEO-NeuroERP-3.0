"""Validierung Folgeaktionen — reine Service-Regeln ohne DB-Mocks (DOM-PROC-004.4).

DB-Pfade werden in tests/test_procurement_match_integration.py abgedeckt.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.procurement_match_service import ProcurementMatchService

pytestmark = pytest.mark.unit


def test_create_follow_up_rejects_unknown_action():
    svc = ProcurementMatchService(db=None, tenant_id="tenant-demo")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unbekannte Folgeaktion"):
        svc.create_follow_up(bestellnummer="DEMO-PO-001", action_type="storno", grund="Testgrund")


def test_create_follow_up_requires_grund():
    svc = ProcurementMatchService(db=None, tenant_id="tenant-demo")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Grund ist Pflicht"):
        svc.create_follow_up(bestellnummer="DEMO-PO-001", action_type="nachforderung", grund="   ")


def test_create_follow_up_does_not_write_without_tenant_order():
    from unittest.mock import Mock

    db = Mock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    svc = ProcurementMatchService(db=db, tenant_id="tenant-a")

    with pytest.raises(ValueError, match="Bestellung nicht"):
        svc.create_follow_up(bestellnummer="PO-42", action_type="eskalation", grund="Prüfen")

    lookup = db.execute.call_args.args
    assert "tenant_id = :t" in str(lookup[0])
    assert lookup[1] == {"t": "tenant-a", "v": "PO-42"}
    db.execute.assert_called_once()
    db.commit.assert_not_called()


def test_follow_up_rest_rolls_back_without_exposing_storage_details(monkeypatch):
    from unittest.mock import Mock

    from app.api.v1.endpoints import procurement_match

    db = Mock()
    service = Mock()
    service.create_follow_up.side_effect = RuntimeError("interne Datenbankdetails")
    monkeypatch.setattr(procurement_match, "ProcurementMatchService", lambda *_: service)
    monkeypatch.setattr(procurement_match, "gepruefter_akteur_aus_request", lambda _: "actor")
    body = procurement_match.FollowUpIn(bestellnummer="PO-42", action_type="eskalation", grund="Prüfen")

    with pytest.raises(HTTPException) as error:
        procurement_match.create_follow_up(body, Mock(), db=db, tenant_id="tenant-a")

    assert error.value.status_code == 503
    assert error.value.detail == "Folgeaktion konnte nicht gespeichert werden."
    db.rollback.assert_called_once_with()


def test_follow_up_replay_leaves_the_existing_entry_unchanged(monkeypatch):
    from unittest.mock import Mock

    from app.api.v1.endpoints import procurement_match

    db = Mock()
    service = Mock()
    replay = Mock(return_value={"id": "saved", "replayed": True})
    monkeypatch.setattr(procurement_match, "ProcurementMatchService", lambda *_: service)
    monkeypatch.setattr(procurement_match, "gepruefter_akteur_aus_request", lambda _: "actor")
    monkeypatch.setattr(procurement_match, "lock_and_replay", replay)
    body = procurement_match.FollowUpIn(bestellnummer="PO-42", action_type="eskalation", grund="Prüfen")

    assert procurement_match.create_follow_up(
        body, Mock(), db=db, tenant_id="tenant-a", idempotency_key="attempt-1",
    )["id"] == "saved"

    assert replay.call_args.kwargs["tenant"] == "tenant-a"
    assert replay.call_args.kwargs["actor"] == "actor"
    service.create_follow_up.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once_with()


def test_follow_up_validation_prepares_canonical_values_without_writing():
    from unittest.mock import Mock

    db = Mock()
    db.execute.return_value.mappings.return_value.first.return_value = {"bestellnummer": "PO-42"}
    svc = ProcurementMatchService(db=db, tenant_id="tenant-a")

    assert svc.validate_follow_up(
        bestellnummer="order-id", action_type=" Eskalation ", grund=" Prüfen ",
    ) == ("PO-42", "eskalation", "Prüfen")
    db.execute.assert_called_once()
    db.commit.assert_not_called()


def test_mask_follow_up_preview_is_read_only(monkeypatch):
    import asyncio
    from unittest.mock import Mock

    from app.api.v1.endpoints import procurement_match

    db = Mock()
    db.execute.return_value.mappings.return_value.first.return_value = {"bestellnummer": "PO-42"}
    monkeypatch.setattr(procurement_match, "gepruefter_akteur_aus_request", lambda _: "actor")
    body = procurement_match.FollowUpMaskIn(action_type="reklamation", grund="Menge prüfen", _mode="dryRun")
    result = asyncio.run(procurement_match.follow_up_mask_action("PO-42", body, Mock(), db, "tenant-a"))

    assert result.success
    assert result.mode == "dryRun"
    assert db.execute.call_args.args[1] == {"t": "tenant-a", "v": "PO-42"}
    db.execute.assert_called_once()
    db.commit.assert_not_called()


@pytest.mark.parametrize("mode", ["dryRun", "execute"])
def test_follow_up_cli_and_mcp_use_the_same_rest_contract(monkeypatch, mode):
    import json
    from types import SimpleNamespace

    import httpx

    from app.api.v1.endpoints.procurement_match import FollowUpMaskIn
    from app.core.screen_definitions_domain_batch15 import build_einkauf_wareneingangsabgleich_detail
    from app.services import mcp_mask_actions, mcp_write_capability
    from valeo_cli.support import build_request

    screen = build_einkauf_wareneingangsabgleich_detail()
    action = next(entry for entry in screen["actions"] if entry["key"] == "folgeaktion")
    order = "PO/23 & #1"
    payload = {"action_type": "reklamation", "grund": "Menge prüfen"}
    audit_reason = "Wareneingang abgeglichen"
    key = "follow-up-1"
    method, path, body = build_request(
        action, screen_id=screen["id"], entity_id=order, payload=payload, mode=mode,
        audit_reason=audit_reason, idempotency_key=key,
    )

    from app.core import identity_context

    principal = SimpleNamespace(scopes=frozenset({"masks:write"}))
    monkeypatch.setattr(identity_context, "current_identity", lambda: principal)
    monkeypatch.setattr(mcp_mask_actions, "_definition", lambda *_: screen)
    monkeypatch.setattr(mcp_write_capability, "_registry", lambda: {"agent_write_phase": "entwicklung"})
    request = SimpleNamespace(
        mode=mode, idempotency_key=key,
        parameters={"screen_id": screen["id"], "action": action["key"], "entity_id": order,
                    "input": payload, "audit_reason": audit_reason, "confirm": mode == "execute"},
    )

    def target(forwarded):
        assert forwarded.method == method
        assert forwarded.url.raw_path.decode() == path
        assert list(forwarded.url.params.multi_items()) == [("bestellung", order)]
        assert forwarded.headers["authorization"] == "Bearer synthetic-test"
        assert "x-tenant-id" not in forwarded.headers
        assert json.loads(forwarded.content) == body
        parsed = FollowUpMaskIn.model_validate(body)
        assert parsed.mode == mode
        assert parsed.key == key
        assert parsed.audit_reason == audit_reason
        return httpx.Response(200, json={"success": True})

    result = mcp_mask_actions.execute(
        request, "tenant-a", "Bearer synthetic-test", transport=httpx.MockTransport(target),
    )
    assert result["success"]


@pytest.mark.parametrize("key", [None, "attempt-1"])
def test_mask_follow_up_requires_execute_metadata_before_database_access(monkeypatch, key):
    import asyncio
    from unittest.mock import Mock

    from app.api.v1.endpoints import procurement_match

    db = Mock()
    monkeypatch.setattr(procurement_match, "gepruefter_akteur_aus_request", lambda _: "actor")
    body = procurement_match.FollowUpMaskIn(
        action_type="reklamation", grund="Menge prüfen", _idempotencyKey=key,
    )
    call = procurement_match.follow_up_mask_action("PO-42", body, Mock(), db, "tenant-a")

    if key is None:
        with pytest.raises(HTTPException) as error:
            asyncio.run(call)
        assert error.value.status_code == 422
        assert "Idempotenzschlüssel" in error.value.detail
    else:
        result = asyncio.run(call)
        assert not result.success
        assert result.validationErrors[0]["field"] == "_auditReason"

    db.execute.assert_not_called()
    db.commit.assert_not_called()
