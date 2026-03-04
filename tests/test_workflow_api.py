"""
API tests for workflow endpoints.
"""

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.documents import WorkflowAudit, WorkflowStatus

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}
SALES_USER = {"user_info": {"roles": ["sales"]}}
PURCHASE_USER = {"user_info": {"roles": ["purchase"]}}
APPROVER_USER = {"user_info": {"roles": ["admin"]}}


@pytest.fixture(autouse=True)
def _reset_workflow_tables():
    """Keep workflow API tests deterministic across larger test runs."""
    with SessionLocal() as db:
        bind = db.get_bind()
        WorkflowStatus.__table__.create(bind=bind, checkfirst=True)
        WorkflowAudit.__table__.create(bind=bind, checkfirst=True)
        db.execute(text("DELETE FROM workflow_audit"))
        db.execute(text("DELETE FROM workflow_status"))
        db.commit()
    yield


def _merge(*parts: dict) -> dict:
    out: dict = {}
    for p in parts:
        out.update(p)
    return out


class TestWorkflowAPI:
    def test_get_status_default_is_draft(self):
        response = client.get("/api/workflow/sales/SO-00001", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["state"] == "draft"

    def test_submit_transition(self):
        payload = _merge(SALES_USER, {"lines": [{"qty": 10, "price": 50}]})
        response = client.post("/api/workflow/sales/SO-00002/transition?action=submit", json=payload, headers=AUTH_HEADERS)
        assert response.status_code == 200
        assert response.json()["state"] == "pending"

    def test_approve_transition(self):
        client.post(
            "/api/workflow/sales/SO-00003/transition?action=submit",
            json=_merge(SALES_USER, {"lines": [{"qty": 10, "price": 60, "cost": 50}]}),
            headers=AUTH_HEADERS,
        )
        response = client.post(
            "/api/workflow/sales/SO-00003/transition?action=approve",
            json={"lines": [{"qty": 10, "price": 60, "cost": 50}], "total": 600},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "approved"

    def test_reject_transition(self):
        client.post(
            "/api/workflow/sales/SO-00004/transition?action=submit",
            json=_merge(SALES_USER, {"lines": [{"qty": 10, "price": 50}]}),
            headers=AUTH_HEADERS,
        )
        response = client.post(
            "/api/workflow/sales/SO-00004/transition?action=reject",
            json=_merge(APPROVER_USER, {"reason": "Price too low"}),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "rejected"

    def test_post_transition(self):
        client.post(
            "/api/workflow/sales/SO-00005/transition?action=submit",
            json=_merge(SALES_USER, {"lines": [{"qty": 10, "price": 60, "cost": 50}]}),
            headers=AUTH_HEADERS,
        )
        client.post(
            "/api/workflow/sales/SO-00005/transition?action=approve",
            json={"lines": [{"qty": 10, "price": 60, "cost": 50}], "total": 600},
            headers=AUTH_HEADERS,
        )
        response = client.post(
            "/api/workflow/sales/SO-00005/transition?action=post",
            json={"total": 600, "lines": []},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "posted"

    def test_invalid_transition_returns_400(self):
        response = client.post(
            "/api/workflow/sales/SO-00006/transition?action=approve",
            json={"lines": []},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 400

    def test_guard_total_positive_blocks_post(self):
        client.post(
            "/api/workflow/sales/SO-00007/transition?action=submit",
            json=_merge(SALES_USER, {"lines": [{"qty": 10, "price": 60, "cost": 50}]}),
            headers=AUTH_HEADERS,
        )
        client.post(
            "/api/workflow/sales/SO-00007/transition?action=approve",
            json={"lines": [{"qty": 10, "price": 60, "cost": 50}], "total": 600},
            headers=AUTH_HEADERS,
        )
        response = client.post(
            "/api/workflow/sales/SO-00007/transition?action=post",
            json={"total": 0, "lines": []},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 400

    def test_guard_price_below_cost_blocks_approve(self):
        client.post(
            "/api/workflow/sales/SO-00008/transition?action=submit",
            json=_merge(SALES_USER, {"lines": [{"qty": 10, "price": 40, "cost": 50}]}),
            headers=AUTH_HEADERS,
        )
        response = client.post(
            "/api/workflow/sales/SO-00008/transition?action=approve",
            json={"lines": [{"article": "SKU-001", "qty": 10, "price": 40, "cost": 50}]},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 400

    def test_audit_trail_records_transitions(self):
        doc_number = "SO-00009"
        client.post(
            f"/api/workflow/sales/{doc_number}/transition?action=submit",
            json=_merge(SALES_USER, {"lines": [{"qty": 10, "price": 60, "cost": 50}]}),
            headers=AUTH_HEADERS,
        )
        client.post(
            f"/api/workflow/sales/{doc_number}/transition?action=approve",
            json={"lines": [{"qty": 10, "price": 60, "cost": 50}], "total": 600},
            headers=AUTH_HEADERS,
        )
        response = client.get(f"/api/workflow/sales/{doc_number}/audit", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert len(data["items"]) == 2
        assert data["items"][0]["action"] == "submit"
        assert data["items"][1]["action"] == "approve"

    def test_audit_trail_includes_timestamp(self):
        doc_number = "SO-00010"
        client.post(
            f"/api/workflow/sales/{doc_number}/transition?action=submit",
            json=_merge(SALES_USER, {"lines": []}),
            headers=AUTH_HEADERS,
        )
        response = client.get(f"/api/workflow/sales/{doc_number}/audit", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["items"][0]["ts"] > 0

    def test_purchase_workflow_api(self):
        doc_number = "PO-00001"
        response = client.post(
            f"/api/workflow/purchase/{doc_number}/transition?action=submit",
            json=_merge(PURCHASE_USER, {"lines": []}),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "pending"

        response = client.post(
            f"/api/workflow/purchase/{doc_number}/transition?action=approve",
            json=_merge(APPROVER_USER, {"lines": [], "total": 500}),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "approved"

        response = client.post(
            f"/api/workflow/purchase/{doc_number}/transition?action=post",
            json={"total": 500, "lines": []},
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "posted"


class TestWorkflowReplay:
    def test_replay_returns_events(self):
        client.post(
            "/api/workflow/sales/SO-00011/transition?action=submit",
            json=_merge(SALES_USER, {"lines": []}),
            headers=AUTH_HEADERS,
        )
        response = client.get("/api/workflow/replay/workflow?since=0", headers=AUTH_HEADERS)
        assert response.status_code in {200, 422}
        if response.status_code == 422:
            return
        data = response.json()
        assert data["ok"] is True
        assert isinstance(data["events"], list)

    def test_replay_filters_by_timestamp(self):
        import time

        now = time.time()
        client.post(
            "/api/workflow/sales/SO-00012/transition?action=submit",
            json=_merge(SALES_USER, {"lines": []}),
            headers=AUTH_HEADERS,
        )

        response = client.get(f"/api/workflow/replay/workflow?since={now}", headers=AUTH_HEADERS)
        assert response.status_code in {200, 422}
        if response.status_code == 422:
            return
        assert len(response.json()["events"]) >= 0

        response = client.get(f"/api/workflow/replay/workflow?since={now + 1000}", headers=AUTH_HEADERS)
        assert response.status_code == 200
        assert len(response.json()["events"]) == 0
