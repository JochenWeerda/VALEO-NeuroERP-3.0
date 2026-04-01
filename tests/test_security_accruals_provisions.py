from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import accruals_provisions


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows


class _CapturingDb:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.calls: list[tuple[str, dict]] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        rows = self.rows.pop(0) if self.rows else []
        return _FakeResult(rows)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


@pytest.mark.asyncio
async def test_list_accruals_uses_context_tenant():
    db = _CapturingDb(rows=[[], []])

    await accruals_provisions.list_accruals_provisions(
        period="2026-03",
        accrual_type="rueckstellung",
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[-1]
    assert "tenant_id = :tid" in statement
    assert params["tid"] == "tenant-a"
    assert params["period"] == "2026-03"
    assert params["atype"] == "rueckstellung"


@pytest.mark.asyncio
async def test_create_accrual_uses_context_tenant_for_insert():
    db = _CapturingDb(rows=[[]])
    item = accruals_provisions.AccrualItemCreate(
        description="Rueckstellung Strom",
        amount=Decimal("250.00"),
        account_number="4900",
        counterpart_account="1200",
        period="2026-03",
        accrual_type="rueckstellung",
    )

    result = await accruals_provisions.create_accrual_provision(
        item=item,
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[-1]
    assert "INSERT INTO domain_erp.accruals_provisions" in statement
    assert params["tid"] == "tenant-a"
    assert result.tenant_id == "tenant-a"


@pytest.mark.asyncio
async def test_post_accrual_scopes_readback_and_update_by_tenant():
    db = _CapturingDb(
        rows=[
            [("acc-1", "draft")],
            [("acc-1", "tenant-a", "Rueckstellung Strom", Decimal("250.00"), "4900", "1200", "2026-03", "rueckstellung", "draft", None)],
            [],
            [],
        ]
    )

    result = await accruals_provisions.post_accrual_provision(
        item_id="acc-1",
        tenant_id="tenant-a",
        db=db,
    )

    lookup_statement, lookup_params = db.calls[1]
    update_statement, update_params = db.calls[3]
    assert "WHERE id = :id AND tenant_id = :tid" in lookup_statement
    assert lookup_params == {"id": "acc-1", "tid": "tenant-a"}
    assert "WHERE id = :id AND tenant_id = :tid" in update_statement
    assert update_params == {"id": "acc-1", "tid": "tenant-a"}
    assert result["ok"] is True
