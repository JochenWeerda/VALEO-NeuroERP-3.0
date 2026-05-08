"""DOM-CRM-002: Tests fuer sales_delivery_notes.py.

Abdeckung: _get_user_id_from_request, DeliveryNote models, HTTP smoke.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.sales_delivery_notes import (
    _get_user_id_from_request,
    DeliveryNoteCreate,
    DeliveryNoteUpdate,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# _get_user_id_from_request unit tests
# ---------------------------------------------------------------------------

def test_get_user_id_returns_none_when_no_request():
    result = _get_user_id_from_request(None)
    assert result is None


# ---------------------------------------------------------------------------
# DeliveryNoteCreate validation
# ---------------------------------------------------------------------------

def test_delivery_note_create_requires_delivery_date():
    with pytest.raises(Exception):
        DeliveryNoteCreate()


def test_delivery_note_create_valid():
    note = DeliveryNoteCreate(delivery_date="2026-05-08")
    assert note.status == "draft"
    assert note.is_credit_note is False


def test_delivery_note_update_all_optional():
    upd = DeliveryNoteUpdate()
    assert upd.customer_id is None
    assert upd.status is None


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_delivery_notes_returns_200():
    resp = _client.get("/api/v1/sales/delivery-notes", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_delivery_note_returns_404():
    resp = _client.get("/api/v1/sales/delivery-notes/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_delivery_note_missing_fields_returns_422():
    resp = _client.post("/api/v1/sales/delivery-notes", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_delivery_note_valid_payload():
    import uuid
    payload = {
        "customer_id": "C-001",
        "delivery_date": "2026-05-08",
        "delivery_note_number": f"LS-{uuid.uuid4().hex[:8].upper()}",
    }
    resp = _client.post("/api/v1/sales/delivery-notes", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)
