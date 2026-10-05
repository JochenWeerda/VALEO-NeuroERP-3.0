from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.services.production_control_service import (
    ProductionControlError,
    ProductionControlService,
    valid_status_transition,
)
from main import app

pytestmark = pytest.mark.unit

HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
    "X-User-ID": "production-test-user",
}


def test_status_transition_contract_covers_rework() -> None:
    assert valid_status_transition("queued", "released")
    assert valid_status_transition("running", "completed")
    assert valid_status_transition("completed", "rework")
    assert not valid_status_transition("cancelled", "running")


def test_register_rejects_unknown_operation() -> None:
    db = MagicMock()
    service = ProductionControlService(db, "tenant-1")
    with pytest.raises(ProductionControlError, match="Unbekannter Produktionsvorgang"):
        service.register({"operation_type": "unknown"}, actor="tester")
    db.execute.assert_not_called()


def test_list_page_is_tenant_scoped_and_paginated() -> None:
    db = MagicMock()
    total = MagicMock()
    total.scalar_one.return_value = 12
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "op-1", "operation_type": "mill_run"}]
    db.execute.side_effect = [total, rows]
    result = ProductionControlService(db, "tenant-1").list_page(page=2, page_size=5, work_center="M1")
    assert result == {"items": [{"id": "op-1", "operation_type": "mill_run"}], "total": 12, "page": 2, "page_size": 5}
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_sync_projects_only_current_tenant() -> None:
    db = MagicMock()
    result = MagicMock(rowcount=3)
    db.execute.return_value = result
    assert ProductionControlService(db, "tenant-a").sync_production_orders(actor="tester", reason="Initialer Abgleich") == {"synchronized": 3}
    assert db.execute.call_args.args[1]["tid"] == "tenant-a"
    db.commit.assert_called_once()


def test_production_control_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("produktion/produktionsleitstand")
    assert definition is not None
    assert definition["adapter"]["temporary"] is False
    assert definition["tables"][0]["serverPagination"] is True
    assert definition["layout"]["tableProfile"] == "inventory"
    assert _check_readiness(definition)["generatorReady"] is True


def test_production_control_route_is_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.production_control as endpoint

    class FakeService:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == HEADERS["X-Tenant-ID"]

        def list_page(self, **kwargs):  # noqa: ANN003
            assert kwargs["operation_type"] == "mill_run"
            return {"items": [], "total": 0, "page": 1, "page_size": 50}

    monkeypatch.setattr(endpoint, "ProductionControlService", FakeService)
    response = TestClient(app, raise_server_exceptions=False).get(
        "/api/v1/production-control/operations?operation_type=mill_run", headers=HEADERS
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0
