"""Der Mandant der Anfrage ist der Mandant der Anmeldung.

Bis zum 12.10.2026 pruefte die Middleware ``X-Tenant-ID`` nur auf seine Form: Wer angemeldet war,
konnte jeden Mandanten in den Kopf schreiben, und 326 Dateien bezogen den Mandanten von dort.

Gebunden wird an einer Stelle — ``require_bearer_token``, das an jedem API-Weg haengt. Geprueft
wird hier mit der echten Mandanten-Middleware davor; nur die Signaturpruefung ist ersetzt.
"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from app.core import security
from app.core.config import settings
from app.middleware.tenant_enforcement import TenantEnforcementMiddleware

HAUS_A = "haus-a"
HAUS_B = "haus-b"


@pytest.fixture
def anfrage(monkeypatch):
    """Ruft einen geschuetzten Weg mit einem Token, dessen Claims der Test bestimmt."""
    monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
    monkeypatch.setattr(settings, "OIDC_TENANT_CLAIM_REQUIRED", False)
    claims: dict = {}
    monkeypatch.setattr(security, "_validate_jwt", lambda _token: dict(claims))

    app = FastAPI()
    app.add_middleware(TenantEnforcementMiddleware)

    @app.get("/api/v1/probe", dependencies=[Depends(security.require_bearer_token)])
    def probe(request: Request):
        return {"mandant": request.state.tenant_id, "claims": request.state.token_claims}

    client = TestClient(app)

    def rufe(token_claims: dict, kopf: str | None = HAUS_A, *, ueber_query: bool = False, token: str = "jwt"):
        claims.clear()
        claims.update({"sub": "5f0c2a9e", **token_claims})
        headers = {} if kopf is None else {"X-Tenant-ID": kopf}
        if ueber_query:
            return client.get("/api/v1/probe", params={"token": token}, headers=headers)
        return client.get("/api/v1/probe", headers={**headers, "Authorization": f"Bearer {token}"})

    return rufe


def test_eigener_mandant_geht_durch(anfrage):
    antwort = anfrage({"tenant_id": HAUS_A})
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["mandant"] == HAUS_A


@pytest.mark.parametrize("claims", [
    {"tenant_id": HAUS_A},
    {"mandanten_id": HAUS_A},
    {"tenant_id": [HAUS_A]},  # Keycloak liefert ein Attribut je nach Mapper als Liste
    {"tenant_id": f"  {HAUS_A} "},
])
def test_fremder_mandant_im_kopf_wird_abgelehnt(anfrage, claims):
    antwort = anfrage(claims, kopf=HAUS_B)
    assert antwort.status_code == 403, antwort.text
    assert "Mandant der Anmeldung" in antwort.json()["detail"]


def test_token_ueber_query_wird_genauso_gebunden(anfrage):
    """SSE und WebSocket schicken das Token als Query-Parameter — kein zweiter, ungebundener Weg."""
    assert anfrage({"tenant_id": HAUS_A}, kopf=HAUS_B, ueber_query=True).status_code == 403
    assert anfrage({"tenant_id": HAUS_A}, kopf=HAUS_A, ueber_query=True).status_code == 200


@pytest.mark.parametrize("claims", [
    {"tenant_id": HAUS_A, "mandanten_id": HAUS_B},
    {"tenant_id": [HAUS_A, HAUS_B]},
])
def test_mehrdeutiges_token_wird_abgelehnt(anfrage, claims):
    for kopf in (HAUS_A, HAUS_B):
        antwort = anfrage(claims, kopf=kopf)
        assert antwort.status_code == 403, antwort.text
        assert "mehr als einen Mandanten" in antwort.json()["detail"]


@pytest.mark.parametrize("claims", [{}, {"tenant_id": ""}, {"tenant_id": None}, {"tenant_id": 7}])
def test_token_ohne_mandant_laeuft_bis_der_schalter_gesetzt_ist(anfrage, monkeypatch, claims):
    """Die Umstellung sperrt niemanden aus: Erst wenn jeder Benutzer das Attribut hat, wird es Pflicht."""
    assert anfrage(claims).status_code == 200
    monkeypatch.setattr(settings, "OIDC_TENANT_CLAIM_REQUIRED", True)
    antwort = anfrage(claims)
    assert antwort.status_code == 403, antwort.text
    assert "keinen Mandanten" in antwort.json()["detail"]


def test_schalter_aendert_nichts_fuer_gebundene_tokens(anfrage, monkeypatch):
    monkeypatch.setattr(settings, "OIDC_TENANT_CLAIM_REQUIRED", True)
    assert anfrage({"tenant_id": HAUS_A}).status_code == 200
    assert anfrage({"tenant_id": HAUS_A}, kopf=HAUS_B).status_code == 403


def test_entwicklung_ohne_kopf_bindet_an_den_vorgabemandanten(anfrage, monkeypatch):
    """Ohne Kopf setzt die Middleware in der Entwicklung den Vorgabemandanten — auch der wird gebunden."""
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
    assert anfrage({"tenant_id": HAUS_A}, kopf=None).status_code == 403
    assert anfrage({"tenant_id": settings.DEFAULT_TENANT_ID}, kopf=None).status_code == 200


def test_dev_token_bleibt_ungebunden(anfrage, monkeypatch):
    """Der Dev-Token traegt keine Claims; in Produktion ist er nicht gesetzt (Startup-Guard)."""
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(settings, "OIDC_TENANT_CLAIM_REQUIRED", True)
    assert anfrage({"tenant_id": HAUS_A}, kopf=HAUS_B, token="dev-token").status_code == 200
    # Ein echtes Token wird auch in der Entwicklung gebunden.
    assert anfrage({"tenant_id": HAUS_A}, kopf=HAUS_B).status_code == 403


def test_realm_dateien_geben_den_mandanten_ins_token():
    """Der Anmeldedienst muss den Claim liefern — sonst bindet die Pruefung nichts."""
    import json
    import pathlib

    wurzel = pathlib.Path(__file__).resolve().parent.parent / "config" / "keycloak"
    for datei in ("realm-export.json", "realm-staging.json"):
        realm = json.loads((wurzel / datei).read_text(encoding="utf-8"))
        scopes = {s["name"]: s.get("protocolMappers", []) for s in realm.get("clientScopes", [])}
        for client in realm["clients"]:
            mapper = list(client.get("protocolMappers", []))
            for scope in client.get("defaultClientScopes", []):
                mapper += scopes.get(scope, [])
            treffer = [m for m in mapper if m.get("config", {}).get("claim.name") == "tenant_id"]
            assert treffer, f"{datei}: Client {client['clientId']} gibt tenant_id nicht ins Token"
            assert treffer[0]["config"]["access.token.claim"] == "true"
            assert treffer[0]["config"]["user.attribute"] == "tenant_id"
