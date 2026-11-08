"""Real RSA/JWKS validation and production middleware before any business access."""
import json
import time
from dataclasses import dataclass

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, Form, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

from app.auth.deps import get_current_user
from app.auth.finance_roles import finance_write
from app.core import security
from app.core.config import settings
from app.core.tenant import get_tenant_id
from app.core.tenant_binding import install_tenant_bindings
from main import BearerAuthMiddleware

ISSUER = "https://tenant-identity.invalid/realm"
AUDIENCE = "valeo-api"


class Child(BaseModel):
    tenant_id: str = "system"
    value: str = "child"


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str = "system"
    child: Child | None = None
    value: str = "unchanged"


@pytest.fixture(scope="module")
def keys():
    return [rsa.generate_private_key(public_exponent=65537, key_size=2048) for _ in range(2)]


@dataclass
class Probe:
    client: TestClient
    calls: list
    keys: list
    app: FastAPI

    def token(self, tenant="tenant-a", *, changes=None, omit=(), key=0):
        claims = {"iss": ISSUER, "aud": AUDIENCE, "exp": int(time.time()) + 300, "iat": time.time(), "sid": "test-session-" + tenant,
                  "sub": "human-a", "tenant_id": tenant, "roles": ["FINANCE_BEARBEITEN"]}
        claims.update(changes or {})
        for name in omit:
            claims.pop(name, None)
        return jwt.encode(claims, self.keys[key], algorithm="RS256", headers={"kid": "own-key"})

    def headers(self, tenant="tenant-a", **extra):
        return {"Authorization": "Bearer " + self.token(tenant), **extra}


@pytest.fixture
def probe(monkeypatch, keys):
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(keys[0].public_key()))
    jwk.update(kid="own-key", alg="RS256", use="sig")
    monkeypatch.setattr(settings, "OIDC_ISSUER_URL", ISSUER)
    monkeypatch.setattr(settings, "OIDC_CLIENT_ID", AUDIENCE)
    monkeypatch.setattr(settings, "OIDC_JWKS_URL", ISSUER + "/certs")
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "opaque-own-dev-token")
    monkeypatch.setattr(security, "_get_jwks", lambda *a, **k: [jwk])
    # This fixture isolates JWT/selector validation; shared-session enforcement
    # has its own Redis contracts and remains active in the production app.
    monkeypatch.setattr('app.core.identity_session.validate', lambda *a, **k: None)
    calls = []
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)

    @app.get('/api/identity-contract')
    def execution_identity():
        from app.core.identity_context import current_identity
        principal = current_identity()
        return {'subject': principal.subject, 'tenant': principal.tenant_id, 'representation': repr(principal)}

    @app.get("/api/probe", dependencies=[Depends(finance_write)])
    def query(tenant_id: str = Query("system"), header: str = Depends(get_tenant_id), user: dict = Depends(get_current_user)):
        calls.append((tenant_id, header, user["sub"]))
        return {"tenant": tenant_id, "header": header, "actor": user["sub"]}

    @app.post("/api/probe")
    def body(value: Input):
        calls.append(value.model_dump())
        return value

    @app.get("/api/probe/{tenant_id}")
    def path(tenant_id: str):
        calls.append(tenant_id)
        return {"tenant": tenant_id}

    @app.get("/api/many")
    def many(tenant_ids: list[str] = Query(["system"])):
        calls.append(tenant_ids)
        return tenant_ids

    @app.post("/api/form")
    def form(tenant_id: str = Form("system"), value: str = Form("ok")):
        calls.append((tenant_id, value))
        return {"tenant": tenant_id}

    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    with TestClient(app) as client:
        yield Probe(client, calls, keys, app)


@pytest.mark.parametrize("changes,omit,key", [
    ({}, ("tenant_id",), 0), ({"tenant_id": ""}, (), 0),
    ({"tenant_id": 12}, (), 0), ({"tenant_id": None}, (), 0),
    ({"mandanten_id": "tenant-b"}, (), 0), ({"mandanten_id": 12}, (), 0),
    ({"tenant_id": "x" * 65}, (), 0), ({"tenant_id": "line\r\nbreak"}, (), 0),
    ({"tenant_id": "tenant with space"}, (), 0),
    ({"tid": "directory-id"}, ("tenant_id",), 0),
    ({}, ("sub",), 0), ({"sub": ""}, (), 0),
    ({"iss": "https://foreign.invalid"}, (), 0), ({"aud": "foreign"}, (), 0),
    ({"exp": int(time.time()) - 3600}, (), 0), ({}, ("exp",), 0),
    ({}, ("iss",), 0), ({}, ("aud",), 0), ({}, (), 1),
])
def test_bad_real_tokens_never_reach_business(probe, changes, omit, key):
    token = probe.token(changes=changes, omit=omit, key=key)
    response = probe.client.get("/api/probe", headers={"Authorization": "Bearer " + token})
    assert response.status_code in (401, 403)
    assert probe.calls == []


@pytest.mark.parametrize("credential", [None, "opaque-own-dev-token", "not-a-jwt"])
def test_no_unscoped_development_or_invalid_credentials(probe, credential):
    response = probe.client.get("/api/probe", headers={"Authorization": "Bearer " + credential} if credential else {})
    assert response.status_code in (401, 403)
    assert probe.calls == []


@pytest.mark.parametrize("tenant", ["tenant-a", "tenant-b"])
def test_valid_context_replaces_query_defaults_and_binds_roles(probe, tenant):
    response = probe.client.get("/api/probe", headers=probe.headers(tenant))
    assert response.status_code == 200
    assert response.json() == {"tenant": tenant, "header": tenant, "actor": "human-a"}
    assert response.headers["x-tenant-id"] == tenant


@pytest.mark.parametrize("suffix", ["?tenant_id=tenant-b", "?tenant_id=tenant-a&tenant_id=tenant-b", "?tenant_id=", "?x_tenant_id=tenant-b"])
def test_query_override_is_rejected_before_business(probe, suffix):
    assert probe.client.get("/api/probe" + suffix, headers=probe.headers()).status_code == 403
    assert probe.calls == []


@pytest.mark.parametrize("headers", [
    [("X-Tenant-ID", "tenant-b")], [("X-Tenant", "tenant-b")],
    [("X-Tenant-ID", "tenant-a"), ("X-Tenant-ID", "tenant-b")], [("X-Tenant-ID", "")],
])
def test_all_header_values_are_bound(probe, headers):
    response = probe.client.get("/api/probe", headers=[("Authorization", "Bearer " + probe.token()), *headers])
    assert response.status_code == 403
    assert probe.calls == []


@pytest.mark.parametrize("body", [
    {"tenant_id": "tenant-b"}, {"tenant_id": ""},
    {"child": {"tenant_id": "tenant-b"}}, {"tenant_id": True},
])
def test_body_or_nested_tenant_override_is_rejected(probe, body):
    assert probe.client.post("/api/probe", json=body, headers=probe.headers()).status_code == 403
    assert probe.calls == []


def test_missing_declared_body_selectors_are_filled_without_changing_business_input(probe):
    result = probe.client.post("/api/probe", json={"value": "explicit", "child": {"value": "explicit-child"}}, headers=probe.headers("tenant-b"))
    assert result.status_code == 200
    assert result.json() == {"tenant_id": "tenant-b", "value": "explicit", "child": {"tenant_id": "tenant-b", "value": "explicit-child"}}


def test_path_and_multi_tenant_filter_cannot_cross_context(probe):
    assert probe.client.get("/api/probe/tenant-b", headers=probe.headers()).status_code == 403
    assert probe.client.get("/api/many?tenant_ids=tenant-a&tenant_ids=tenant-b", headers=probe.headers()).status_code == 403
    assert probe.calls == []
    assert probe.client.get("/api/many", headers=probe.headers()).json() == ["tenant-a"]


def test_form_defaults_and_overrides_are_bound(probe):
    assert probe.client.post("/api/form", data={"tenant_id": "tenant-b"}, headers=probe.headers()).status_code == 403
    assert probe.calls == []
    response = probe.client.post("/api/form", data={"value": "input"}, headers=probe.headers("tenant-b"))
    assert response.status_code == 200
    assert response.json() == {"tenant": "tenant-b"}


def test_no_context_bleed_across_success_rejection_and_next_request(probe):
    assert probe.client.get("/api/probe", headers=probe.headers()).json()["tenant"] == "tenant-a"
    assert probe.client.get("/api/probe?tenant_id=tenant-a", headers=probe.headers("tenant-b")).status_code == 403
    assert probe.client.get("/api/probe", headers=probe.headers("tenant-b")).json()["tenant"] == "tenant-b"
    assert probe.calls == [("tenant-a", "tenant-a", "human-a"), ("tenant-b", "tenant-b", "human-a")]


def test_every_registered_protected_http_route_is_bound_and_installation_idempotent(probe):
    first = install_tenant_bindings(probe.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    second = install_tenant_bindings(probe.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    assert first == second and len(first) == 6


def test_execution_identity_is_scoped_and_does_not_expose_credentials(probe):
    from app.core.identity_context import current_identity
    token = probe.token('tenant-b')
    result = probe.client.get('/api/identity-contract', headers={'Authorization': 'Bearer '+token})
    assert result.status_code == 200
    assert result.json()['subject'] == 'human-a'
    assert result.json()['tenant'] == 'tenant-b'
    assert token not in result.json()['representation']
    with pytest.raises(HTTPException) as error:
        current_identity()
    assert error.value.status_code == 401
