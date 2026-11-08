"""Transport, role projection, privacy and actual SQL domain-command parity."""
from unittest.mock import MagicMock
from uuid import uuid4
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.endpoints import harvest_acceptance as api
from test_harvest_rule_store_sql import case, ready


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


def client(db, tenant, principal, *, verified=True):
    app = FastAPI(); app.include_router(api.router, prefix="/harvest")
    principal = dict(principal, raw=dict(principal.get("raw") or {}, sub=principal["sub"]))
    app.dependency_overrides[get_current_user] = lambda: principal
    app.dependency_overrides[get_db] = lambda: db
    def tenant_context(request: Request):
        request.state.tenant_verified = verified
        request.state.token_claims = principal["raw"]
        return tenant
    app.dependency_overrides[get_tenant_id] = tenant_context
    return TestClient(app)


@pytest.mark.parametrize("path", ["/settlement-controls/rules", "/settlement-controls/rules/id/approve",
    "/settlement-controls/rules/id/revoke", "/settlement-controls/acceptances/id/bind-rule",
    "/settlement-controls/acceptances/id/attest-measurement", "/settlement-controls/acceptances/id/approve-calculation",
    "/id/calculate", "/id/release?release_status=final&create_credit_note=true"])
def test_read_only_actor_is_rejected_before_any_database_access(path):
    db = MagicMock()
    response = client(db, "own", {"sub": "reader", "roles": ["EINKAUF_LESEN"],
        "raw": {"iss": "urn:synthetic", "identity_type": "human"}}).post("/harvest" + path, json={})
    assert response.status_code == 403
    db.query.assert_not_called(); db.execute.assert_not_called()


def test_context_must_be_verified_before_storage():
    db = MagicMock()
    response = client(db, "own", {"sub": "editor", "roles": ["EINKAUF_BEARBEITEN"],
        "raw": {"iss": "urn:synthetic", "identity_type": "human"}}, verified=False).get("/harvest/settlement-controls/rules")
    assert response.status_code == 403
    db.query.assert_not_called(); db.execute.assert_not_called()


def test_validation_does_not_echo_values_or_accept_actor_override():
    db = MagicMock(); sentinel = "PRIVATE_VALIDATION_SENTINEL"
    response = client(db, "own", {"sub": "editor", "roles": ["EINKAUF_BEARBEITEN"],
        "raw": {"iss": "urn:synthetic", "identity_type": "human"}}).post("/harvest/settlement-controls/rules", json={
            "actor": sentinel, "idempotency_key": str(uuid4()), "rule_id": sentinel, "expected_version": 0,
            "terms": {"customer_id": sentinel}})
    assert response.status_code == 422
    assert sentinel not in response.text
    assert all("input" not in error for error in response.json()["detail"])
    db.execute.assert_not_called()


def test_http_calculation_uses_the_same_persistent_domain_proof(case):
    c = case; ready(c)
    http = client(c.db, c.tenant, c.editor)
    context = http.get(f"/harvest/settlement-controls/acceptances/{c.acceptance.id}/context")
    assert context.status_code == 200
    body = {"idempotency_key": str(uuid4()), "expected_context_hash": context.json()["context_hash"]}
    result = http.post(f"/harvest/{c.acceptance.id}/calculate", json=body)
    assert result.status_code == 200, result.text
    assert result.json()["total_net_amount_eur"] == 5417.5 and result.json()["calculation_hash"]
    assert http.post(f"/harvest/{c.acceptance.id}/calculate", json=body).json() == result.json()
    history = http.get(f"/harvest/settlement-controls/acceptances/{c.acceptance.id}/history").json()
    assert history["items"][0]["action"] == "calculation.completed"
    assert history["items"][0]["actor"] == c.editor["sub"]
    history_path = f"/harvest/settlement-controls/acceptances/{c.acceptance.id}/history"
    first_page = http.get(history_path, params={"page": 1, "limit": 1}).json()
    second_page = http.get(history_path, params={"page": 2, "limit": 1}).json()
    explicit_offset = http.get(history_path, params={"offset": 1, "limit": 1}).json()
    assert first_page["items"] != second_page["items"]
    assert second_page == explicit_offset


def test_choices_and_permissions_do_not_leak_or_grant_another_tenant(case):
    c = case
    own = client(c.db, c.tenant, c.editor)
    permissions = own.get("/harvest/settlement-controls/permissions").json()["allowed_actions"]
    assert "calculate" in permissions and "approve_rule" not in permissions and "approve_calculation" not in permissions
    other = client(c.db, str(uuid4()), c.editor)
    assert other.get("/harvest/settlement-controls/choices/article?q=Synthetic").json()["items"] == []
    assert other.get(f"/harvest/settlement-controls/acceptances/{c.acceptance.id}/context").status_code == 404
