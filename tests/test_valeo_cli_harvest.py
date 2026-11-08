"""Ernte-Steuerungsadapter der CLI — dieselben Faelle wie harvest-control-command-adapter.test.ts der Maske."""
from __future__ import annotations

import base64
import io
import json

import httpx
import pytest

from valeo_cli import cli, harvest

CONFIRMED = {"approve_rule", "revoke_rule", "approve_calculation", "release"}


def action(command: str) -> dict:
    return {"key": command, "label": command, "method": "POST", "permission": command,
            "commandEndpoint": harvest.PATHS[command], "forbiddenForAgents": True,
            "requiresConfirmation": command in CONFIRMED,
            "commandBinding": {"adapter": "harvest.control.v1", "command": command, "preview": False}}


CONTEXT = {"context_hash": "a" * 64, "calculation_hash": "b" * 64, "protocol_hash": "c" * 64,
           "state": {"acceptance": {"id": "acceptance"}, "protocol": {"id": "protocol"}}}
RULE = {"id": "rule-version", "content_hash": "d" * 64, "definition": {"rule_id": "terms", "rule_version": 2}}


def prepare(command, payload=None, *, mode="execute", entity="acceptance", is_agent=False, act=None, reason=None):
    return harvest.prepare(act or action(command), selected_rule=RULE, context=CONTEXT, entity_id=entity,
                           payload={"acceptance_id": "acceptance", **(payload or {})}, mode=mode, audit_reason=reason,
                           idempotency_key="stable-key", is_agent=is_agent)


def test_nur_der_exakte_kommandokoerper_mit_gebundenem_eingabestand():
    url, body = prepare("calculate", {"tenant_id": "foreign", "actor": "spoofed", "impurities_free_pct": 2})
    assert url == "/api/v1/agrar/harvest-acceptance/acceptance/calculate"
    assert body == {"idempotency_key": "stable-key", "expected_context_hash": "a" * 64}


@pytest.mark.parametrize("mode", ["dryRun", "validate", "propose"])
def test_keine_aenderung_ueber_vorschaumodi(mode):
    with pytest.raises(ValueError, match="menschliche"):
        prepare("calculate", mode=mode)


def test_agent_fremde_annahme_und_falscher_endpunkt():
    with pytest.raises(ValueError, match="menschliche"):
        prepare("calculate", is_agent=True)
    with pytest.raises(ValueError, match="Annahme"):
        prepare("calculate", entity="other")
    with pytest.raises(ValueError, match="Endpunkt"):
        prepare("calculate", act={**action("calculate"), "commandEndpoint": "/evil"})


def test_finanzkommando_braucht_bestaetigung_und_berechnungshash():
    with pytest.raises(ValueError, match="bestaetigt"):
        prepare("release")
    _, body = prepare("release", {"confirm_execution": "confirm"})
    assert body == {"idempotency_key": "stable-key", "expected_calculation_hash": "b" * 64}


def test_regel_mit_explizitem_nullfreibetrag_ohne_aufruferidentitaet():
    _, body = prepare("create_rule", {"rule_id": "terms", "customer_id": "customer", "article_id": "article",
                                      "valid_from": "2026-01-01", "valid_until": "2026-12-31",
                                      "source_reference": "synthetic agreement", "measurement_method": "lab",
                                      "measurement_method_version": "1", "impurities_free_pct": 0,
                                      "quality_limit_pct": 2, "actor": "forged", "tenant_id": "foreign"})
    assert body["expected_version"] == 2
    assert body["terms"]["impurities_free_pct"] == "0" and body["terms"]["quality_limit_pct"] == 2
    assert body["terms"]["contract_id"] is None and "actor" not in body and "tenant_id" not in body


def test_regelgenehmigung_bindet_hash_grund_und_frist():
    url, body = prepare("approve_rule", {"confirm_execution": "confirm", "expires_at": "2026-12-31T12:00:00Z"},
                        reason="Vertrag geprueft")
    assert url.endswith("/rules/rule-version/approve")
    assert body == {"idempotency_key": "stable-key", "expected_hash": "d" * 64, "reason": "Vertrag geprueft",
                    "expires_at": "2026-12-31T12:00:00Z"}
    with pytest.raises(ValueError, match="Genehmigungsfrist ist ungueltig"):
        prepare("approve_rule", {"confirm_execution": "confirm", "expires_at": "morgen"}, reason="x y z")


def test_messnachweis_bindet_protokoll():
    _, body = prepare("attest", {"measurement_method": "lab", "measurement_method_version": "1",
                                 "measurement_source": "Bericht 7"})
    assert body["protocol_id"] == "protocol" and body["expected_protocol_hash"] == "c" * 64


def test_antwort_ohne_nachweis_ist_kein_erfolg():
    assert not harvest.result({"calculation_hash": "x"})["success"]
    assert harvest.result({"control_event_id": "receipt"})["success"]


def test_regelfassung_nur_aus_der_regelliste():
    assert harvest.find_rule({"items": [RULE]}, "rule-version") == RULE
    with pytest.raises(ValueError, match="Regelliste"):
        harvest.find_rule([{"id": "rule-version"}], "rule-version")


# --------------------------------------------------------------------------------------------- Ende zu Ende


def _jwt(**claims) -> str:
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")  # noqa: E731
    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


class Server:
    def __init__(self, allowed=("calculate", "release"), fail_first=False):
        self.allowed, self.fail_first, self.posts = list(allowed), fail_first, []

    def __call__(self, request):
        path = request.url.path
        if path.endswith("/screen-definition"):
            return httpx.Response(200, json={"id": "agrar/harvest-controls",
                                             "actions": [action("calculate"), action("release")]})
        if path.endswith("/permissions"):
            return httpx.Response(200, json={"allowed_actions": self.allowed})
        if path.endswith("/context"):
            return httpx.Response(200, json=CONTEXT)
        self.posts.append(json.loads(request.content))
        if self.fail_first and len(self.posts) == 1:
            return httpx.Response(502, json={"detail": "Gateway"})
        return httpx.Response(200, json={"control_event_id": "receipt"})


def run(argv, server, tmp_path, monkeypatch, answer=""):
    monkeypatch.setenv("VALEO_API_URL", "https://api.invalid")
    monkeypatch.setenv("VALEO_CLI_SESSION", str(tmp_path / "s.json"))
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", _jwt(sub="u", tenant_id="t", identity_type="human", exp=4_000_000_000))
    lines = []
    with httpx.Client(transport=httpx.MockTransport(server)) as http:
        code = cli.main(argv, http=http, out=lines.append, ask=lambda _: answer, stdin=io.StringIO(""))
    return code, "\n".join(lines)


def test_cli_berechnet_mit_geladenem_kontrollstand(tmp_path, monkeypatch):
    server = Server()
    code, out = run(["ausfuehren", "agrar/harvest-controls", "calculate", "--id", "acceptance"], server, tmp_path, monkeypatch)
    assert code == 0 and "unveraenderlichem Nachweis" in out
    assert server.posts[0]["expected_context_hash"] == "a" * 64


def test_interaktive_bestaetigung_gilt_als_confirm_execution(tmp_path, monkeypatch):
    server = Server()
    code, _ = run(["ausfuehren", "agrar/harvest-controls", "release", "--id", "acceptance"], server, tmp_path,
                  monkeypatch, answer="ja")
    assert code == 0 and server.posts[0]["expected_calculation_hash"] == "b" * 64


def test_ohne_berechtigung_kein_transport(tmp_path, monkeypatch):
    server = Server(allowed=[])
    code, _ = run(["ausfuehren", "agrar/harvest-controls", "calculate", "--id", "acceptance"], server, tmp_path, monkeypatch)
    assert code == 3 and not server.posts


def test_unsicherer_ausgang_nennt_den_schluessel_fuer_die_wiederholung(tmp_path, monkeypatch):
    server = Server(fail_first=True)
    code, out = run(["ausfuehren", "agrar/harvest-controls", "calculate", "--id", "acceptance"], server, tmp_path, monkeypatch)
    assert code == 4
    key = out.split("--idempotenz ")[1].split()[0]
    code, _ = run(["ausfuehren", "agrar/harvest-controls", "calculate", "--id", "acceptance", "--idempotenz", key],
                  server, tmp_path, monkeypatch)
    assert code == 0 and server.posts[0] == server.posts[1], "Wiederholung ist derselbe Auftrag"
