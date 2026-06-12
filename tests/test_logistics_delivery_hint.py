"""Unit-Tests: Logistik Read-Spine Lieferschein-Referenz (LOG-SPINE-RAND-001)."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.v1.endpoints import logistics_tours


def test_lookup_sales_delivery_note_returns_none_when_empty_ref():
    db = MagicMock()
    assert logistics_tours._lookup_sales_delivery_note(db, "   ", "tenant-1") is None
    db.execute.assert_not_called()


def test_lookup_sales_delivery_note_formats_row():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "dn-uuid-1",
        "delivery_note_number": "2026000042",
        "status": "draft",
        "delivery_date": date(2026, 6, 10),
        "customer_id": "K-100",
        "sales_order_id": None,
    }
    out = logistics_tours._lookup_sales_delivery_note(db, "2026000042", "00000000-0000-0000-0000-000000000001")
    assert out is not None
    assert out["delivery_note_number"] == "2026000042"
    assert out["status"] == "draft"
    assert out["delivery_date"] == "2026-06-10"
    assert out["customer_id"] == "K-100"
    assert out["sales_order_id"] is None


def test_resolve_sales_delivery_note_by_ref_requires_tenant():
    from main import app

    client = TestClient(app, raise_server_exceptions=True)
    res = client.get(
        "/api/v1/logistik/sales-delivery-note-by-ref?ref=2026000001",
        headers={"Authorization": "Bearer dev-token"},
    )
    assert res.status_code == 422
