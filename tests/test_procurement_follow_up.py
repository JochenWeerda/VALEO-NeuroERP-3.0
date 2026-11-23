"""Validierung Folgeaktionen — reine Service-Regeln ohne DB-Mocks (DOM-PROC-004.4).

DB-Pfade werden in tests/test_procurement_match_integration.py abgedeckt.
"""

from __future__ import annotations

import pytest

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

    from fastapi import HTTPException
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
