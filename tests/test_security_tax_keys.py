from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.api.v1.endpoints import tax_keys


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows
        self.rowcount = len(rows)

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


def _tax_key_row():
    return (
        "tax-1",
        "19",
        "Standard",
        Decimal("19.00"),
        "81",
        "Umsatzsteuer 19%",
        False,
        False,
        False,
        date(2026, 1, 1),
        None,
        None,
        None,
        None,
        "DE",
        None,
        True,
        datetime.utcnow(),
        datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_list_tax_keys_uses_context_tenant():
    db = _CapturingDb(rows=[[_tax_key_row()]])

    result = await tax_keys.list_tax_keys(
        tenant_id="tenant-a",
        active_only=True,
        country="DE",
        db=db,
    )

    statement, params = db.calls[0]
    assert "tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"
    assert params["country"] == "DE"
    assert result[0].id == "tax-1"


@pytest.mark.asyncio
async def test_create_tax_key_uses_context_tenant():
    db = _CapturingDb(rows=[[], [_tax_key_row()]])
    payload = tax_keys.TaxKeyCreate(
        code="19",
        bezeichnung="Standard",
        steuersatz=Decimal("19.00"),
        ustva_position="81",
        ustva_bezeichnung="Umsatzsteuer 19%",
        gueltig_von=date(2026, 1, 1),
    )

    result = await tax_keys.create_tax_key(
        tax_key=payload,
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[1]
    assert "INSERT INTO domain_erp.tax_keys" in statement
    assert params["tenant_id"] == "tenant-a"
    assert result.id == "tax-1"


@pytest.mark.asyncio
async def test_get_tax_key_scopes_by_context_tenant():
    db = _CapturingDb(rows=[[_tax_key_row()]])

    await tax_keys.get_tax_key(
        tax_key_id="tax-1",
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "WHERE id = :tax_key_id AND tenant_id = :tenant_id" in statement
    assert params == {"tax_key_id": "tax-1", "tenant_id": "tenant-a"}
