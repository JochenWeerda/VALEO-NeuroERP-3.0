from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import sales_credit_notes


def _eligibility_fetchone_ok():
    return SimpleNamespace(
        customer_number="",
        business_partner_id=None,
        bp_id=None,
        bp_status=None,
        blocked_for_delivery=None,
        blocked_for_invoice=None,
    )


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

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        rows = self.rows.pop(0) if self.rows else []
        return _FakeResult(rows)

    def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_create_credit_note_rejects_payload_tenant_mismatch(monkeypatch):
    db = _CapturingDb()
    payload = sales_credit_notes.CreditNoteCreate(
        tenant_id="tenant-b",
        credit_note_number="GS-1",
        customer_id="cust-1",
        reason="Retoure",
        lines=[],
    )
    monkeypatch.setattr(sales_credit_notes, "log_fibu_audit", lambda *args, **kwargs: None)

    with pytest.raises(HTTPException) as exc_info:
        await sales_credit_notes.create_credit_note(
            payload=payload,
            request=None,
            tenant_id="tenant-a",
            db=db,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_post_credit_note_scopes_lookup_and_update_by_tenant(monkeypatch):
    db = _CapturingDb(
        rows=[
            [("cn-1", "tenant-a", "GS-1", "cust-1", Decimal("50.00"), "draft")],
            [_eligibility_fetchone_ok()],
            [],
            [],
        ]
    )
    monkeypatch.setattr(sales_credit_notes, "log_fibu_audit", lambda *args, **kwargs: None)

    result = await sales_credit_notes.post_credit_note(
        cn_id="cn-1",
        request=None,
        tenant_id="tenant-a",
        db=db,
    )

    select_statement, select_params = db.calls[0]
    update_statement, update_params = db.calls[3]
    assert "WHERE id = :id AND tenant_id = :tid" in select_statement
    assert select_params == {"id": "cn-1", "tid": "tenant-a"}
    assert "WHERE id = :id AND tenant_id = :tid" in update_statement
    assert update_params == {"id": "cn-1", "tid": "tenant-a"}
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_update_return_status_scopes_by_tenant():
    db = _CapturingDb(rows=[[("ret-1",)], []])

    result = await sales_credit_notes.update_return_status(
        return_id="ret-1",
        new_status="processing",
        tenant_id="tenant-a",
        db=db,
    )

    select_statement, select_params = db.calls[0]
    update_statement, update_params = db.calls[1]
    assert "WHERE id = :id AND tenant_id = :tid" in select_statement
    assert select_params == {"id": "ret-1", "tid": "tenant-a"}
    assert "WHERE id = :id AND tenant_id = :tid" in update_statement
    assert update_params == {"id": "ret-1", "s": "processing", "tid": "tenant-a"}
    assert result["status"] == "processing"
