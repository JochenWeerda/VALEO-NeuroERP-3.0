from __future__ import annotations

from decimal import Decimal

import pytest

from app.api.v1.endpoints import sales_delivery_notes


class _FakeMappingsResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class _FakeResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def mappings(self):
        return _FakeMappingsResult(self._rows)


class _CapturingDb:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.calls: list[tuple[str, dict]] = []
        self.committed = False

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        rows = self.rows.pop(0) if self.rows else []
        return _FakeResult(rows)

    def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_list_delivery_notes_uses_context_tenant():
    db = _CapturingDb(rows=[[]])

    result = await sales_delivery_notes.list_delivery_notes(
        customer_id=None,
        status_filter=None,
        tenant_id="tenant-a",
        skip=0,
        limit=50,
        db=db,
    )

    assert result == []
    statement, params = db.calls[0]
    assert "WHERE tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"


@pytest.mark.asyncio
async def test_create_invoice_from_delivery_scopes_final_update_by_tenant():
    db = _CapturingDb(
        rows=[
            [{"id": "ls-1", "status": "posted", "ls_nummer": "LS-100"}],
            [{"netto_betrag": Decimal("19.50")}],
            [],
            [],
            [],
        ]
    )

    result = await sales_delivery_notes.create_invoice_from_delivery(
        ls_id="ls-1",
        tenant_id="tenant-a",
        db=db,
    )

    assert result["delivery_note_id"] == "ls-1"
    update_statement, update_params = db.calls[-1]
    assert "WHERE id = :id AND tenant_id = :tenant_id" in update_statement
    assert update_params["tenant_id"] == "tenant-a"
    assert db.committed is True
