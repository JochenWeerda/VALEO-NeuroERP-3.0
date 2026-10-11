"""Real HTTP dependencies and outbox effects; OIDC provider is the only auth boundary replaced."""
from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import whatsapp_notify as endpoint
from app.auth.deps_oidc import oidc
from app.services import whatsapp_notify_service as service


@pytest.fixture
def client(monkeypatch):
    from sqlalchemy.engine import Engine

    def forbidden_database(*args, **kwargs):
        pytest.fail("WhatsApp outbox access tests must not connect to a database")

    monkeypatch.setattr(Engine, "connect", forbidden_database)
    service._OUTBOX.clear()
    claims = {
        "a": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "crm:read crm:write"},
        "b": {"sub": "actor-b", "tenant_id": "tenant-b", "scope": "crm:read crm:write"},
        "alias": {"sub": "actor-a", "mandanten_id": "tenant-a", "scope": "crm:read crm:write"},
        "read": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "crm:read"},
        "write": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "crm:write"},
        "admin": {"sub": "actor-a", "tenant_id": "tenant-a", "scope": "admin:all"},
        "none": {"sub": "actor-a", "tenant_id": "tenant-a"},
        "no-tenant": {"sub": "actor-a", "scope": "admin:all"},
        "no-actor": {"tenant_id": "tenant-a", "scope": "admin:all"},
        "conflict": {"sub": "actor-a", "tenant_id": "tenant-a", "mandanten_id": "tenant-b", "scope": "admin:all"},
    }

    async def verify(token):
        if token not in claims:
            raise ValueError("Rejected test token")
        return deepcopy(claims[token])

    monkeypatch.setattr(oidc, "verify", verify)
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/whatsapp")
    with TestClient(app) as client:
        yield client
    service._OUTBOX.clear()


def headers(token="a", **extra):
    return {"Authorization": f"Bearer {token}", **extra}


DELIVERY = {"phone": "+491700000001", "artikel": "Weizen", "menge": 2}
DOCUMENT = {"phone": "+491700000001", "doc_typ": "Rechnung", "doc_nr": "RE-1"}
WRITES = [("/dev/notify/lieferankuendigung", DELIVERY), ("/dev/notify/dokument-ready", DOCUMENT)]


@pytest.mark.parametrize("path,body", WRITES)
def test_token_tenant_is_used_when_body_omits_tenant(client, path, body):
    result = client.post("/whatsapp" + path, json=body, headers=headers())
    assert result.status_code == 200
    assert result.json()["status"] == "pending_browser"
    assert len(service.get_outbox("tenant-a")) == 1
    assert service.get_outbox("dev-tenant") == []
    assert service.get_outbox("tenant-b") == []


@pytest.mark.parametrize("path,body", WRITES)
@pytest.mark.parametrize("token", ["no-tenant", "no-actor", "conflict", "none", "read", "invalid"])
def test_rejected_identity_or_scope_never_writes(client, path, body, token):
    result = client.post("/whatsapp" + path, json=body, headers=headers(token))
    assert result.status_code in (401, 403)
    assert service._OUTBOX == {}


@pytest.mark.parametrize("path,body", WRITES)
@pytest.mark.parametrize("override", [{"tenant_id": "tenant-b"}, {"tenant_id": ""}, {"tenant_id": "dev-tenant"}])
def test_payload_tenant_cannot_override_verified_context(client, path, body, override):
    result = client.post("/whatsapp" + path, json={**body, **override}, headers=headers())
    assert result.status_code == 403
    assert service._OUTBOX == {}


@pytest.mark.parametrize("token,tenant,phone", [("a", "tenant-a", "+491700000001"), ("admin", "tenant-a", "+491700000001"), ("b", "tenant-b", "+491700000002")])
def test_outbox_is_scoped_to_verified_identity_even_for_admin(client, token, tenant, phone):
    service.send_dokument_ready("tenant-a", "+491700000001", None, None, "Rechnung", "RE-A")
    service.send_dokument_ready("tenant-b", "+491700000002", None, None, "Rechnung", "RE-B")
    result = client.get("/whatsapp/dev/outbox", headers=headers(token))
    assert result.status_code == 200
    assert result.json()["tenant_id"] == tenant
    assert [m["phone"] for m in result.json()["messages"]] == [phone]
    foreign = "tenant-b" if tenant == "tenant-a" else "tenant-a"
    assert client.get("/whatsapp/dev/outbox?tenant_id=" + foreign, headers=headers(token)).status_code == 403


@pytest.mark.parametrize("token", ["none", "write", "no-tenant", "no-actor", "conflict", "invalid"])
def test_read_rejects_missing_scope_or_identity(client, token):
    result = client.get("/whatsapp/dev/outbox", headers=headers(token))
    assert result.status_code in (401, 403)


@pytest.mark.parametrize("path,body", WRITES)
def test_mismatched_header_is_rejected_before_mutation(client, path, body):
    result = client.post("/whatsapp" + path, json=body, headers=headers(**{"X-Tenant-ID": "tenant-b"}))
    assert result.status_code == 403
    assert service._OUTBOX == {}


def test_missing_bearer_cannot_read_or_write(client):
    assert client.get("/whatsapp/dev/outbox").status_code in (401, 403)
    for path, body in WRITES:
        assert client.post("/whatsapp" + path, json=body).status_code in (401, 403)
    assert service._OUTBOX == {}


@pytest.mark.parametrize("token", ["a", "alias"])
def test_matching_explicit_tenant_and_alias_work(client, token):
    for path, body in WRITES:
        assert client.post("/whatsapp" + path, json={**body, "tenant_id": "tenant-a"}, headers=headers(token)).status_code == 200
    result = client.get("/whatsapp/dev/outbox?tenant_id=tenant-a", headers=headers(token, **{"X-Tenant-ID": "tenant-a"}))
    assert result.status_code == 200
    assert len(result.json()["messages"]) == 2
