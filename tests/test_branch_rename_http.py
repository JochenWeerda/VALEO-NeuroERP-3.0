"""HTTP contract for the administrative Studio branch command."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.api.v1.endpoints import branches
from app.auth.deps import get_current_user


PATH = "/admin/branches/branch-1/actions/bearbeiten"
BODY = {"name": "Nordwest", "expected_version": 123, "_auditReason": "Korrektur", "_idempotencyKey": "rename-1"}


@pytest.fixture
def branch_http(monkeypatch):
    app = FastAPI()
    app.include_router(branches.router)
    identity = {"roles": ["admin"], "sub": "synthetic-admin"}
    calls = []

    def current_user(request: Request):
        request.state.token_claims = dict(identity)
        return dict(identity)

    async def delegate(db, **kwargs):
        calls.append(kwargs)
        return branches.MaskActionResult(actionKey="bearbeiten", mode=kwargs["body"]["_mode"], success=True)

    app.dependency_overrides[get_current_user] = current_user
    app.dependency_overrides[branches.get_tenant_id] = lambda: "synthetic-tenant"
    app.dependency_overrides[branches.get_db] = object
    monkeypatch.setattr(branches, "run_delegated_mask_action", delegate)
    with TestClient(app) as client:
        yield client, identity, calls


@pytest.mark.parametrize("roles", [[], ["FINANCE_ADMIN"], ["portal_customer"]])
def test_branch_rename_requires_admin(branch_http, roles):
    client, identity, calls = branch_http
    identity["roles"] = roles
    assert client.post(PATH, json=BODY).status_code == 403
    assert not calls


@pytest.mark.parametrize("field", ["expected_version", "_auditReason", "_idempotencyKey"])
def test_branch_execute_requires_controls(branch_http, field):
    client, _, calls = branch_http
    assert client.post(PATH, json={key: value for key, value in BODY.items() if key != field}).status_code == 422
    assert not calls


def test_branch_preview_and_execution_use_verified_context(branch_http):
    client, identity, calls = branch_http
    preview = {"name": BODY["name"], "expected_version": BODY["expected_version"], "_mode": "dryRun"}
    assert client.post(PATH, json=preview).status_code == 200
    assert client.post(PATH, json=BODY).status_code == 200
    dry_run, execute = calls
    assert dry_run["body"]["_mode"] == "dryRun"
    assert execute["body"]["_mode"] == "execute"
    assert execute["performed_by"] == identity["sub"]
    assert execute["tenant_id"] == "synthetic-tenant"
