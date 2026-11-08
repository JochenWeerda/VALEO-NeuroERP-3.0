"""CLI-Anlage — derselbe ``creation``-Vertrag wie die native Anlagemaske (UniversalNativeCreatePage)."""
from __future__ import annotations

import io
import json

import base64

import httpx
import pytest

from valeo_cli import cli, support

API = "https://api.invalid"
ISSUER = "https://idp.invalid/realms/fixture"


def jwt(**claims) -> str:
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")  # noqa: E731
    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


HUMAN = jwt(sub="u1", tenant_id="t1", identity_type="human", exp=4_000_000_000)
AGENT = jwt(sub="a1", tenant_id="t1", identity_type="service", exp=4_000_000_000)

CREATION = {
    "endpoint": "/api/v1/einkauf/lieferanten",
    "permission": "einkauf.lieferant.create",
    "detailRoute": "/einkauf/lieferanten/{entity_id}",
    "defaults": {"land": "Deutschland"},
    "fields": [
        {"key": "lieferantennummer", "type": "text", "required": True},
        {"key": "firmenname", "type": "text", "required": True},
        {"key": "zahlungsziel", "type": "number"},
        {"key": "angelegt_am", "type": "date", "readOnly": True},
        {"key": "land", "type": "text"},
    ],
}


@pytest.fixture(autouse=True)
def umgebung(tmp_path, monkeypatch):
    monkeypatch.setenv("VALEO_API_URL", API)
    monkeypatch.setenv("VALEO_OIDC_ISSUER", ISSUER)
    monkeypatch.setenv("VALEO_CLI_SESSION", str(tmp_path / "sitzung.json"))


class Server:
    def __init__(self, creation=CREATION, result=None):
        self.definition = {"id": "einkauf/supplier", "creation": creation} if creation is not None else {"id": "x"}
        self.result = result if result is not None else {"id": "L-7"}
        self.calls: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/screen-definition"):
            return httpx.Response(200, json=self.definition)
        self.calls.append(request)
        return httpx.Response(201, json=self.result)


def run(argv, server, monkeypatch, token=HUMAN):
    lines: list[str] = []
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", token)
    with httpx.Client(transport=httpx.MockTransport(server)) as http:
        code = cli.main(argv, http=http, out=lines.append, ask=lambda _: "", stdin=io.StringIO(""))
    return code, "\n".join(lines)


def test_legt_mit_vorgaben_und_typisierten_feldern_an(monkeypatch):
    server = Server()
    code, text = run(["anlegen", "einkauf/supplier", "--feld", "lieferantennummer=L-7", "--feld", "firmenname=Hof",
                      "--feld", "zahlungsziel=30"], server, monkeypatch)
    assert code == 0, text
    assert "Angelegt: L-7 (/einkauf/lieferanten/L-7)" in text
    (call,) = server.calls
    assert call.method == "POST" and call.url.path == "/api/v1/einkauf/lieferanten"
    assert json.loads(call.content) == {"land": "Deutschland", "lieferantennummer": "L-7", "firmenname": "Hof",
                                        "zahlungsziel": 30}


@pytest.mark.parametrize("argv, meldung", [
    (["--feld", "lieferantennummer=L-7"], "Pflichtfelder fehlen: firmenname"),
    (["--feld", "lieferantennummer=L-7", "--feld", "firmenname=Hof", "--feld", "angelegt_am=2026-01-01"],
     "Unbekannte Anlagefelder: angelegt_am"),
    (["--feld", "lieferantennummer=L-7", "--feld", "firmenname=Hof", "--feld", "tenant_id=fremd"],
     "Unbekannte Anlagefelder: tenant_id"),
])
def test_bedienfehler_senden_nichts(monkeypatch, argv, meldung):
    server = Server()
    code, text = run(["anlegen", "einkauf/supplier", *argv], server, monkeypatch)
    assert code == 2 and meldung in text
    assert server.calls == []


def test_agenten_legen_nicht_an(monkeypatch):
    server = Server()
    code, text = run(["anlegen", "einkauf/supplier", "--feld", "lieferantennummer=L-7", "--feld", "firmenname=Hof"],
                     server, monkeypatch, token=AGENT)
    assert code == 1 and "keine Agenten-Freigabe" in text
    assert server.calls == []


def test_ohne_creation_keine_anlage(monkeypatch):
    server = Server(creation=None)
    code, text = run(["anlegen", "einkauf/supplier"], server, monkeypatch)
    assert code == 2 and "keine Neuanlage freigegeben" in text and server.calls == []


def test_wiederholungsschluessel_wenn_verlangt(monkeypatch):
    server = Server(creation={**CREATION, "requiresIdempotencyKey": True})
    code, text = run(["anlegen", "einkauf/supplier", "--feld", "lieferantennummer=L-7", "--feld", "firmenname=Hof",
                      "--idempotenz", "k-1", "--json"], server, monkeypatch)
    assert code == 0, text
    assert json.loads(server.calls[0].content)["idempotency_key"] == "k-1"
    assert json.loads(text)["idempotenz"] == "k-1"


def test_antwort_ohne_id_ist_kein_erfolg(monkeypatch):
    server = Server(result={"ok": True})
    code, text = run(["anlegen", "einkauf/supplier", "--feld", "lieferantennummer=L-7", "--feld", "firmenname=Hof"],
                     server, monkeypatch)
    assert code == 1 and "keine Datensatz-ID" in text


@pytest.mark.parametrize("creation, meldung", [
    ({**CREATION, "adapter": "docflow.create.v1"}, "Adapter docflow.create.v1"),
    ({**CREATION, "endpoint": "https://fremd.invalid/x"}, "Ungueltiger Anlageweg"),
])
def test_adapter_und_fremde_wege_abgelehnt(creation, meldung):
    with pytest.raises(ValueError, match=meldung):
        support.creation_request({"creation": creation}, {}, idempotency_key=None, is_agent=False)
