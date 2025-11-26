from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.dependencies import get_approval_rule_store
from app.storage.approval_rules import ApprovalRuleStore
from finance_shared.auth import FiBuRole
from main import app


@pytest.fixture()
def override_store(tmp_path: Path):
    store = ApprovalRuleStore(str(tmp_path / "approval.db"))
    original_flag = settings.EVENT_BUS_ENABLED
    settings.EVENT_BUS_ENABLED = False

    def _override():
        return store

    app.dependency_overrides[get_approval_rule_store] = _override
    yield store
    app.dependency_overrides.pop(get_approval_rule_store, None)
    settings.EVENT_BUS_ENABLED = original_flag


def _client():
    return TestClient(app)


def test_list_approval_rules_returns_data(override_store: ApprovalRuleStore):
    override_store.upsert_rule(
        tenant_id="tenant-x",
        currency="EUR",
        min_amount=Decimal("1500.00"),
        required_role=FiBuRole.FREIGEBER,
    )
    with _client() as client:
        response = client.get("/api/v1/finance/approval-rules", headers={"x-tenant-id": "tenant-x"})
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["tenant"] == "tenant-x"
        assert body["meta"]["count"] >= 1


def test_upsert_approval_rule(override_store: ApprovalRuleStore):
    with _client() as client:
        response = client.post(
            "/api/v1/finance/approval-rules",
            json={
                "tenant_id": "tenant-y",
                "currency": "USD",
                "min_amount": "500.00",
                "required_role": "freigeber",
            },
        )
        assert response.status_code == 201
        record = override_store.list_rules("tenant-y")[0]
        assert record.currency == "USD"


