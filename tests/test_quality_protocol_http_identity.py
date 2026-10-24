"""Signed JWT, tenant, and actor contract at the real HTTP dependency boundary."""

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import quality_protocols as api
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from main import BearerAuthMiddleware
from test_system_tenant_binding import keys, probe  # noqa: F401


def test_finalize_binds_approver_to_verified_token_and_rejects_foreign_identity(probe, monkeypatch):
    fields = {name: None for name in api.QualityProtocolOut.model_fields}
    fields.update(id="protocol-a", tenant_id="tenant-a", protocol_number="SYNTH-QS", version=1, is_final=False)
    protocol = SimpleNamespace(**fields)
    calls = []

    class Repo:
        def __init__(self, db, tenant_id):
            self.tenant_id = tenant_id

        def get_by_id(self, protocol_id):
            calls.append(("read", self.tenant_id, protocol_id))
            return protocol if self.tenant_id == "tenant-a" else None

    class Outbox:
        def __init__(self, db, publisher):
            pass

        async def store_event(self, event, **kwargs):
            calls.append(("outbox", event.payload["approved_by"], kwargs))

    db = SimpleNamespace(commit=lambda: calls.append(("commit",)), rollback=lambda: calls.append(("rollback",)))
    monkeypatch.setattr(api, "QualityProtocolRepositoryImpl", Repo)
    monkeypatch.setattr(api, "OutboxPublisher", Outbox)
    monkeypatch.setattr(api, "get_event_publisher", lambda: object())

    def finalize(repo, protocol_id, approved_by):
        calls.append(("finalize", approved_by))
        protocol.is_final = True
        protocol.approved_by = approved_by
        return protocol

    monkeypatch.setattr(api, "finalize_quality_protocol", finalize)
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(api.router, prefix="/api/v1/agrar/quality-protocols")
    app.dependency_overrides[get_db] = lambda: db
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    path = "/api/v1/agrar/quality-protocols/protocol-a/finalize"
    token = lambda tenant="tenant-a", **options: {
        "Authorization": "Bearer " + probe.token(tenant, changes={"roles": ["AGRAR_BEARBEITEN"], **options})
    }

    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.post(path, json={"approved_by": "forged"}).status_code == 401
        assert client.post(path, headers={**token(), "X-Tenant-ID": "tenant-b", "X-User-ID": "forged"}, json={"approved_by": "forged"}).status_code == 403
        assert client.post(path, headers=token("tenant-b"), json={"approved_by": "forged"}).status_code == 404
        assert not any(call[0] == "finalize" for call in calls)
        response = client.post(path, headers={**token(), "X-User-ID": "forged"}, json={"approved_by": "forged"})
    assert response.status_code == 200, response.text
    assert response.json()["approved_by"] == "human-a"
    assert ("finalize", "human-a") in calls
    assert ("outbox", "human-a", {"tenant_id": "tenant-a", "mirror_on_store": False}) in calls
    assert calls[-1] == ("commit",)
