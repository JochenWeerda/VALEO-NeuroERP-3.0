"""DOM-CRM-002: Tests fuer sales_orders.py.

Abdeckung: _line_total, _resolve_order_number, _resolve_tenant_scope, HTTP CRUD.
"""
from __future__ import annotations

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from main import app
from uuid import uuid4
from types import SimpleNamespace
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from test_system_tenant_binding import keys, probe
from app.api.v1.endpoints.sales_orders import (
    _line_total,
    _resolve_order_number,
    _resolve_tenant_scope,
    SalesOrderCreate,
    SalesOrderItemInput,
)

_HEADERS = {}
_client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def sales_context(require_db, probe, monkeypatch):
    tenant, customer = str(uuid4()), str(uuid4())
    number = 'IT-'+uuid4().hex[:12]
    previous = app.dependency_overrides.get(get_db)
    with engine.connect() as connection:
        outer = connection.begin()
        db = Session(bind=connection, join_transaction_mode='create_savepoint')
        try:
            db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:id,:name,:domain,TRUE)'),
                       {'id': tenant, 'name': 'Synthetic sales tenant', 'domain': tenant+'.test.invalid'})
            db.execute(text('INSERT INTO domain_crm.customers (id,tenant_id,customer_number,company_name,is_active) VALUES (:id,:tenant,:number,:name,TRUE)'),
                       {'id': customer, 'tenant': tenant, 'number': number, 'name': 'Synthetic Sales Customer'})
            db.commit()
            app.dependency_overrides[get_db] = lambda: db
            monkeypatch.setitem(globals(), '_HEADERS', {
                'Authorization': 'Bearer '+probe.token(tenant, changes={'roles': ['admin']}), 'X-Tenant-ID': tenant})
            yield SimpleNamespace(db=db, tenant=tenant, customer=customer, customer_number=number)
        finally:
            if previous is None:
                app.dependency_overrides.pop(get_db, None)
            else:
                app.dependency_overrides[get_db] = previous
            db.close()
            outer.rollback()


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

def test_resolve_order_number_generates_when_none(monkeypatch, tmp_path):
    from app.services.numbering_service import NumberingService
    numbering = NumberingService(str(tmp_path / 'series.json'))
    monkeypatch.setattr('app.api.v1.endpoints.sales_orders.get_numbering', lambda: numbering)
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

def test_list_sales_orders_returns_200(sales_context):
    resp = _client.get("/api/v1/sales/orders/", headers=_HEADERS)
    assert resp.status_code == 200


def test_get_nonexistent_order_returns_404(sales_context):
    resp = _client.get("/api/v1/sales/orders/does-not-exist", headers=_HEADERS)
    assert resp.status_code == 404


def test_create_order_missing_fields_returns_422(sales_context):
    resp = _client.post("/api/v1/sales/orders/", json={}, headers=_HEADERS)
    assert resp.status_code == 422


def test_create_order_valid_payload_accepted(sales_context):
    import uuid
    payload = {
        "customer_id": sales_context.customer,
        "order_number": "IT-SO-"+uuid.uuid4().hex[:12],
        "subject": f"Test Order {uuid.uuid4().hex[:6]}",
        "total_amount": 1000.0,
    }
    resp = _client.post("/api/v1/sales/orders/", json=payload, headers=_HEADERS)
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created['customer_id'] == sales_context.customer
    detail = _client.get('/api/v1/sales/orders/'+created['id'], headers=_HEADERS)
    assert detail.status_code == 200, detail.text
    assert detail.json()['subject'] == payload['subject']


def test_order_detail_names_the_crm_customer(sales_context):
    """The mask heading resolves the own tenant's actual CRM customer."""
    order_id, order_number = str(uuid4()), 'IT-SO-'+uuid4().hex[:12]
    sales_context.db.execute(text(
        "INSERT INTO domain_crm.sales_orders "
        "(id,tenant_id,order_number,customer_id,subject,description,total_amount,currency,status,version) "
        "VALUES (:id,:tenant,:number,:customer,'Test wheat','',0,'EUR','ENTWURF',1)"),
        {'id': order_id, 'tenant': sales_context.tenant, 'number': order_number, 'customer': sales_context.customer})
    sales_context.db.commit()
    response = _client.get('/api/v1/sales/orders/'+order_id, headers=_HEADERS)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['customer_id'] == sales_context.customer
    assert body['customer_name'] == 'Synthetic Sales Customer'
    assert body['customer_number'] == sales_context.customer_number


def test_delete_nonexistent_order_returns_404(sales_context):
    resp = _client.delete("/api/v1/sales/orders/does-not-exist", headers=_HEADERS)
    assert resp.status_code == 404, resp.text


@pytest.mark.parametrize('credential', [None, 'dev-token'])
def test_sales_orders_reject_missing_or_legacy_identity(sales_context, credential):
    headers = {'X-Tenant-ID': sales_context.tenant}
    if credential:
        headers['Authorization'] = 'Bearer '+credential
    response = _client.get('/api/v1/sales/orders/', headers=headers)
    assert response.status_code == 401


def test_sales_orders_reject_foreign_tenant_selector(sales_context):
    response = _client.get('/api/v1/sales/orders/', headers={**_HEADERS, 'X-Tenant-ID': str(uuid4())})
    assert response.status_code == 403
