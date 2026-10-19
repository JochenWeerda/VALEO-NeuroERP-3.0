"""MASK-CLI — die Kommandozeile ruft denselben Kommandoweg wie die Maske und behauptet nichts darueber hinaus."""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import httpx
import pytest

from valeo_cli import auth, cli, support

ROOT = Path(__file__).resolve().parents[1]
ISSUER = "https://idp.invalid/realms/fixture"
API = "https://api.invalid"


def jwt(**claims) -> str:
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")  # noqa: E731
    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


HUMAN = jwt(sub="u1", preferred_username="fixture-mensch", tenant_id="t1", identity_type="human", exp=4_000_000_000)
AGENT = jwt(sub="a1", tenant_id="t1", identity_type="service", exp=4_000_000_000)
UNTYPED = jwt(sub="u2", tenant_id="t1", exp=4_000_000_000)

ACTIONS = [
    {"key": "testen", "label": "Testmail senden", "commandEndpoint": "/api/v1/admin/postfaecher/{entity_id}/testen",
     "method": "POST", "inputFields": [{"key": "empfaenger", "type": "text"}]},
    {"key": "allocate", "label": "Kontingent vergeben", "commandEndpoint": "/api/v1/identity/budgets/actions/allocate",
     "method": "POST", "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
     "humanApprovalRequired": True,
     "inputFields": [{"key": "tokens", "type": "number", "required": True},
                     {"key": "kind", "type": "select", "required": True,
                      "options": [{"value": "user"}, {"value": "agent"}]}]},
    {"key": "regel", "label": "Regelversion", "commandEndpoint": "/api/v1/agrar/harvest/rules",
     "commandBinding": {"adapter": "harvest.control.v1", "command": "create_rule"}},
    {"key": "neu", "label": "Neu", "command": "admin.neu"},
]
DEFINITION = {"id": "admin/fixture", "title": "Fixture", "actions": ACTIONS[:2],
              "tables": [{"key": "t", "rowActions": ACTIONS[2:]}]}


@pytest.fixture(autouse=True)
def umgebung(tmp_path, monkeypatch):
    monkeypatch.setenv("VALEO_API_URL", API)
    monkeypatch.setenv("VALEO_OIDC_ISSUER", ISSUER)
    monkeypatch.setenv("VALEO_CLI_SESSION", str(tmp_path / "sitzung.json"))
    monkeypatch.delenv("VALEO_ACCESS_TOKEN", raising=False)


class Server:
    """Aufgezeichneter Backend-Fake: liefert die ScreenDefinition und protokolliert jeden Aktionsaufruf."""

    def __init__(self, result=None, status=200):
        self.calls: list[httpx.Request] = []
        self.result = result if result is not None else {"success": True, "summary": "erledigt"}
        self.status = status

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/screen-definition"):
            return httpx.Response(200, json=DEFINITION)
        self.calls.append(request)
        return httpx.Response(self.status, json=self.result if self.status < 400 else {"detail": "verboten"})


def run(argv, server, token=HUMAN, monkeypatch=None, answer=""):
    lines: list[str] = []
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", token)
    with httpx.Client(transport=httpx.MockTransport(server)) as http:
        code = cli.main(argv, http=http, out=lines.append, ask=lambda _: answer, stdin=io.StringIO(""))
    return code, "\n".join(lines)


# --------------------------------------------------------------------------------------------- Vertrag


def test_nur_der_generische_weg_der_maske_ist_unterstuetzt():
    by_key = {a["key"]: support.support(a) for a in ACTIONS}
    assert by_key["testen"].supported and by_key["allocate"].supported
    assert by_key["regel"].reason == "adapter:harvest.control.v1"
    assert support.support({"key": "b", "commandEndpoint": "/api/v1/docflow/{entity_id}/post",
                            "commandBinding": {"adapter": "docflow.v1", "command": "post"}}).supported
    assert by_key["neu"].reason == "kein_endpunkt"
    assert support.support({"key": "x", "commandEndpoint": "/api/v1/docflow/{entity_id}/x"}).reason == "docflow_ohne_adapter"
    assert support.support({"key": "x", "commandEndpoint": "/api/v1/a", "inputFlow": {"kind": "humanForm"}}).reason \
        == "eingabe_in_maske"
    assert support.support({"key": "x", "commandEndpoint": "/api/v1/a/{approval_id}"}).reason \
        == "pfadparameter:{approval_id}"


def test_request_wie_useActionRuntime():
    method, path, body = support.build_request(
        ACTIONS[0], screen_id="admin/fixture", entity_id="a/b c", payload={"empfaenger": "x@invalid"},
        mode="dryRun", audit_reason="Pruefung", idempotency_key="k1")
    assert (method, path) == ("POST", "/api/v1/admin/postfaecher/a%2Fb%20c/testen")
    assert body == {"empfaenger": "x@invalid", "_mode": "dryRun", "_auditReason": "Pruefung", "_idempotencyKey": "k1"}
    _, _, body = support.build_request(ACTIONS[0], screen_id="s", entity_id="1", payload={}, mode="execute",
                                       audit_reason=None, idempotency_key=None)
    assert body == {}, "execute ohne Umschlagfelder, wie die Maske"


def test_kontingent_nur_mit_den_feldern_des_strengen_kommandos():
    _, _, body = support.build_request(ACTIONS[1], screen_id="s", entity_id=None,
                                       payload={"tokens": 5, "kind": "user", "tenant_id": "fremd", "x": 1},
                                       mode="execute", audit_reason="r", idempotency_key=None)
    assert body == {"tokens": 5, "kind": "user", "_auditReason": "r"}


def test_objektkennung_ist_pflicht_wenn_der_pfad_sie_braucht():
    with pytest.raises(ValueError, match="--id"):
        support.build_request(ACTIONS[0], screen_id="s", entity_id=None, payload={}, mode="execute",
                              audit_reason=None, idempotency_key=None)


def test_felder_werden_typgerecht_und_mit_auswahl_geprueft():
    assert support.coerce_fields(ACTIONS[1], {"tokens": "12", "kind": "agent"}) == {"tokens": 12, "kind": "agent"}
    with pytest.raises(ValueError, match="Zahl"):
        support.coerce_fields(ACTIONS[1], {"tokens": "viele"})
    with pytest.raises(ValueError, match="erlaubt"):
        support.coerce_fields(ACTIONS[1], {"kind": "gott"})


# --------------------------------------------------------------------------------------------- Ausfuehren


def test_ausfuehren_sendet_genau_den_maskenaufruf(monkeypatch):
    server = Server()
    code, out = run(["ausfuehren", "admin/fixture", "testen", "--id", "7", "--feld", "empfaenger=x@invalid"],
                    server, monkeypatch=monkeypatch)
    assert code == 0 and "OK: erledigt" in out
    [call] = server.calls
    assert call.url.path == "/api/v1/admin/postfaecher/7/testen"
    assert call.headers["Authorization"] == f"Bearer {HUMAN}"
    assert json.loads(call.content) == {"empfaenger": "x@invalid"}
    assert "X-Tenant-ID" not in call.headers, "Mandant kommt allein aus dem Token"


def test_bestaetigung_ohne_zustimmung_fuehrt_nichts_aus(monkeypatch):
    server = Server()
    argv = ["ausfuehren", "admin/fixture", "allocate", "--feld", "tokens=1", "--feld", "kind=user", "--grund", "r"]
    code, out = run(argv, server, monkeypatch=monkeypatch, answer="nein")
    assert code == 1 and not server.calls and "nichts ausgefuehrt" in out
    code, _ = run(argv, server, monkeypatch=monkeypatch, answer="ja")
    assert code == 0 and len(server.calls) == 1
    code, _ = run(argv + ["--ja"], server, monkeypatch=monkeypatch)
    assert code == 0 and len(server.calls) == 2


def test_rueckfrage_ohne_antwort_gilt_als_nein(monkeypatch):
    """Git Bash meldet ein Terminal, liefert aber EOF — das darf weder abstuerzen noch ausfuehren."""
    class Terminal(io.StringIO):
        def isatty(self):
            return True

    def eof(_prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", HUMAN)
    server, lines = Server(), []
    with httpx.Client(transport=httpx.MockTransport(server)) as http:
        code = cli.main(["ausfuehren", "admin/fixture", "allocate", "--feld", "tokens=1", "--feld", "kind=user",
                         "--grund", "r"], http=http, out=lines.append, stdin=Terminal(""))
    assert code == 1 and not server.calls


def test_begruendung_und_pflichtfelder_vor_dem_aufruf(monkeypatch):
    server = Server()
    code, out = run(["ausfuehren", "admin/fixture", "allocate", "--feld", "tokens=1", "--feld", "kind=user", "--ja"],
                    server, monkeypatch=monkeypatch)
    assert code == 2 and "Begruendung" in out and not server.calls
    code, out = run(["ausfuehren", "admin/fixture", "allocate", "--grund", "r", "--ja"], server, monkeypatch=monkeypatch)
    assert code == 2 and "tokens" in out and not server.calls


@pytest.mark.parametrize("token", [AGENT, UNTYPED])
def test_agent_und_unbekannte_identitaet_sind_gesperrt(monkeypatch, token):
    server = Server()
    code, out = run(["ausfuehren", "admin/fixture", "allocate", "--feld", "tokens=1", "--feld", "kind=user",
                     "--grund", "r", "--ja"], server, token=token, monkeypatch=monkeypatch)
    assert code == 1 and "Agent" in out and not server.calls


def test_adapteraktion_wird_mit_grund_abgewiesen(monkeypatch):
    server = Server()
    code, out = run(["ausfuehren", "admin/fixture", "regel", "--ja"], server, monkeypatch=monkeypatch)
    assert code == 1 and "harvest.control.v1" in out and not server.calls


def test_fachliche_ablehnung_und_serververweigerung(monkeypatch):
    code, out = run(["ausfuehren", "admin/fixture", "testen", "--id", "1"],
                    Server(result={"success": False, "error": "Postfach gesperrt"}), monkeypatch=monkeypatch)
    assert code == 1 and "ABGELEHNT: Postfach gesperrt" in out
    code, out = run(["ausfuehren", "admin/fixture", "testen", "--id", "1"], Server(status=403), monkeypatch=monkeypatch)
    assert code == 3 and "verboten" in out


def test_aktionen_listet_zugang_und_grund(monkeypatch):
    code, out = run(["aktionen", "admin/fixture"], Server(), monkeypatch=monkeypatch)
    assert code == 0
    assert "testen" in out and "CLI" in out and "harvest.control.v1" in out and "keinen Kommando-Endpunkt" in out


# --------------------------------------------------------------------------------------------- Anmeldung


class Idp:
    def __init__(self, token_responses, refresh=None):
        self.token_responses = list(token_responses)
        self.refresh = refresh
        self.requests: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json={"device_authorization_endpoint": f"{ISSUER}/device",
                                             "token_endpoint": f"{ISSUER}/token",
                                             "end_session_endpoint": f"{ISSUER}/logout"})
        form = dict(httpx.QueryParams(request.content.decode()))
        self.requests.append({"path": request.url.path, **form})
        if request.url.path.endswith("/device"):
            return httpx.Response(200, json={"device_code": "dc", "user_code": "ABCD-EFGH", "interval": 1,
                                             "expires_in": 60, "verification_uri": f"{ISSUER}/device"})
        if request.url.path.endswith("/logout"):
            return httpx.Response(204)
        if form.get("grant_type") == "refresh_token":
            return self.refresh
        return self.token_responses.pop(0)


def test_device_flow_wartet_bremst_und_speichert_nur_fuer_den_eigentuemer(tmp_path):
    idp = Idp([httpx.Response(400, json={"error": "authorization_pending"}),
               httpx.Response(400, json={"error": "slow_down"}),
               httpx.Response(200, json={"access_token": HUMAN, "refresh_token": "r1", "expires_in": 300})])
    waits: list[float] = []
    settings = auth.Settings.from_env()
    with httpx.Client(transport=httpx.MockTransport(idp)) as http:
        session = auth.login(http, settings, announce=lambda _: None, open_browser=False,
                             sleep=waits.append, clock=lambda: 1000.0)
    assert session["access_token"] == HUMAN and waits == [1, 1, 6]
    assert all(r.get("client_id") == "valeo-neuro-erp-cli" for r in idp.requests)
    assert not any("password" in r for r in idp.requests), "die CLI fasst nie ein Passwort an"
    device = next(r for r in idp.requests if r["path"].endswith("/device"))
    assert device["code_challenge_method"] == "S256"
    verifier = idp.requests[-1]["code_verifier"]
    import hashlib
    assert device["code_challenge"] == base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    stored = json.loads(settings.session_file.read_text(encoding="utf-8"))
    assert stored["refresh_token"] == "r1" and stored["issuer"] == ISSUER


def test_abgelehnte_anmeldung_speichert_nichts():
    settings = auth.Settings.from_env()
    idp = Idp([httpx.Response(400, json={"error": "access_denied"})])
    with httpx.Client(transport=httpx.MockTransport(idp)) as http, pytest.raises(auth.AuthError, match="abgelehnt"):
        auth.login(http, settings, announce=lambda _: None, open_browser=False, sleep=lambda _: None)
    assert not settings.session_file.exists()


def _session(settings, **values):
    settings.session_file.parent.mkdir(parents=True, exist_ok=True)
    settings.session_file.write_text(json.dumps({"issuer": ISSUER, "client_id": settings.client_id,
                                                 "access_token": "alt", "refresh_token": "r1",
                                                 "expires_at": 1000.0, **values}), encoding="utf-8")


def test_erneuerung_schreibt_das_rotierte_refresh_token_sofort_zurueck():
    settings = auth.Settings.from_env()
    _session(settings)
    idp = Idp([], refresh=httpx.Response(200, json={"access_token": "neu", "refresh_token": "r2", "expires_in": 300}))
    with httpx.Client(transport=httpx.MockTransport(idp)) as http:
        assert auth.access_token(http, settings, clock=lambda: 2000.0) == "neu"
    assert json.loads(settings.session_file.read_text(encoding="utf-8"))["refresh_token"] == "r2"
    assert idp.requests[-1]["refresh_token"] == "r1"


def test_widerrufene_sitzung_wird_geloescht():
    settings = auth.Settings.from_env()
    _session(settings)
    idp = Idp([], refresh=httpx.Response(400, json={"error": "invalid_grant"}))
    with httpx.Client(transport=httpx.MockTransport(idp)) as http, pytest.raises(auth.AuthError, match="erneut"):
        auth.access_token(http, settings, clock=lambda: 2000.0)
    assert not settings.session_file.exists()


def test_sitzung_eines_anderen_providers_wird_nie_benutzt():
    settings = auth.Settings.from_env()
    _session(settings, issuer="https://fremd.invalid/realms/x", expires_at=9e12)
    with httpx.Client(transport=httpx.MockTransport(Idp([]))) as http, pytest.raises(auth.AuthError, match="Nicht"):
        auth.access_token(http, settings)


def test_abmelden_beendet_die_sitzung_beim_provider():
    settings = auth.Settings.from_env()
    _session(settings, expires_at=9e12)
    idp = Idp([])
    with httpx.Client(transport=httpx.MockTransport(idp)) as http:
        assert auth.logout(http, settings) is True
    assert idp.requests[-1]["path"].endswith("/logout") and idp.requests[-1]["refresh_token"] == "r1"
    assert not settings.session_file.exists()


# --------------------------------------------------------------------------------------------- Register / Realm


def test_cli_register_ist_aktuell():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts/generate_cli_mask_commands.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    assert gen.main(["--check"]) == 0, "python scripts/generate_cli_mask_commands.py ausfuehren"


def test_cli_client_nur_device_grant_mit_erp_audience_und_belegscopes():
    from scripts.provision_identity_provider import prepared_realm
    realm = prepared_realm(json.loads((ROOT / "config/keycloak/realm-export.json").read_text(encoding="utf-8")))
    client = next(c for c in realm["clients"] if c["clientId"] == "valeo-neuro-erp-cli")
    assert client["publicClient"] and not client["standardFlowEnabled"] and not client["directAccessGrantsEnabled"]
    assert not client.get("serviceAccountsEnabled") and client["redirectUris"] == []
    assert client["attributes"]["oauth2.device.authorization.grant.enabled"] == "true"
    audience = next(m for m in client["protocolMappers"] if m["name"] == "erp-api-audience")
    assert audience["config"]["included.client.audience"] == "valeo-neuro-erp-backend"
    assert {"roles", "belege:read", "belege:write"} <= set(client["defaultClientScopes"])


def test_provisionierung_legt_nur_den_fehlenden_cli_client_an():
    from scripts.provision_identity_provider import create_declared_client
    created = []
    transport = httpx.MockTransport(lambda r: (created.append(json.loads(r.content)), httpx.Response(201))[1])
    with httpx.Client(base_url="https://idp.invalid", transport=transport) as client:
        create_declared_client(client, {}, "fixture", {
            "clientId": "valeo-neuro-erp-cli", "publicClient": True, "redirectUris": [],
            "attributes": {"oauth2.device.authorization.grant.enabled": "true"}, "defaultClientScopes": ["roles"]})
        with pytest.raises(RuntimeError, match="device-grant-only"):
            create_declared_client(client, {}, "fixture", {
                "clientId": "valeo-neuro-erp-cli", "publicClient": True, "standardFlowEnabled": True,
                "attributes": {"oauth2.device.authorization.grant.enabled": "true"}})
    assert len(created) == 1 and "defaultClientScopes" not in created[0]
