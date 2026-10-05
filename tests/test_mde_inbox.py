from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.services.mobile_sync_service import (
    MobileSyncService,
    next_mobile_failure_status,
    validate_mobile_event_payload,
)
from main import app


pytestmark = pytest.mark.unit

HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
    "X-User-ID": "mde-test-user",
}


def test_inventory_count_payload_contract() -> None:
    assert validate_mobile_event_payload(
        "inventory_count",
        {"warehouse_id": "LAGER-1", "article_id": "ART-1", "counted_qty": 12.5},
    ) == []
    assert validate_mobile_event_payload("inventory_count", {"article_id": "ART-1"}) == [
        "warehouse_id fehlt",
        "counted_qty fehlt",
    ]


def test_enqueue_rejects_invalid_payload_before_persistence() -> None:
    db = MagicMock()
    service = MobileSyncService(db, "tenant-1")

    result = service.enqueue_events(
        "MDE-01",
        [{"event_type": "inventory_count", "payload": {"article_id": "ART-1"}, "idempotency_key": "idem-1"}],
    )

    assert result[0]["status"] == "rejected"
    assert "warehouse_id fehlt" in result[0]["reason"]
    db.execute.assert_not_called()


def test_third_failed_attempt_is_quarantined() -> None:
    assert next_mobile_failure_status(0) == "failed"
    assert next_mobile_failure_status(1) == "failed"
    assert next_mobile_failure_status(2) == "quarantined"


def test_delivery_confirmation_uses_canonical_tenant_scoped_logistics_table() -> None:
    db = MagicMock()
    db.execute.return_value.rowcount = 1
    service = MobileSyncService(db, "tenant-1")

    service._handle_delivery_confirmation({"tour_id": "tour-1", "stop_id": "stop-1"})

    statement = str(db.execute.call_args.args[0])
    params = db.execute.call_args.args[1]
    assert "domain_logistics.tour_stops" in statement
    assert "tenant_id = :tid" in statement
    assert params["tid"] == "tenant-1"


def test_retry_requires_failed_or_quarantined_state() -> None:
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "evt-1",
        "sync_status": "done",
        "retry_count": 0,
    }
    service = MobileSyncService(db, "tenant-1")

    with pytest.raises(ValueError, match="nicht wiederholt"):
        service.retry_event("evt-1", actor="tester", reason="erneute Pruefung")


def test_mde_queue_endpoint_uses_server_pagination(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.mobile_sync as endpoint

    class FakeService:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == HEADERS["X-Tenant-ID"]

        def list_queue_page(self, **kwargs):  # noqa: ANN003
            assert kwargs["page"] == 2
            assert kwargs["page_size"] == 25
            assert kwargs["status"] == "quarantined"
            return {"items": [{"id": "evt-1", "sync_status": "quarantined"}], "total": 26, "page": 2, "page_size": 25}

    monkeypatch.setattr(endpoint, "MobileSyncService", FakeService)
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/v1/mobile/sync-queue?page=2&page_size=25&status=quarantined",
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 26


def test_mde_screen_definition_is_native_audit_worklist() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("schnittstelle/mde-inbox")

    assert definition is not None
    assert definition["adapter"]["temporary"] is False
    assert definition["layout"]["floorplan"] == "worklist"
    assert definition["layout"]["density"] == "expertDense"
    assert definition["layout"]["contextRail"] == "audit"
    assert definition["layout"]["tableProfile"] == "audit"
    assert definition["tables"][0]["serverPagination"] is True
    assert definition["tables"][0]["dataSourceKey"] == "queue"
    assert _check_readiness(definition)["generatorReady"] is True
