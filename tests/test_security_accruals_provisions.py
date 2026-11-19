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
async def test_post_accrual_scopes_readback_service_and_update_by_tenant(monkeypatch):
    """Gebucht wird ueber den Buchungsdienst des Kontextmandanten; Lesen und Statusupdate bleiben mandantengebunden.

    Die Buchung selbst pruefen die Tests in tests/test_abgrenzung_bucht_ueber_dienst.py gegen echtes Schema.
    """
    db = _CapturingDb(
        rows=[
            [("acc-1", "tenant-a", "Rueckstellung Strom", Decimal("250.00"), "4900", "1200", "2026-03", "rueckstellung", "draft", None)],
            [],
        ]
    )
    dienste: list[str] = []

    class _Dienst:
        def __init__(self, sitzung, tenant_id, *, commit_on_success=True):
            assert sitzung is db and commit_on_success is False
            dienste.append(tenant_id)

        def account_id_for_number(self, nummer):
            return f"konto-{nummer}"

        def create(self, **daten):
            assert [z["account_id"] for z in daten["lines"]] == ["konto-4900", "konto-1200"]
            return type("Eintrag", (), {"id": "je-1"})()

        def post(self, entry_id, posted_by=None):
            assert entry_id == "je-1"

    monkeypatch.setattr(accruals_provisions, "FinanceTransactionService", _Dienst)
    monkeypatch.setattr(accruals_provisions.finance_freigabe, "verlange_hauptbuchbuchung", lambda *a, **k: None)

    result = await accruals_provisions.post_accrual_provision(
        item_id="acc-1",
        tenant_id="tenant-a",
        db=db,
        nutzer={"sub": "buchhalter"},
    )

    lookup_statement, lookup_params = db.calls[0]
    update_statement, update_params = db.calls[1]
    assert "WHERE id = :id AND tenant_id = :tid" in lookup_statement
    assert lookup_params == {"id": "acc-1", "tid": "tenant-a"}
    assert "UPDATE domain_erp.accruals_provisions" in update_statement
    assert "WHERE id = :id AND tenant_id = :tid" in update_statement
    assert update_params == {"id": "acc-1", "tid": "tenant-a"}
    assert dienste == ["tenant-a"] and db.committed
    assert result == {"ok": True, "journal_entry_id": "je-1"}
