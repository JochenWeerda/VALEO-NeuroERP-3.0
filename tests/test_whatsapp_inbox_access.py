"""Real HTTP auth dependencies; the service spy proves rejection before data access."""
from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import whatsapp_intake as endpoint
from app.auth.deps_oidc import oidc
from app.core.database import get_db


PATH = "/crm/bestell-inbox"
OPERATIONS = [
    ("GET", PATH, None, "read"),
    ("GET", PATH + "/item", None, "read"),
    ("POST", PATH, {"raw_text": "Probe"}, "write"),
    ("POST", PATH + "/item/bestaetigen", {}, "write"),
    ("POST", PATH + "/item/verwerfen", {}, "write"),
]


@pytest.fixture
def http(monkeypatch):
    calls = []
    claims = {
        "a": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "crm:read crm:write"},
        "b": {"sub": "actor-b", "tenant_id": "tenant-b", "scope": "crm:read crm:write"},
        "alias": {"sub": "actor-a", "mandanten_id": "tenant-a", "scope": "crm:read crm:write"},
        "admin": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "admin:all"},
        "read": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "crm:read"},
        "write": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "crm:write"},
        "none": {"sub": "actor-a", "tenant_id": "tenant-a"},
        "no-tenant": {"sub": "actor-a", "scope": "admin:all"},
        "no-actor": {"tenant_id": "tenant-a", "scope": "admin:all"},
        "conflict": {"sub": "actor-a", "tenant_id": "tenant-a", "mandanten_id": "tenant-b", "scope": "admin:all"},
    }

    async def verify(token):
        if token not in claims:
            raise ValueError("Rejected test token")
        return deepcopy(claims[token])

    class ServiceSpy:
        def __init__(self, db, tenant):
            calls.append(("context", tenant))

        def create_inbox(self, *args):
            return {"id": "item"}

        def get(self, *args):
            return {"id": "item"}

        def list_inbox(self, *args):
            return []

        def bestaetigen(self, *args, actor):
            calls.append(("actor", actor))
            return {"id": "item"}

        def verwerfen(self, *args):
            return {"id": "item"}

    monkeypatch.setattr(oidc, "verify", verify)
    monkeypatch.setattr(endpoint, "WhatsAppIntakeService", ServiceSpy)
    app = FastAPI()
    app.include_router(endpoint.router)
    app.dependency_overrides[get_db] = lambda: None
    with TestClient(app) as client:
        yield client, calls


@pytest.mark.parametrize("method,path,body,scope", OPERATIONS)
@pytest.mark.parametrize("token", [None, "invalid", "none", "no-tenant", "no-actor", "conflict"])
def test_invalid_identity_never_reaches_service(http, method, path, body, scope, token):
    client, calls = http
    headers = {"Authorization": "Bearer " + token} if token else {}
    response = client.request(method, path, json=body, headers=headers)
    assert response.status_code in (401, 403)
    assert calls == []


@pytest.mark.parametrize("method,path,body,scope", OPERATIONS)
def test_wrong_scope_or_foreign_header_never_reaches_service(http, method, path, body, scope):
    client, calls = http
    wrong = "write" if scope == "read" else "read"
    assert client.request(method, path, json=body, headers={"Authorization": "Bearer " + wrong}).status_code == 403
    assert client.request(method, path, json=body, headers={"Authorization": "Bearer admin", "X-Tenant-ID": "tenant-b"}).status_code == 403
    assert calls == []


@pytest.mark.parametrize("method,path,body,scope", OPERATIONS)
@pytest.mark.parametrize("token,tenant", [("a", "tenant-a"), ("b", "tenant-b"), ("alias", "tenant-a"), ("admin", "tenant-a")])
def test_accepted_identity_keeps_token_tenant(http, method, path, body, scope, token, tenant):
    client, calls = http
    assert client.request(method, path, json=body, headers={"Authorization": "Bearer " + token}).status_code == 200
    assert calls[0] == ("context", tenant)
    if path.endswith("bestaetigen"):
        assert calls[1] == ("actor", "actor-b" if token == "b" else "actor-a")


@pytest.mark.parametrize("method,path,body,scope", [op for op in OPERATIONS if op[3] == "write"][:2])
def test_payload_cannot_supply_tenant_or_actor(http, method, path, body, scope):
    client, calls = http
    response = client.request(method, path, json={**body, "tenant_id": "tenant-b", "actor": "forged"}, headers={"Authorization": "Bearer a"})
    assert response.status_code == 422
    assert calls == []


def test_unknown_document_type_is_rejected(http):
    client, calls = http
    assert client.post(PATH + "/item/bestaetigen", json={"beleg_typ": "arbitrary"}, headers={"Authorization": "Bearer a"}).status_code == 422
    assert calls == []


@pytest.mark.parametrize("tenant", [None, "", "   ", "x" * 65, 1])
def test_service_has_no_default_tenant(tenant):
    from app.services.whatsapp_intake_service import WhatsAppIntakeService
    with pytest.raises(ValueError, match="Explicit tenant"):
        WhatsAppIntakeService(None, tenant)
