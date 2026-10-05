from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.services.billing_batch_service import BillingBatchError, BillingBatchService
from main import app

pytestmark = pytest.mark.unit
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
    "X-User-ID": "billing-test-user",
}


def test_create_rejects_empty_batch() -> None:
    db = MagicMock()
    with pytest.raises(BillingBatchError, match="keine Zeilen"):
        BillingBatchService(db, "tenant-1").create(
            {"batch_type": "sales_invoice", "lines": []}, actor="maker"
        )
    db.execute.assert_not_called()


def test_create_rejects_unknown_type() -> None:
    db = MagicMock()
    with pytest.raises(BillingBatchError, match="Unbekannter"):
        BillingBatchService(db, "tenant-1").create(
            {"batch_type": "unknown", "lines": [{}]}, actor="maker"
        )


def test_list_page_is_tenant_scoped() -> None:
    db = MagicMock()
    total = MagicMock()
    total.scalar_one.return_value = 2
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "b1"}]
    db.execute.side_effect = [total, rows]
    result = BillingBatchService(db, "tenant-1").list_page(status="draft")
    assert result["total"] == 2
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_four_eyes_release_rejects_maker() -> None:
    db = MagicMock()
    locked = MagicMock()
    locked.mappings.return_value.first.return_value = {
        "id": "b1",
        "status": "validated",
        "maker": "same",
        "failed_lines": 0,
    }
    db.execute.return_value = locked
    with pytest.raises(BillingBatchError, match="Vier-Augen"):
        BillingBatchService(db, "tenant-1").release(
            "b1", actor="same", reason="Eigene Freigabe"
        )


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("finance/rechnungstapel")
    assert definition and definition["layout"]["tableProfile"] == "financial"
    assert _check_readiness(definition)["generatorReady"] is True


def test_route_is_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.billing_batch as endpoint

    class FakeService:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == HEADERS["X-Tenant-ID"]

        def list_page(self, **kwargs):  # noqa: ANN003
            return {"items": [], "total": 0, "page": 1, "page_size": 50}

    monkeypatch.setattr(endpoint, "BillingBatchService", FakeService)
    response = TestClient(app, raise_server_exceptions=False).get(
        "/api/v1/billing-batches", headers=HEADERS
    )
    assert response.status_code == 200
