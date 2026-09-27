"""Real RSA verification through the MCP HTTP dependency (no auth override)."""
import importlib
import json
import time
from unittest.mock import Mock

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
import jwt
import pytest

from app.api.v1.endpoints.mcp_tool_registry import router, get_db

oidc_module = importlib.import_module("app.auth.oidc")


@pytest.fixture(scope="module")
def signing_keys():
    return [rsa.generate_private_key(public_exponent=65537, key_size=2048) for _ in range(2)]


@pytest.fixture
def secured_client(monkeypatch, signing_keys):
    public_key = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(signing_keys[0].public_key()))
    public_key.update(kid="test-key", alg="RS256", use="sig")
    # Only provider configuration/key distribution is supplied by the fixture.
    # Token parsing, signature, claims and endpoint authorization run unchanged.
    monkeypatch.setattr(oidc_module, "OIDC_ISSUER", "https://identity.test/realm")
    monkeypatch.setattr(oidc_module, "OIDC_AUDIENCE", "valeo-erp")
    monkeypatch.setattr(oidc_module.oidc, "jwks", {"keys": [public_key]})
    monkeypatch.setattr(oidc_module.oidc, "exp", time.time() + 600)
    app = FastAPI()
    app.include_router(router)
    db = Mock()
    db.execute.return_value.first.return_value = (1,)
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client, db


def token(signing_keys, changes=None, omit=None, key=0):
    claims = {"iss": "https://identity.test/realm", "aud": "valeo-erp", "sub": "test-agent",
              "exp": int(time.time()) + 300, "scope": "crm:write", "tenant_id": "tenant-a"}
    claims.update(changes or {})
    if omit:
        claims.pop(omit)
    return jwt.encode(claims, signing_keys[key], algorithm="RS256", headers={"kid": "test-key"})


def call(client, bearer, tenant="tenant-a"):
    return client.post('/mcp/tools/call', headers={"Authorization": f"Bearer {bearer}", "X-Tenant-ID": tenant},
                       json={"tool_name": "crm.contact.log", "parameters": {
                           "kunden_nr": "TEST", "kanal": "telefon", "ergebnis": "Synthetic test"}})


def test_valid_signed_token_reaches_read_only_preview(secured_client, signing_keys):
    client, db = secured_client
    response = call(client, token(signing_keys))
    assert response.status_code == 200
    assert response.json()["mode"] == "dryRun"
    db.commit.assert_not_called()


@pytest.mark.parametrize("omit", ["exp", "iss", "aud", "sub"])
def test_required_claim_cannot_be_omitted(secured_client, signing_keys, omit):
    client, db = secured_client
    assert call(client, token(signing_keys, omit=omit)).status_code == 401
    db.execute.assert_not_called()


@pytest.mark.parametrize("changes", [
    {"exp": 1}, {"iss": "https://other.test"}, {"aud": "another-service"},
    {"sub": " "}, {"nbf": 9999999999},
])
def test_invalid_claims_cannot_reach_database(secured_client, signing_keys, changes):
    client, db = secured_client
    assert call(client, token(signing_keys, changes)).status_code == 401
    db.execute.assert_not_called()


def test_wrong_signing_key_is_rejected(secured_client, signing_keys):
    client, db = secured_client
    assert call(client, token(signing_keys, key=1)).status_code == 401
    db.execute.assert_not_called()


@pytest.mark.parametrize("changes,tenant", [
    ({"scope": "crm:read"}, "tenant-a"), ({}, "tenant-b"), ({"tenant_id": None}, "tenant-a"),
])
def test_valid_signature_does_not_replace_authorization(secured_client, signing_keys, changes, tenant):
    client, db = secured_client
    assert call(client, token(signing_keys, changes), tenant).status_code == 403
    db.execute.assert_not_called()


@pytest.mark.parametrize("setting", ["OIDC_ISSUER", "OIDC_AUDIENCE"])
def test_incomplete_verifier_configuration_rejects_even_cached_keys(secured_client, signing_keys, monkeypatch, setting):
    client, db = secured_client
    monkeypatch.setattr(oidc_module, setting, "")
    assert call(client, token(signing_keys)).status_code == 401
    db.execute.assert_not_called()
