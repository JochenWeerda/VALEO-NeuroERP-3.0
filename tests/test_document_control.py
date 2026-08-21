from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.services.document_control_service import (
    DocumentControlError,
    DocumentControlService,
    valid_status_transition,
)
from main import app

pytestmark = pytest.mark.unit

HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
    "X-User-ID": "beleg-test-user",
}


def test_status_transition_contract() -> None:
    assert valid_status_transition("open", "assigned")
    assert valid_status_transition("assigned", "resolved")
    assert not valid_status_transition("resolved", "open")


def test_register_rejects_unknown_type() -> None:
    db = MagicMock()
    service = DocumentControlService(db, "tenant-1")
    with pytest.raises(DocumentControlError, match="Unbekannter Ausnahme-Typ"):
        service.register_exception(
            {"exception_type": "unknown", "document_ref": "PO-1", "reason": "ungueltiger Typ"},
            actor="tester",
        )
    db.execute.assert_not_called()


def test_list_page_is_tenant_scoped_and_paginated() -> None:
    db = MagicMock()
    total = MagicMock()
    total.scalar_one.return_value = 42
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "ex-1", "exception_type": "open_purchase_order"}]
    db.execute.side_effect = [total, rows]
    result = DocumentControlService(db, "tenant-1").list_page(page=2, page_size=10, assigned_user="jw")
    assert result["total"] == 42
    assert result["page"] == 2
    assert result["page_size"] == 10
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_document_control_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("auswertungen/beleg-kontrolle")
    assert definition is not None
    assert definition["adapter"]["temporary"] is False
    assert definition["tables"][0]["serverPagination"] is True
    assert definition["layout"]["floorplan"] == "worklist"
    assert _check_readiness(definition)["generatorReady"] is True


def test_document_control_routes_are_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.document_control as endpoint

    class FakeService:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == HEADERS["X-Tenant-ID"]

        def list_page(self, **kwargs):  # noqa: ANN003
            assert kwargs["page"] == 1
            assert kwargs["exception_type"] == "uninvoiced_delivery_note"
            return {"items": [], "total": 0, "page": 1, "page_size": 25}

    monkeypatch.setattr(endpoint, "DocumentControlService", FakeService)
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/v1/document-control/exceptions?exception_type=uninvoiced_delivery_note",
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0
