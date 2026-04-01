from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.api.v1.endpoints import subsidiary_ledger_reconciliation as reconciliation


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
        item = self.queue.pop(0) if self.queue else _FakeResult()
        return item


@pytest.mark.asyncio
async def test_reconcile_ar_uses_context_tenant():
    db = _CapturingDb(
        queue=[
            _FakeResult(rows=[("coa-1", "1400", "Debitoren")]),
            _FakeResult(rows=[(Decimal("150.00"), Decimal("25.00"))]),
            _FakeResult(scalar_value="domain_erp.offene_posten"),
            _FakeResult(rows=[(Decimal("200.00"), 3, 1)]),
        ]
    )

    result = await reconciliation.reconcile_ar(
        period="2026-03",
        tenant_id="tenant-a",
        db=db,
    )

    account_statement, account_params = db.calls[0]
    open_items_statement, open_items_params = db.calls[3]
    assert "WHERE tenant_id = :tenant_id" in account_statement
    assert account_params["tenant_id"] == "tenant-a"
    assert "tenant_id = :tenant_id" in open_items_statement
    assert open_items_params["tenant_id"] == "tenant-a"
    assert result.entries[0].account_number == "1400"


@pytest.mark.asyncio
async def test_reconciliation_details_use_context_tenant():
    db = _CapturingDb(
        queue=[
            _FakeResult(scalar_value="domain_erp.offene_posten"),
            _FakeResult(rows=[("row-1", "RE-1", date(2026, 3, 31), Decimal("10.00"), "Text", "offen")]),
        ]
    )

    result = await reconciliation.get_reconciliation_details(
        ledger_type="ar",
        account_number="1400",
        period="2026-03",
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[1]
    assert "tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"
    assert result[0].entry_id == "row-1"
