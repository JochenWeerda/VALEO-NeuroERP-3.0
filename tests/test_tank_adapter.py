from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.tank_adapter_service import TankAdapterError, TankAdapterService

pytestmark = pytest.mark.unit
PAYLOAD = {
    "kennzeichen": "B-VA 123",
    "artikel": "Diesel",
    "menge": 42.5,
    "zeitstempel": "2026-08-21T10:00:00+00:00",
    "customer_id": "C-1",
    "billable": True,
}


def _first(value):  # noqa: ANN001, ANN202
    result = MagicMock()
    result.mappings.return_value.first.return_value = value
    return result


def test_ingest_rejects_missing_identity() -> None:
    with pytest.raises(TankAdapterError, match="External-ID"):
        TankAdapterService(MagicMock(), "tenant-1").ingest(
            "", "", PAYLOAD, actor="adapter"
        )


def test_idempotency_rejects_changed_payload() -> None:
    db = MagicMock()
    existing = MagicMock()
    existing.mappings.return_value.one.return_value = {
        "id": "i1",
        "status": "received",
        "payload_hash": "different",
    }
    db.execute.side_effect = [_first(None), existing]
    with pytest.raises(TankAdapterError, match="abweichendem Payload"):
        TankAdapterService(db, "tenant-1").ingest(
            "pump-a", "42", PAYLOAD, actor="adapter"
        )


def test_validation_creates_delivery_note_rule() -> None:
    db = MagicMock()
    locked = _first(
        {
            "id": "i1",
            "status": "received",
            "payload": PAYLOAD,
            "payload_hash": "hash",
            "rule_result": {},
            "zapfung_id": None,
            "delivery_handover_id": None,
        }
    )
    db.execute.side_effect = [locked, MagicMock(), MagicMock()]
    result = TankAdapterService(db, "tenant-1").validate(
        "i1", actor="user", reason="Datensatz pruefen"
    )
    assert (
        result["status"] == "validated"
        and result["rule_result"]["create_delivery_note"] is True
    )


def test_validation_routes_invalid_quantity_to_error() -> None:
    db = MagicMock()
    locked = _first(
        {
            "id": "i1",
            "status": "received",
            "payload": {**PAYLOAD, "menge": 0},
            "payload_hash": "hash",
            "rule_result": {},
            "zapfung_id": None,
            "delivery_handover_id": None,
        }
    )
    db.execute.side_effect = [locked, MagicMock(), MagicMock()]
    result = TankAdapterService(db, "tenant-1").validate(
        "i1", actor="user", reason="Datensatz pruefen"
    )
    assert result["status"] == "error" and result["validation_errors"]


def test_process_is_idempotent_after_completion() -> None:
    db = MagicMock()
    db.execute.return_value = _first(
        {
            "id": "i1",
            "status": "processed",
            "payload": PAYLOAD,
            "payload_hash": "hash",
            "rule_result": {},
            "zapfung_id": "z1",
            "delivery_handover_id": "o1",
        }
    )
    result = TankAdapterService(db, "tenant-1").process(
        "i1", actor="user", reason="Uebernahme bestaetigt"
    )
    assert result["idempotent"] is True and result["zapfung_id"] == "z1"


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("tankstelle/adapter-inbox")
    assert definition and definition["layout"]["tableProfile"] == "inventory"
    assert _check_readiness(definition)["generatorReady"] is True
