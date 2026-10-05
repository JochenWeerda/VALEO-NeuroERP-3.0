from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.document_control_projection import DocumentControlProjectionService
from app.services.document_control_service import DocumentControlService

pytestmark = pytest.mark.unit


def test_upsert_projected_skips_resolved_cases() -> None:
    db = MagicMock()
    existing = MagicMock()
    existing.mappings.return_value.first.return_value = {"id": "ex-1", "status": "resolved"}
    db.execute.return_value = existing
    result = DocumentControlService(db, "tenant-1").upsert_projected(
        {
            "exception_type": "open_purchase_order",
            "document_ref": "PO-1",
            "source_key": "proj:open_purchase_order:PO-1",
            "reason": "Live-Projektion Belegkontrolle",
        },
        actor="projector",
    )
    assert result["projection"] == "skipped"
    db.commit.assert_not_called()


def test_upsert_projected_refreshes_open_case() -> None:
    db = MagicMock()
    select_result = MagicMock()
    select_result.mappings.return_value.first.return_value = {"id": "ex-2", "status": "open"}
    update_result = MagicMock()
    audit_result = MagicMock()
    db.execute.side_effect = [select_result, update_result, audit_result]
    result = DocumentControlService(db, "tenant-1").upsert_projected(
        {
            "exception_type": "uninvoiced_delivery_note",
            "document_ref": "LS-9",
            "document_number": "LS-9",
            "source_key": "proj:uninvoiced_delivery_note:LS-9",
            "notes": "Projiziert: nicht fakturierter Lieferschein",
            "reason": "Live-Projektion Belegkontrolle",
        },
        actor="projector",
    )
    assert result == {"id": "ex-2", "status": "open", "projection": "refreshed"}
    db.commit.assert_called_once()


def test_projection_refresh_is_tenant_scoped_and_idempotent() -> None:
    db = MagicMock()
    control = MagicMock()
    control.upsert_projected.side_effect = [
        {"id": "a", "projection": "created"},
        {"id": "a", "projection": "refreshed"},
        {"id": "b", "projection": "skipped"},
    ]

    def collector(_db, tenant_id):  # noqa: ANN001
        assert tenant_id == "tenant-1"
        return [
            {"exception_type": "open_purchase_order", "document_ref": "PO-1", "reason": "Live-Projektion Belegkontrolle"},
            {"exception_type": "open_purchase_order", "document_ref": "PO-1", "reason": "Live-Projektion Belegkontrolle"},
            {"exception_type": "blocked_delivery_note", "document_ref": "LS-1", "reason": "Live-Projektion Belegkontrolle"},
        ]

    service = DocumentControlProjectionService(db, "tenant-1", collectors=[collector])
    service.control = control
    result = service.refresh(actor="projector")
    assert result["collected"] == 3
    assert result["created"] == 1
    assert result["refreshed"] == 1
    assert result["skipped"] == 1
    assert result["tenant_id"] == "tenant-1"


def test_project_endpoint_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.document_control as endpoint
    from fastapi.testclient import TestClient
    from main import app

    class FakeProjection:
        def __init__(self, db, tenant_id):  # noqa: ANN001
            assert tenant_id == "00000000-0000-0000-0000-000000000001"

        def refresh(self, *, actor: str):
            assert actor == "beleg-test-user"
            return {"tenant_id": "00000000-0000-0000-0000-000000000001", "collected": 2, "created": 1, "refreshed": 1, "skipped": 0}

    monkeypatch.setattr(endpoint, "DocumentControlProjectionService", FakeProjection)
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/document-control/project",
        headers={
            "Authorization": "Bearer dev-token",
            "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
            "X-User-ID": "beleg-test-user",
        },
    )
    assert response.status_code == 200
    assert response.json()["created"] == 1
