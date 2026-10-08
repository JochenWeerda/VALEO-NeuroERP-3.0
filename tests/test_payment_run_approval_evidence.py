"""Approval requires evidence of two distinct authenticated people in every mode."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.endpoints.mask_actions import router
from app.services.payment_run_freigabe import pruefe_freigabe


class Result:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row

    def scalar(self):
        return self.row[0] if self.row else None


class ApprovalDb:
    def __init__(self, row):
        self.row = row
        self.calls = []
        self.commits = 0
        self.rollbacks = 0

    def execute(self, statement, parameters=None):
        sql = str(statement)
        self.calls.append((sql, parameters))
        assert sql.lstrip().startswith("SELECT"), "Rejected/preview approval must not write"
        return Result(self.row)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


@pytest.fixture(autouse=True)
def no_database_connections(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Isolated approval contracts cannot connect to a database")

    monkeypatch.setattr(Engine, "connect", forbidden)


@pytest.mark.parametrize("approver", ["", " ", "\t"])
def test_missing_approver_is_rejected_before_any_database_access(approver):
    db = ApprovalDb(("draft", "maker"))
    with pytest.raises(HTTPException) as error:
        pruefe_freigabe(db, "run-id", "own-tenant", approver)
    assert error.value.status_code == 403
    assert db.calls == []


@pytest.mark.parametrize("creator", [None, "", "  "])
def test_missing_creator_is_not_a_four_eyes_exception(creator):
    db = ApprovalDb(("draft", creator))
    with pytest.raises(HTTPException) as error:
        pruefe_freigabe(db, "run-id", "own-tenant", "reviewer")
    assert error.value.status_code == 409
    assert db.commits == 0


@pytest.mark.parametrize("status", ["approved", "executed", "cancelled"])
def test_only_a_draft_can_be_approved(status):
    with pytest.raises(HTTPException) as error:
        pruefe_freigabe(ApprovalDb((status, "maker")), "run-id", "own-tenant", "reviewer")
    assert error.value.status_code == 409


@pytest.mark.parametrize("creator", ["maker", " maker "])
def test_creator_cannot_approve_their_own_run(creator):
    with pytest.raises(HTTPException) as error:
        pruefe_freigabe(ApprovalDb(("draft", creator)), "run-id", "own-tenant", "maker")
    assert error.value.status_code == 409


def test_foreign_or_missing_run_stays_not_found():
    db = ApprovalDb(None)
    with pytest.raises(HTTPException) as error:
        pruefe_freigabe(db, "foreign-id", "own-tenant", "reviewer")
    assert error.value.status_code == 404
    assert db.calls[0][1] == {"run_id": "foreign-id", "tenant_id": "own-tenant"}


def test_two_known_people_can_approve_a_locked_own_draft():
    db = ApprovalDb(("draft", "maker"))
    pruefe_freigabe(db, "run-id", "own-tenant", "reviewer")
    assert "FOR UPDATE" in db.calls[0][0]
    assert db.calls[0][1] == {"run_id": "run-id", "tenant_id": "own-tenant"}
    assert db.commits == 0


def client_for(db, user):
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "own-tenant"
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose", "execute"])
@pytest.mark.parametrize("creator", [None, "reviewer"])
def test_actual_command_endpoint_rejects_unproven_approval_in_every_mode(mode, creator):
    db = ApprovalDb(("draft", creator))
    with client_for(db, {"sub": "reviewer", "roles": ["FINANCE_ADMIN"]}) as client:
        response = client.post(
            "/api/v1/finance/payment-runs/run-id/actions/freigeben",
            json={"_mode": mode, "_auditReason": "approval evidence check"},
        )
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["validationErrors"]
    assert db.commits == 0
    assert all(sql.lstrip().startswith("SELECT") for sql, _ in db.calls)


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose"])
def test_actual_command_preview_passes_for_distinct_people_without_writes(mode):
    db = ApprovalDb(("draft", "maker"))
    with client_for(db, {"sub": "reviewer", "roles": ["FINANCE_ADMIN"]}) as client:
        response = client.post(
            "/api/v1/finance/payment-runs/run-id/actions/freigeben", json={"_mode": mode}
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["mode"] == mode
    assert db.commits == 0


def test_reader_cannot_reach_the_approval_database():
    db = ApprovalDb(("draft", "maker"))
    with client_for(db, {"sub": "reader", "roles": ["FINANCE_LESEN"]}) as client:
        response = client.post(
            "/api/v1/finance/payment-runs/run-id/actions/freigeben", json={"_mode": "dryRun"}
        )
    assert response.status_code == 403
    assert db.calls == []
