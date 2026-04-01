from __future__ import annotations

from datetime import date
import importlib

import pytest
from fastapi import HTTPException

from app.einkauf import schemas as einkauf_schemas

einkauf_router = importlib.import_module("app.einkauf.router")


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
async def test_get_lieferant_scopes_lookup_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await einkauf_router.get_lieferant(lieferant_id=17, tenant_id="tenant-a", db=db)

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "tenant_id = :tenant_id" in statement
    assert params == {"id": 17, "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_create_lieferant_uses_context_tenant_for_duplicate_check_and_insert():
    db = _CapturingDb(rows=[[], [(99,)]])
    payload = einkauf_schemas.LieferantCreate(
        lieferantennummer="L-100",
        firmenname="Lieferant GmbH",
        email="test@example.com",
    )

    result = await einkauf_router.create_lieferant(
        lieferant=payload,
        tenant_id="tenant-a",
        db=db,
    )

    assert result["id"] == 99
    duplicate_statement, duplicate_params = db.calls[0]
    insert_statement, insert_params = db.calls[1]
    assert "tenant_id = :tenant_id" in duplicate_statement
    assert duplicate_params["tenant_id"] == "tenant-a"
    assert "tenant_id" in insert_statement
    assert insert_params["tenant_id"] == "tenant-a"
    assert db.committed is True


@pytest.mark.asyncio
async def test_get_bestellung_scopes_lookup_by_tenant():
    db = _CapturingDb(rows=[[]])

    with pytest.raises(HTTPException) as exc:
        await einkauf_router.get_bestellung(bestellung_id=5, tenant_id="tenant-a", db=db)

    assert exc.value.status_code == 404
    statement, params = db.calls[0]
    assert "tenant_id = :tenant_id" in statement
    assert params == {"id": 5, "tenant_id": "tenant-a"}


@pytest.mark.asyncio
async def test_create_bestellung_uses_context_tenant_for_duplicate_check_and_insert():
    db = _CapturingDb(rows=[[], [(123,)]])
    payload = einkauf_schemas.BestellungCreate(
        bestellnummer="B-100",
        lieferant_id=17,
        bestelldatum=date(2026, 4, 1),
        status="entwurf",
    )

    result = await einkauf_router.create_bestellung(
        bestellung=payload,
        tenant_id="tenant-a",
        db=db,
    )

    assert result["id"] == 123
    duplicate_statement, duplicate_params = db.calls[0]
    insert_statement, insert_params = db.calls[1]
    assert "tenant_id = :tenant_id" in duplicate_statement
    assert duplicate_params["tenant_id"] == "tenant-a"
    assert "tenant_id" in insert_statement
    assert insert_params["tenant_id"] == "tenant-a"
