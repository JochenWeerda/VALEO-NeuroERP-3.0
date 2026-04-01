from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import creditors


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


@pytest.mark.asyncio
async def test_create_creditor_rejects_tenant_mismatch():
    db = _CapturingDb()
    payload = creditors.CreditorCreate(
        tenant_id="tenant-evil",
        creditor_number="K-1000",
        company_name="Lieferant GmbH",
        street="Hauptstrasse 1",
        postal_code="10115",
        city="Berlin",
        country="DE",
        payment_terms_days=30,
        discount_days=0,
        discount_percent=Decimal("0.00"),
        credit_limit=Decimal("0.00"),
        is_active=True,
    )

    with pytest.raises(HTTPException) as exc:
        await creditors.create_creditor(payload=payload, tenant_id="tenant-a", db=db)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"


@pytest.mark.asyncio
async def test_list_creditors_always_filters_by_context_tenant():
    db = _CapturingDb(rows=[[(0,)], []])

    result = await creditors.list_creditors(
        is_active=True,
        search="K-10",
        skip=5,
        limit=25,
        tenant_id="tenant-a",
        db=db,
    )

    assert result.total == 0
    count_statement, count_params = db.calls[0]
    list_statement, list_params = db.calls[1]
    assert "tenant_id = :tenant_id" in count_statement
    assert count_params["tenant_id"] == "tenant-a"
    assert count_params["is_active"] is True
    assert count_params["search"] == "%K-10%"
    assert "tenant_id = :tenant_id" in list_statement
    assert list_params["tenant_id"] == "tenant-a"
    assert list_params["limit"] == 25
    assert list_params["skip"] == 5


@pytest.mark.asyncio
async def test_get_creditor_scopes_lookup_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await creditors.get_creditor(
            creditor_id="cred-1",
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "WHERE id = :id AND (tenant_id = :tenant_id" in statement
    assert params == {"id": "cred-1", "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_update_creditor_scopes_existing_row_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await creditors.update_creditor(
            creditor_id="cred-1",
            payload=creditors.CreditorUpdate(company_name="Neu GmbH"),
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "WHERE id = :id AND (tenant_id = :tenant_id" in statement
    assert params == {"id": "cred-1", "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_balance_lookup_scopes_creditor_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await creditors.get_creditor_balance(
            creditor_id="cred-1",
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "WHERE id = :id AND (tenant_id = :tenant_id" in statement
    assert params == {"id": "cred-1", "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_delete_creditor_scopes_lookup_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await creditors.delete_creditor(
            creditor_id="cred-1",
            tenant_id="tenant-a",
            db=db,
        )

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "WHERE id = :id AND (tenant_id = :tenant_id" in statement
    assert params == {"id": "cred-1", "tenant_id": "tenant-a"}
