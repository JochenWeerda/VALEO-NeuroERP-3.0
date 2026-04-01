from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.api.v1.endpoints import sales_reports


class _FakeResult:
    def __init__(self, rows=None, scalar_value=None):
        self._rows = rows or []
        self._scalar_value = scalar_value

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows

    def scalar(self):
        return self._scalar_value


class _CapturingDb:
    def __init__(self, queue=None):
        self.queue = list(queue or [])
        self.calls: list[tuple[str, dict]] = []

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        return self.queue.pop(0) if self.queue else _FakeResult()


@pytest.mark.asyncio
async def test_sales_summary_uses_context_tenant():
    db = _CapturingDb(
        queue=[
            _FakeResult(rows=[(4, Decimal("500.00"))]),
            _FakeResult(rows=[(2,)]),
        ]
    )

    result = await sales_reports.get_sales_summary(
        period_from=date(2026, 3, 1),
        period_to=date(2026, 3, 31),
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "tenant_id = :tid" in statement
    assert params["tid"] == "tenant-a"
    assert result.total_orders == 4


@pytest.mark.asyncio
async def test_top_customers_uses_context_tenant():
    db = _CapturingDb(queue=[_FakeResult(rows=[("cust-1", "Customer", 3, Decimal("250.00"))])])

    result = await sales_reports.get_top_customers(
        period_from=date(2026, 3, 1),
        period_to=date(2026, 3, 31),
        limit=5,
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "so.tenant_id = :tid" in statement
    assert params["tid"] == "tenant-a"
    assert params["lim"] == 5
    assert result[0].customer_id == "cust-1"


@pytest.mark.asyncio
async def test_sales_pipeline_uses_context_tenant():
    db = _CapturingDb(
        queue=[
            _FakeResult(rows=[(2, Decimal("200.00"))]),
            _FakeResult(rows=[(3, Decimal("150.00"))]),
            _FakeResult(scalar_value=10),
            _FakeResult(scalar_value=5),
        ]
    )

    result = await sales_reports.get_sales_pipeline_kpi(
        tenant_id="tenant-a",
        db=db,
    )

    for _statement, params in db.calls:
        assert params["tid"] == "tenant-a"
    assert result.open_orders == 2
    assert result.conversion_rate == 50.0
