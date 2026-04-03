from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import sales_offers


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
async def test_create_sales_offer_rejects_payload_tenant_mismatch():
    db = _CapturingDb()
    payload = sales_offers.SalesOfferCreate(
        tenant_id="tenant-b",
        offer_number="ANG-1",
        subject="Angebot",
        items=[],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sales_offers.create_sales_offer(payload=payload, tenant_id="tenant-a", db=db)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_update_sales_offer_scopes_item_reset_and_total_update_by_tenant():
    now = datetime.now(timezone.utc)
    db = _CapturingDb(
        results=[
            _FakeResult(
                [
                    {
                        "id": "offer-1",
                        "tenant_id": "tenant-a",
                        "offer_number": "ANG-1",
                        "subject": "Angebot",
                        "status": "offen",
                        "total_amount": 10,
                        "created_at": now,
                        "updated_at": now,
                    }
                ]
            ),
            _FakeResult(),
            _FakeResult(),
            _FakeResult(),
            _FakeResult(
                [
                    {
                        "id": "offer-1",
                        "tenant_id": "tenant-a",
                        "offer_number": "ANG-1",
                        "subject": "Angebot",
                        "status": "offen",
                        "total_amount": 19,
                        "created_at": now,
                        "updated_at": now,
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
                        "unit": "kg",
                        "unit_price": 9.5,
                        "ek_price": None,
                        "discount_percent": 0,
                        "line_total": 19,
                    }
                ]
            ),
        ]
    )

    result = await sales_offers.update_sales_offer(
        offer_id="offer-1",
        payload=sales_offers.SalesOfferUpdate(
            items=[
                sales_offers.SalesOfferItemInput(
                    article_number="ART-1",
                    quantity=2,
                    unit_price=9.5,
                )
            ]
        ),
        tenant_id="tenant-a",
        db=db,
    )

    delete_items_statement, delete_items_params = db.calls[1]
    update_total_statement, update_total_params = db.calls[3]
    assert "DELETE FROM domain_crm.sales_offer_items WHERE offer_id = :offer_id AND tenant_id = :tenant_id" in delete_items_statement
    assert delete_items_params == {"offer_id": "offer-1", "tenant_id": "tenant-a"}
    assert "WHERE id = :offer_id AND tenant_id = :tenant_id" in update_total_statement
    assert update_total_params["offer_id"] == "offer-1"
    assert update_total_params["tenant_id"] == "tenant-a"
    assert result.tenant_id == "tenant-a"
    assert db.committed is True


@pytest.mark.asyncio
async def test_convert_offer_to_order_scopes_status_update_by_tenant():
    db = _CapturingDb(
        results=[
            _FakeResult(
                [
                    {
                        "id": "offer-1",
                        "tenant_id": "tenant-a",
                        "offer_number": "ANG-1",
                        "customer_id": "cust-1",
                        "subject": "Angebot",
                        "description": "",
                        "currency": "EUR",
                        "status": "offen",
                    }
                ]
            ),
            _FakeResult(),
            _FakeResult(
                [
                    {
                        "id": "item-1",
                        "line_number": 1,
                        "article_number": "ART-1",
                        "description": "Artikel",
                        "quantity": 1,
                        "unit": "kg",
                        "unit_price": 10,
                        "ek_price": None,
                        "discount_percent": 0,
                        "line_total": 10,
                    }
                ]
            ),
            _FakeResult(),
            _FakeResult(),
            _FakeResult(
                [
                    {
                        "id": "offer-1",
                        "tenant_id": "tenant-a",
                        "offer_number": "ANG-1",
                        "customer_id": "cust-1",
                        "subject": "Angebot",
                        "description": "",
                        "currency": "EUR",
                        "status": "angenommen",
                    }
                ]
            ),
        ]
    )

    result = await sales_offers.convert_offer_to_order(
        offer_id="offer-1",
        tenant_id="tenant-a",
        db=db,
    )

    update_statement, update_params = db.calls[1]
    assert "WHERE id = :id AND tenant_id = :tenant_id" in update_statement
    assert update_params["id"] == "offer-1"
    assert update_params["tenant_id"] == "tenant-a"
    assert result["created_order_number"] == "SO-ANG-1"
    assert db.committed is True
