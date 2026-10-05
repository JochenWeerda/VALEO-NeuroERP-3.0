from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.services.foreign_goods_worklist_service import (
    ForeignGoodsError,
    ForeignGoodsWorklistService,
)
from main import app

pytestmark = pytest.mark.unit
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
    "X-User-ID": "foreign-goods-test-user",
}


def _locked(**overrides):  # noqa: ANN003, ANN202
    result = MagicMock()
    item = {
        "id": "fg-1",
        "status": "eingelagert",
        "warehouse_id": "WH-1",
        "lagerort": "A-1",
        "menge_aktuell": Decimal("10"),
    }
    item.update(overrides)
    result.mappings.return_value.first.return_value = item
    return result


def test_list_page_is_tenant_scoped_and_paginated() -> None:
    db = MagicMock()
    count = MagicMock()
    count.scalar_one.return_value = 3
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "fg-1"}]
    db.execute.side_effect = [count, rows]
    result = ForeignGoodsWorklistService(db, "tenant-1").list_page(
        page=2, page_size=25, owner_id="owner-1"
    )
    assert result == {"items": [{"id": "fg-1"}], "total": 3, "page": 2, "page_size": 25}
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_transfer_rejects_completed_item() -> None:
    db = MagicMock()
    db.execute.return_value = _locked(status="ausgelagert")
    with pytest.raises(ForeignGoodsError, match="Erledigte"):
        ForeignGoodsWorklistService(db, "tenant-1").transfer(
            "fg-1",
            warehouse_id="WH-2",
            location="B-1",
            actor="user",
            reason="Umlagerung geplant",
        )


def test_complete_rejects_quantity_above_stock() -> None:
    db = MagicMock()
    db.execute.return_value = _locked()
    with pytest.raises(ForeignGoodsError, match="Restmenge"):
        ForeignGoodsWorklistService(db, "tenant-1").complete(
            "fg-1",
            actor="user",
            reason="Auslagerung geplant",
            remaining_quantity=Decimal("11"),
        )


def test_complete_writes_audit_and_commits() -> None:
    db = MagicMock()
    db.execute.side_effect = [_locked(), MagicMock(), MagicMock()]
    result = ForeignGoodsWorklistService(db, "tenant-1").complete(
        "fg-1",
        actor="user",
        reason="Vollstaendig abgeholt",
        remaining_quantity=Decimal("0"),
    )
    assert result["status"] == "ausgelagert"
    assert db.execute.call_args_list[-1].args[1]["tid"] == "tenant-1"
    db.commit.assert_called_once()


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("lager/fremdware")
    assert definition and definition["layout"]["tableProfile"] == "inventory"
    assert _check_readiness(definition)["generatorReady"] is True


def test_route_is_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.foreign_goods_worklist as endpoint

    class FakeService:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == HEADERS["X-Tenant-ID"]

        def list_page(self, **kwargs):  # noqa: ANN003
            return {"items": [], "total": 0, "page": 1, "page_size": 50}

    monkeypatch.setattr(endpoint, "ForeignGoodsWorklistService", FakeService)
    response = TestClient(app, raise_server_exceptions=False).get(
        "/api/v1/foreign-goods", headers=HEADERS
    )
    assert response.status_code == 200
