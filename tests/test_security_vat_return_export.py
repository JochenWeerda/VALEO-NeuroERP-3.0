from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import vat_return_export


class _FakeResult:
    def __init__(self, rows=None):
        self._rows = rows or []

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


def _vat_row():
    return (
        "vat-1",
        "2026-03",
        "monthly",
        "Company",
        None,
        None,
        Decimal("100.00"),
        Decimal("19.00"),
        Decimal("19.00"),
        Decimal("0.00"),
        '[{"position_code":"81","description":"USt","net_amount":100.0,"tax_amount":19.0,"tax_rate":19.0}]',
        "calculated",
        datetime.utcnow(),
        None,
        None,
        None,
        datetime.utcnow(),
        datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_calculate_vat_return_rejects_payload_tenant_mismatch():
    db = _CapturingDb()
    request = vat_return_export.VATReturnCalculationRequest(period="2026-03", tenant_id="tenant-b")

    with pytest.raises(HTTPException) as exc_info:
        await vat_return_export.calculate_vat_return(
            request=request,
            tenant_id="tenant-a",
            db=db,
        )

    assert exc_info.value.status_code == 403
    assert "different tenant" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_vat_return_uses_context_tenant():
    db = _CapturingDb(rows=[[_vat_row()]])

    result = await vat_return_export.get_vat_return(
        return_id="vat-1",
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "WHERE id = :return_id AND tenant_id = :tenant_id" in statement
    assert params == {"return_id": "vat-1", "tenant_id": "tenant-a"}
    assert result.id == "vat-1"


@pytest.mark.asyncio
async def test_list_vat_returns_uses_context_tenant():
    db = _CapturingDb(rows=[[_vat_row()]])

    result = await vat_return_export.list_vat_returns(
        period="2026-03",
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "WHERE tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"
    assert params["period"] == "2026-03"
    assert result[0].id == "vat-1"
