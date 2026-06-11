"""Unit-Tests Folgeaktionen beim Beschaffungs-Match (DOM-PROC-004.4)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.procurement_match_service import ProcurementMatchService

pytestmark = pytest.mark.unit


def _service() -> ProcurementMatchService:
    return ProcurementMatchService(MagicMock(), "tenant-demo")


def test_create_follow_up_rejects_unknown_action():
    with pytest.raises(ValueError, match="Unbekannte Folgeaktion"):
        _service().create_follow_up(bestellnummer="DEMO-PO-001", action_type="storno", grund="Testgrund")


def test_create_follow_up_requires_grund():
    with pytest.raises(ValueError, match="Grund ist Pflicht"):
        _service().create_follow_up(bestellnummer="DEMO-PO-001", action_type="nachforderung", grund="   ")


def test_create_follow_up_eskalation_increments_stufe():
    svc = _service()
    db = svc.db
    db.execute.side_effect = [
        MagicMock(mappings=MagicMock(return_value=MagicMock(first=MagicMock(return_value={"max_stufe": 2})))),
        MagicMock(),
        MagicMock(
            mappings=MagicMock(
                return_value=MagicMock(
                    all=MagicMock(
                        return_value=[
                            {
                                "id": "x",
                                "action_type": "eskalation",
                                "ausnahme_code": None,
                                "grund": "Lieferverzug",
                                "eskalationsstufe": 3,
                                "created_at": None,
                                "created_by": None,
                            }
                        ]
                    )
                )
            )
        ),
    ]
    result = svc.create_follow_up(bestellnummer="DEMO-PO-001", action_type="eskalation", grund="Lieferverzug")
    assert result["eskalationsstufe"] == 3
    db.commit.assert_called_once()


def test_list_follow_ups_returns_empty_on_missing_table():
    svc = _service()
    svc.db.execute.side_effect = Exception("relation does not exist")
    assert svc.list_follow_ups("DEMO-PO-001") == []
