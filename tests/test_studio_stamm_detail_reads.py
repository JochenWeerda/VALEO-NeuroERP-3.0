"""Signed HTTP reads with actual SQL and two tenants; no external database.

JWT validation is real RSA/JWKS. Shared-session enforcement is isolated here;
its Redis contracts remain separate. Business data is SQLite memory only.
"""
import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from starlette.routing import Match

from app.api.v1.endpoints import artikel_mengeneinheiten as units, individuelle_artikelnummern as numbers
from app.core import security
from app.core.config import settings
from app.core.database import get_db

ISSUER = "https://studio-stamm.invalid/realm"


@pytest.fixture
def probe(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
    jwk.update(kid="studio-stamm", alg="RS256", use="sig")
    monkeypatch.setattr(settings, "OIDC_ISSUER_URL", ISSUER)
    monkeypatch.setattr(settings, "OIDC_CLIENT_ID", "valeo-api")
    monkeypatch.setattr(settings, "OIDC_JWKS_URL", ISSUER + "/certs")
    monkeypatch.setattr(security, "_get_jwks", lambda *a, **k: [jwk])
    monkeypatch.setattr("app.core.identity_session.validate", lambda *a, **k: None)
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    with engine.begin() as c:
        c.exec_driver_sql("ATTACH DATABASE ':memory:' AS domain_shared")
        c.exec_driver_sql("CREATE TABLE domain_shared.artikel_mengeneinheiten (id TEXT, tenant_id TEXT, einheit_kuerzel TEXT, bezeichnung TEXT, basis_einheit TEXT, umrechnungsfaktor NUMERIC, dezimalstellen INTEGER, aktiv BOOLEAN, created_at TEXT)")
        c.exec_driver_sql("CREATE TABLE domain_shared.individuelle_artikelnummern (id TEXT, tenant_id TEXT, artikel_nr TEXT, partner_nr TEXT, partner_typ TEXT, indiv_artikel_nr TEXT, indiv_bezeichnung TEXT, gueltig_von TEXT, gueltig_bis TEXT, aktiv BOOLEAN, created_at TEXT)")
        for tenant, active, key in [("tenant-a", True, "own"), ("tenant-b", True, "foreign"), ("tenant-a", False, "inactive")]:
            c.execute(text("INSERT INTO domain_shared.artikel_mengeneinheiten VALUES (:key,:tenant,:key,:tenant,NULL,NULL,3,:active,'2026-10-23T12:00:00')"), dict(key=key, tenant=tenant, active=active))
            c.execute(text("INSERT INTO domain_shared.individuelle_artikelnummern VALUES (:key,:tenant,'SYNTH-ARTICLE','SYNTH-PARTNER','kunden',:key,NULL,NULL,NULL,:active,'2026-10-23T12:00:00')"), dict(key=key, tenant=tenant, active=active))
    app = FastAPI()
    app.include_router(units.router, prefix="/api/v1")
    app.include_router(numbers.router, prefix="/api/v1")
    def session():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = session
    claims = {"iss": ISSUER, "aud": "valeo-api", "sub": "synthetic-studio-user", "tenant_id": "tenant-a", "exp": int(time.time()) + 300, "iat": int(time.time()), "sid": "synthetic-studio-session"}
    token = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "studio-stamm"})
    with TestClient(app) as client:
        yield client, {"Authorization": "Bearer " + token}, app
    engine.dispose()


@pytest.mark.parametrize("path,identity", [
    ("/api/v1/artikel/mengeneinheiten/stamm/", "einheit_kuerzel"),
    ("/api/v1/artikel/individuelle-nummern/", "id"),
])
def test_signed_detail_returns_one_own_record(probe, path, identity):
    client, headers, _ = probe
    response = client.get(path + "own", headers=headers)
    assert response.status_code == 200, response.text
    record = response.json()
    assert isinstance(record, dict) and record[identity] == "own"
    assert "tenant_id" not in record


@pytest.mark.parametrize("key", ["foreign", "inactive", "missing"])
@pytest.mark.parametrize("path", ["/api/v1/artikel/mengeneinheiten/stamm/", "/api/v1/artikel/individuelle-nummern/"])
def test_foreign_missing_and_inactive_are_indistinguishable(probe, path, key):
    client, headers, _ = probe
    assert client.get(path + key, headers=headers).status_code == 404


@pytest.mark.parametrize("path", ["/api/v1/artikel/mengeneinheiten/stamm/own", "/api/v1/artikel/individuelle-nummern/own"])
def test_missing_token_and_forged_selector_cannot_read(probe, path):
    client, headers, _ = probe
    assert client.get(path).status_code == 401
    assert client.get(path, headers={**headers, "X-Tenant-ID": "tenant-b"}).status_code == 403
    assert client.get(path, headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_static_lookup_and_conversion_routes_keep_precedence(probe):
    _, _, app = probe
    for path, name in [("/api/v1/artikel/mengeneinheiten/stamm/umrechnen", "umrechnen"), ("/api/v1/artikel/individuelle-nummern/lookup", "lookup_interne_nummer")]:
        matches = [route for route in app.routes if route.matches({"type": "http", "path": path, "method": "GET"})[0] == Match.FULL]
        assert matches[0].endpoint.__name__ == name
