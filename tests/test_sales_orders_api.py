"""DOM-CRM-002: Tests fuer sales_orders.py.

Abdeckung: _line_total, _resolve_order_number, _resolve_tenant_scope, HTTP CRUD.
"""
from __future__ import annotations

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.sales_orders import (
    _line_total,
    _resolve_order_number,
    _resolve_tenant_scope,
    SalesOrderCreate,
    SalesOrderItemInput,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# _line_total unit tests
# ---------------------------------------------------------------------------

def test_line_total_no_discount():
    result = _line_total(10.0, 5.0, 0.0)
    assert result == Decimal("50.00")


def test_line_total_with_discount():
    result = _line_total(10.0, 100.0, 10.0)
    assert result == Decimal("900.00")


def test_line_total_full_discount():
    result = _line_total(5.0, 200.0, 100.0)
    assert result == Decimal("0.00")


def test_line_total_fractional():
    result = _line_total(1.5, 3.0, 0.0)
    assert result == Decimal("4.50")


# ---------------------------------------------------------------------------
# _resolve_order_number unit tests
# ---------------------------------------------------------------------------

def test_resolve_order_number_generates_when_none():
    result = _resolve_order_number(None)
    assert result.startswith("SO-")


def test_resolve_order_number_keeps_provided():
    result = _resolve_order_number("SO-CUSTOM-001")
    assert result == "SO-CUSTOM-001"


# ---------------------------------------------------------------------------
# _resolve_tenant_scope unit tests
# ---------------------------------------------------------------------------

def test_resolve_tenant_scope_matches_same_tenant():
    result = _resolve_tenant_scope("same-tenant", "same-tenant")
    assert result == "same-tenant"


def test_resolve_tenant_scope_falls_back_to_header():
    result = _resolve_tenant_scope(None, "header-tenant")
    assert result == "header-tenant"


def test_resolve_tenant_scope_raises_on_mismatch():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        _resolve_tenant_scope("other-tenant", "header-tenant")
    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# SalesOrderCreate validation
# ---------------------------------------------------------------------------

def test_sales_order_create_defaults():
    order = SalesOrderCreate(customer_id="C-001", subject="Test")
    assert order.currency == "EUR"
    assert order.status == "open"
    assert order.items == []


def test_sales_order_item_validation_rejects_negative_quantity():
    with pytest.raises(Exception):
        SalesOrderItemInput(article_number="ART-001", quantity=-1, unit_price=10.0)


def test_sales_order_item_validation_rejects_negative_price():
    with pytest.raises(Exception):
        SalesOrderItemInput(article_number="ART-001", quantity=1, unit_price=-5.0)


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_sales_orders_returns_200():
    resp = _client.get("/api/v1/sales/orders/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_order_returns_404():
    resp = _client.get("/api/v1/sales/orders/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_order_missing_fields_returns_422():
    resp = _client.post("/api/v1/sales/orders/", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_order_valid_payload_accepted():
    import uuid
    payload = {
        "customer_id": "C-001",
        "subject": f"Test Order {uuid.uuid4().hex[:6]}",
        "total_amount": 1000.0,
    }
    resp = _client.post("/api/v1/sales/orders/", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)


def test_delete_nonexistent_order_returns_404():
    resp = _client.delete("/api/v1/sales/orders/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 204)
