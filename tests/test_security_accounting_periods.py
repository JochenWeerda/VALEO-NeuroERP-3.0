from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.v1.endpoints import accounting_periods


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows

    def scalar(self):
        row = self.fetchone()
        if row is None:
            return None
        if isinstance(row, tuple):
            return row[0]
        return row


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


def _make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/finance/periods",
            "headers": [],
        }
    )


@pytest.mark.asyncio
async def test_create_period_rejects_tenant_mismatch():
    db = _CapturingDb()
    payload = accounting_periods.PeriodCreate(
        tenant_id="tenant-evil",
        period="2026-01",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    with pytest.raises(HTTPException) as exc:
        await accounting_periods.create_period(
            period_data=payload,
            request=_make_request(),
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"


@pytest.mark.asyncio
async def test_list_periods_always_filters_by_context_tenant():
    db = _CapturingDb(rows=[[]])

    result = await accounting_periods.list_periods(
        status="OPEN",
        limit=50,
        skip=10,
        tenant_id="tenant-a",
        db=db,
    )

    assert result == []
    statement, params = db.calls[0]
    assert "tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"
    assert params["status"] == "OPEN"
    assert params["limit"] == 50
    assert params["skip"] == 10


@pytest.mark.asyncio
async def test_get_period_scopes_lookup_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await accounting_periods.get_period(
            period_id="period-1",
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "WHERE id = :id AND tenant_id = :tenant_id" in statement
    assert params == {"id": "period-1", "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_update_period_scopes_existing_row_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await accounting_periods.update_period(
            period_id="period-1",
            period_update=accounting_periods.PeriodUpdate(status="CLOSED"),
            request=_make_request(),
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "WHERE id = :id AND tenant_id = :tenant_id" in statement
    assert params == {"id": "period-1", "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_check_period_status_rejects_foreign_tenant():
    db = _CapturingDb()

    with pytest.raises(HTTPException) as exc:
        await accounting_periods.check_period_status(
            tenant_id="tenant-evil",
            period="2026-01",
            current_tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"
