from __future__ import annotations

from datetime import datetime

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import ap_approval_workflow


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
async def test_list_approval_rules_uses_context_tenant():
    db = _CapturingDb(
        rows=[
            [
                (
                    "rule-1",
                    "Rule",
                    None,
                    '[{"field":"amount","operator":"gt","value":1000}]',
                    2,
                    '["manager"]',
                    10,
                    True,
                    datetime.utcnow(),
                    datetime.utcnow(),
                )
            ]
        ]
    )

    result = await ap_approval_workflow.list_approval_rules(
        active_only=True,
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "WHERE tenant_id = :tenant_id" in statement
    assert params["tenant_id"] == "tenant-a"
    assert result[0].id == "rule-1"


@pytest.mark.asyncio
async def test_create_approval_rule_uses_context_tenant():
    db = _CapturingDb(
        rows=[
            [
                (
                    "rule-1",
                    "Rule",
                    None,
                    '[{"field":"amount","operator":"gt","value":1000}]',
                    2,
                    '["manager"]',
                    10,
                    True,
                    datetime.utcnow(),
                    datetime.utcnow(),
                )
            ]
        ]
    )
    payload = ap_approval_workflow.ApprovalRuleCreate(
        name="Rule",
        description=None,
        conditions=[ap_approval_workflow.ApprovalRuleCondition(field="amount", operator="gt", value=1000)],
        required_approvals=2,
        approval_roles=["manager"],
        priority=10,
        active=True,
    )

    result = await ap_approval_workflow.create_approval_rule(
        rule=payload,
        tenant_id="tenant-a",
        db=db,
    )

    statement, params = db.calls[0]
    assert "INSERT INTO domain_erp.ap_approval_rules" in statement
    assert params["tenant_id"] == "tenant-a"
    assert result.id == "rule-1"


@pytest.mark.asyncio
async def test_request_approval_rejects_cross_tenant_invoice(monkeypatch):
    db = _CapturingDb()
    request = ap_approval_workflow.ApprovalRequest(
        invoice_id="inv-1",
        requested_by="user-a",
        comment=None,
    )

    monkeypatch.setattr("app.documents.router_helpers.get_repository", lambda _db: object())
    monkeypatch.setattr(
        "app.documents.router_helpers.get_from_store",
        lambda *_args, **_kwargs: {"id": "inv-1", "status": "ENTWURF", "tenantId": "tenant-b"},
    )

    with pytest.raises(HTTPException) as exc_info:
        await ap_approval_workflow.request_approval(
            request=request,
            tenant_id="tenant-a",
            db=db,
        )

    assert exc_info.value.status_code == 403
    assert "different tenant" in str(exc_info.value.detail)
