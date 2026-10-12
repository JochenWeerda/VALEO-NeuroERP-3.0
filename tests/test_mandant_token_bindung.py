"""Mandatory provider tenant binding replaces the permissive transition contract."""
import pytest
from test_system_tenant_binding import keys, probe


@pytest.mark.parametrize('claim', ['tenant_id', 'mandanten_id'])
def test_provider_mandant_wird_verbindlich_gebunden(probe, claim):
    token = probe.token(changes={claim: 'tenant-a'}, omit=() if claim == 'tenant_id' else ('tenant_id',))
    headers = {'Authorization': 'Bearer ' + token}
    assert probe.client.get('/api/probe', headers=headers).status_code == 200
    assert probe.client.get('/api/probe', headers={**headers, 'X-Tenant-ID': 'tenant-b'}).status_code == 403


@pytest.mark.parametrize('required', [False, True])
@pytest.mark.parametrize('claims', [{}, {'tenant_id': ''}, {'tenant_id': None}, {'tenant_id': 7}, {'tenant_id': ['tenant-a']}])
def test_keine_missing_claim_ausnahme(probe, monkeypatch, required, claims):
    from app.core.config import settings
    monkeypatch.setattr(settings, 'OIDC_TENANT_CLAIM_REQUIRED', required)
    token = probe.token(changes=claims, omit=('tenant_id',) if not claims else ())
    assert probe.client.get('/api/probe', headers={'Authorization': 'Bearer ' + token}).status_code == 403
    assert probe.calls == []


def test_dev_token_erteilt_keine_rechte(probe):
    response = probe.client.get('/api/probe', headers={'Authorization': 'Bearer opaque-own-dev-token', 'X-Tenant-ID': 'tenant-a'})
    assert response.status_code == 401
    assert probe.calls == []


def test_mandant_kommt_ohne_kopf_aus_der_anmeldung(probe):
    result = probe.client.get('/api/probe', headers=probe.headers('tenant-b'))
    assert result.status_code == 200
    assert result.json()['tenant'] == 'tenant-b'


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
