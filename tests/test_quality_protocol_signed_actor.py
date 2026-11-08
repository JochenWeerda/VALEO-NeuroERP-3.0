"""Real RSA/JWKS authentication binds quality approval to the signed subject."""
import json
import time
from types import SimpleNamespace
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.endpoints import quality_protocols as api
from app.core import security
from app.core.config import settings
from app.core.database import get_db

@pytest.mark.parametrize("case,expected", [("forged-body", 200), ("invalid-token", 401), ("missing-role", 403)])
def test_signed_http_finalization_uses_token_actor(monkeypatch, case, expected):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
    jwk.update(kid="quality-closure", alg="RS256", use="sig")
    issuer = "https://quality-closure.invalid/realm"
    monkeypatch.setattr(settings, "OIDC_ISSUER_URL", issuer)
    monkeypatch.setattr(settings, "OIDC_CLIENT_ID", "valeo-api")
    monkeypatch.setattr(settings, "OIDC_JWKS_URL", issuer + "/certs")
    monkeypatch.setattr(security, "_get_jwks", lambda *a, **k: [jwk])
    monkeypatch.setattr("app.core.identity_session.validate", lambda *a, **k: None)
    captured = {}
    protocol = SimpleNamespace(id="synthetic-protocol", tenant_id="tenant-a", harvest_acceptance_id=None, is_final=False)
    class Repo:
        def __init__(self, db, tenant_id):
            assert tenant_id == "tenant-a"
        def get_by_id(self, identity):
            return protocol
    class Db:
        def commit(self):
            captured["committed"] = True
        def rollback(self):
            captured["rollback"] = True
    class Outbox:
        def __init__(self, db, publisher):
            pass
        async def store_event(self, event, **kwargs):
            captured["event_actor"] = event.payload["approved_by"]
    def finalize(repo, identity, actor):
        captured["actor"] = actor
        return protocol
    monkeypatch.setattr(api, "QualityProtocolRepositoryImpl", Repo)
    monkeypatch.setattr(api, "OutboxPublisher", Outbox)
    monkeypatch.setattr(api, "get_event_publisher", lambda: object())
    monkeypatch.setattr(api, "finalize_quality_protocol", finalize)
    monkeypatch.setattr(api, "_to_out", lambda value: api.QualityProtocolOut(id=value.id, tenant_id=value.tenant_id, protocol_number="SYNTH", version=1, is_final=True, approved_by=captured["actor"]))
    app = FastAPI()
    app.include_router(api.router, prefix="/quality")
    app.dependency_overrides[get_db] = lambda: Db()
    claims = dict(iss=issuer, aud="valeo-api", sub="signed-subject", tenant_id="tenant-a", exp=int(time.time())+300, iat=int(time.time()), sid="synthetic-session", realm_access={"roles": [] if case == "missing-role" else ["AGRAR_BEARBEITEN"]})
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048) if case == "invalid-token" else private
    token = jwt.encode(claims, key, algorithm="RS256", headers={"kid": "quality-closure"})
    with TestClient(app) as client:
        response = client.post("/quality/synthetic-protocol/finalize", json={"approved_by":"forged-client-actor"}, headers={"Authorization":"Bearer "+token, "X-User-ID":"forged-header-actor"})
    assert response.status_code == expected, response.text
    if expected == 200:
        assert captured["actor"] == captured["event_actor"] == response.json()["approved_by"] == "signed-subject"
        assert captured["committed"] is True
    else:
        assert "actor" not in captured and "committed" not in captured
