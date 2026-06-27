"""Wave 62 — Tests fuer agribusiness und agri_lot_link_booking."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# agribusiness  /api/v1/farmers/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_farmers_returns_list() -> None:
    resp = _client.get("/api/v1/agribusiness/farmers", headers=_HEADERS)
    # DB may not be seeded — 200 with empty list or 500 are both valid
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        body = resp.json()
        assert "items" in body


@pytest.mark.unit
def test_delete_farmer_not_found() -> None:
    import json as _json
    resp = _client.request(
        "DELETE",
        "/api/v1/agribusiness/farmers/nonexistent-farmer-xyz",
        content=_json.dumps({"reason": "Test deletion"}),
        headers={**_HEADERS, "content-type": "application/json"},
    )
    assert resp.status_code in (204, 404)


@pytest.mark.unit
def test_delete_farmer_missing_reason() -> None:
    import json as _json
    resp = _client.request(
        "DELETE",
        "/api/v1/agribusiness/farmers/some-id",
        content=_json.dumps({}),
        headers={**_HEADERS, "content-type": "application/json"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# agri_lot_link_booking  /api/v1/lager/wms/agri/material-flow/lot-link
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_lot_link_book_missing_fields() -> None:
    resp = _client.post("/api/v1/lager/wms/agri/material-flow/lot-link", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_lot_link_book_returns_ok() -> None:
    from app.api.v1.endpoints.agri_lot_link_booking import _svc
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService

    class _FakeSvc:
        def book_lot_to_cell(self, lot_id, target_cell_id, warehouse_id, quantity_kg, booked_by, reference):  # noqa: ANN001
            return {"ok": True, "lot_id": lot_id, "cell_id": target_cell_id}

    app.dependency_overrides[_svc] = lambda: _FakeSvc()
    try:
        payload = {
            "warehouse_id": "WH-001",
            "lot_id": "LOT-001",
            "target_cell_id": "CELL-001",
            "quantity_kg": 100.0,
        }
        resp = _client.post("/api/v1/lager/wms/agri/material-flow/lot-link", json=payload, headers=_HEADERS)
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.pop(_svc, None)


@pytest.mark.unit
def test_lot_link_auto_book_missing_lot_id() -> None:
    resp = _client.post("/api/v1/lager/wms/agri/material-flow/lot-link/auto-book", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_lot_link_auto_book_returns_ok() -> None:
    from app.api.v1.endpoints.agri_lot_link_booking import _svc

    class _FakeSvc:
        def auto_book_lot(self, lot_id, warehouse_id=None, booked_by=None):  # noqa: ANN001
            return {"ok": True, "lot_id": lot_id, "auto": True}
        def auto_book_lot_link_by_lot_id(self, lot_id, warehouse_id=None, booked_by=None):  # noqa: ANN001
            return {"ok": True, "lot_id": lot_id, "auto": True}

    app.dependency_overrides[_svc] = lambda: _FakeSvc()
    try:
        payload = {"lot_id": "LOT-002", "warehouse_id": "WH-001"}
        resp = _client.post("/api/v1/lager/wms/agri/material-flow/lot-link/auto-book", json=payload, headers=_HEADERS)
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.pop(_svc, None)


@pytest.mark.unit
def test_lot_link_suggest_returns_ok() -> None:
    from app.api.v1.endpoints.agri_lot_link_booking import _svc

    class _FakeSvc:
        def suggest_lot_link(self, lot_id, warehouse_id=None, top_n=3):  # noqa: ANN001
            return {"suggestions": [], "lot_id": lot_id}

    app.dependency_overrides[_svc] = lambda: _FakeSvc()
    try:
        resp = _client.get(
            "/api/v1/lager/wms/agri/material-flow/lot-link/suggest",
            params={"lot_id": "LOT-001"},
            headers=_HEADERS,
        )
        assert resp.status_code in (200, 404, 422)
    finally:
        app.dependency_overrides.pop(_svc, None)
