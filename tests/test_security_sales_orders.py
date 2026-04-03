from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import sales_orders


class _FakeMappingsResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class _FakeResult:
    def __init__(self, rows=None, *, rowcount: int = 1):
        self._rows = list(rows or [])
        self.rowcount = rowcount

    def mappings(self):
        return _FakeMappingsResult(self._rows)

    def first(self):
        return self._rows[0] if self._rows else None

    def scalar(self):
        return self._rows[0] if self._rows else None


class _CapturingDb:
    def __init__(self, results=None):
        self.results = list(results or [])
        self.calls: list[tuple[str, dict]] = []
        self.committed = False

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        result = self.results.pop(0) if self.results else _FakeResult()
        return result

    def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_create_sales_order_rejects_payload_tenant_mismatch():
    db = _CapturingDb()
    payload = sales_orders.SalesOrderCreate(
        tenant_id="tenant-b",
        customer_id="cust-1",
        subject="Auftrag",
        items=[],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sales_orders.create_sales_order(payload=payload, tenant_id="tenant-a", db=db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_create_delivery_from_order_scopes_final_update_by_tenant():
    db = _CapturingDb(
        results=[
            _FakeResult(
                [
                    {
                        "id": "so-1",
                        "tenant_id": "tenant-a",
                        "order_number": "SO-1",
                        "customer_id": "cust-1",
                        "subject": "Auftrag",
                        "status": "open",
                    }
                ]
            ),
            _FakeResult(
                [
                    {
                        "id": "item-1",
                        "line_number": 1,
                        "article_number": "ART-1",
                        "description": "Artikel",
                        "quantity": 2,
                        "unit_price": 9.5,
                        "discount_percent": 0,
                        "line_total": 19,
                    }
                ]
            ),
            _FakeResult(),
            _FakeResult(),
            _FakeResult(),
        ]
    )

    result = await sales_orders.create_delivery_from_order(
        order_id="so-1",
        tenant_id="tenant-a",
        db=db,
    )

    update_statement, update_params = db.calls[-1]
    assert result["order_id"] == "so-1"
    assert "WHERE id = :id AND tenant_id = :tenant_id" in update_statement
    assert update_params["tenant_id"] == "tenant-a"
    assert db.committed is True


@pytest.mark.asyncio
async def test_delete_sales_order_scopes_item_delete_and_soft_delete_by_tenant():
    db = _CapturingDb(results=[_FakeResult(rowcount=1), _FakeResult(rowcount=1)])

    response = await sales_orders.delete_sales_order(
        order_id="so-1",
        tenant_id="tenant-a",
        db=db,
    )

    delete_items_statement, delete_items_params = db.calls[0]
    update_statement, update_params = db.calls[1]
    assert "DELETE FROM domain_crm.sales_order_items WHERE order_id = :id AND tenant_id = :tenant_id" in delete_items_statement
    assert delete_items_params == {"id": "so-1", "tenant_id": "tenant-a"}
    assert "WHERE id = :id AND tenant_id = :tenant_id" in update_statement
    assert update_params["id"] == "so-1"
    assert update_params["tenant_id"] == "tenant-a"
    assert response.status_code == 204
    assert db.committed is True
