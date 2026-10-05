from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.services.inventory_auxiliary_service import InventoryAuxiliaryError, InventoryAuxiliaryService, payload_hash
from main import app

pytestmark = pytest.mark.unit
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "00000000-0000-0000-0000-000000000001", "X-User-ID": "inventory-test-user"}


def test_payload_hash_is_stable() -> None:
    assert payload_hash([{"b": 2, "a": 1}]) == payload_hash([{"a": 1, "b": 2}])


def test_import_rejects_hash_mismatch() -> None:
    db = MagicMock()
    count = MagicMock()
    count.mappings.return_value.first.return_value = {"id": "c1", "warehouse_id": "w1", "status": "open"}
    db.execute.return_value = count
    with pytest.raises(InventoryAuxiliaryError, match="Hash"):
        InventoryAuxiliaryService(db, "tenant-1").create(count_id="c1", batch_type="count_import",
            actor="maker", reason="Kontrollierter Import", import_rows=[{"line_id": "l1", "counted_qty": 2}], declared_hash="0" * 64)


def test_list_page_is_tenant_scoped() -> None:
    db = MagicMock()
    total = MagicMock()
    total.scalar_one.return_value = 4
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "b1"}]
    db.execute.side_effect = [total, rows]
    result = InventoryAuxiliaryService(db, "tenant-1").list_page(page=2, page_size=2, status="reviewed")
    assert result["total"] == 4 and result["page"] == 2
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_four_eyes_rejects_maker_as_checker() -> None:
    db = MagicMock()
    locked = MagicMock()
    locked.mappings.return_value.first.return_value = {
        "id": "b1", "status": "reviewed", "batch_type": "opening_balance", "maker": "same",
        "payload": [], "inventory_count_id": "c1",
    }
    db.execute.return_value = locked
    with pytest.raises(InventoryAuxiliaryError, match="Vier-Augen"):
        InventoryAuxiliaryService(db, "tenant-1").transition("b1", target="approved", actor="same", reason="Eigene Freigabe")


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition
    definition = get_screen_definition("lager/inventur-nebenlaeufe")
    assert definition and definition["layout"]["tableProfile"] == "inventory"
    assert _check_readiness(definition)["generatorReady"] is True


def test_route_is_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.inventory_auxiliary as endpoint
    class FakeService:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == HEADERS["X-Tenant-ID"]
        def list_page(self, **kwargs):  # noqa: ANN003
            return {"items": [], "total": 0, "page": 1, "page_size": 50}
    monkeypatch.setattr(endpoint, "InventoryAuxiliaryService", FakeService)
    response = TestClient(app, raise_server_exceptions=False).get("/api/v1/inventory/auxiliary/batches", headers=HEADERS)
    assert response.status_code == 200
