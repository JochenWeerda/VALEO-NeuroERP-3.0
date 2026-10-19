"""DocFlow-Adapter der CLI — dieselben Faelle wie docflow-command-adapter.test.ts der Maske."""
from __future__ import annotations

import base64
import io
import json

import httpx
import pytest

from valeo_cli import cli, docflow


def action(command: str, **defaults) -> dict:
    suffix = {"approval_request": "/approvals", "approval_decide": "/approvals/{approval_id}/decision",
              "update": ""}.get(command, f"/{command}")
    default = defaults or ({"target_doc_type": "purchase_invoice"} if command == "convert"
                           else {"action": "post"} if command == "approval_request" else {"granted": True, "action": "post"})
    return {"key": command, "label": command, "enabledWhen": "allowed", "method": "PUT" if command == "update" else "POST",
            "commandEndpoint": f"/api/v1/docflow/{{entity_id}}{suffix}",
            "commandBinding": {"adapter": "docflow.v1", "command": command, "preview": command == "convert",
                               "defaults": default}}


def data(command: str, **extra) -> dict:
    return {"version": 7, "allowed": True, "aktionen": [{"key": command, "erlaubt": True, "approval_id": "approval-1"}], **extra}


def prepare(command, *, payload=None, mode="execute", reason=None, version=None, entity="doc-1", is_agent=False, **kw):
    return docflow.prepare(kw.get("act") or action(command), entity_id=entity, data=kw.get("data") or data(command),
                           payload=payload or {}, mode=mode, audit_reason=reason, idempotency_key="stable-intent-key",
                           expected_version=version, is_agent=is_agent)


@pytest.mark.parametrize("command", ["post", "release", "reverse", "convert"])
def test_kanonische_felder_und_ergebnis(command):
    method, url, body = prepare(command, reason="Fehlerkorrektur" if command == "reverse" else None)
    assert method == "POST" and url == f"/api/v1/docflow/doc-1/{command}"
    assert body["idempotency_key"] == "stable-intent-key" and body["expected_version"] == 7
    assert "_mode" not in body and "posted_by" not in body
    if command == "reverse":
        assert body["reason"] == "Fehlerkorrektur"
    if command == "convert":
        assert body["target_doc_type"] == "purchase_invoice" and body["dry_run"] is False
    assert docflow.result(action(command), entity_id="doc-1", data=data(command), mode="execute",
                          response={"command": command, "status": "ok", "source_doc_id": "doc-1"},
                          expected_version=None)["success"]


def test_umwandeln_als_trockenlauf_mit_sichtbarem_vorschlag():
    _, _, body = prepare("convert", mode="dryRun")
    assert body["dry_run"] is True
    res = docflow.result(action("convert"), entity_id="doc-1", data=data("convert"), mode="dryRun",
                         response={"command": "convert", "status": "dry_run", "source_doc_id": "doc-1",
                                   "payload": {"item_count": 2}}, expected_version=None)
    assert res["success"] and "Positionen 2" in res["summary"]


@pytest.mark.parametrize("command", ["post", "release", "reverse", "approval_request", "approval_decide"])
def test_keine_erfundene_vorschau(command):
    with pytest.raises(ValueError, match="schreibfreie Vorschau"):
        prepare(command, mode="dryRun", reason="Fehlerkorrektur")


@pytest.mark.parametrize("change", [{"payload": {"posted_by": "x"}}, {"payload": {"idempotency_key": "override"}},
                                    {"payload": {"target_doc_type": "sales_invoice"}}, {"version": 6}, {"entity": None}])
def test_gefaelschte_oder_veraltete_eingaben(change):
    with pytest.raises(ValueError):
        prepare("post", **change)


def test_serveraktion_und_version_sind_pflicht():
    with pytest.raises(ValueError, match="gesperrt"):
        prepare("post", data={"version": 7, "allowed": True})
    with pytest.raises(ValueError, match="gesperrt"):
        prepare("post", data={**data("post"), "allowed": False})
    with pytest.raises(ValueError, match="version fehlt"):
        prepare("post", data={**data("post"), "version": None})


def test_falscher_endpunkt_oder_adapter():
    with pytest.raises(ValueError, match="Endpoint"):
        prepare("post", act={**action("post"), "commandEndpoint": "/api/v1/pay"})
    with pytest.raises(ValueError, match="Adapter"):
        prepare("post", act={**action("post"), "commandBinding": None})


def test_freigabe_an_serverkennung_und_konkrete_entscheidung():
    assert prepare("approval_decide") == ("POST", "/api/v1/docflow/doc-1/approvals/approval-1/decision", {"granted": True})
    declined = action("approval_decide", granted=False, action="post")
    assert prepare("approval_decide", act=declined) [2] == {"granted": False}
    ok = {"id": "approval-1", "action": "post", "status": "granted"}
    res = lambda a, r: docflow.result(a, entity_id="doc-1", data=data("approval_decide"), mode="execute",  # noqa: E731
                                      response=r, expected_version=None)["success"]
    assert res(action("approval_decide"), ok) and not res(action("approval_decide"), {**ok, "id": "other"})
    assert not res(action("approval_decide"), {**ok, "action": "reverse"})
    assert res(declined, {**ok, "status": "denied"})


def test_freigabeanfrage_nur_fuer_die_deklarierte_aktion():
    assert prepare("approval_request")[2] == {"action": "post"}
    with pytest.raises(ValueError, match="Unzulaessige"):
        prepare("approval_request", payload={"action": "reverse"})


def test_keine_schreibenden_agentenaufrufe():
    with pytest.raises(ValueError, match="nicht freigeschaltet"):
        prepare("post", is_agent=True)


def test_unpassende_erfolgsantworten_sind_kein_erfolg():
    for response in ({"success": True}, {"command": "reverse", "status": "ok", "source_doc_id": "doc-1"},
                     {"command": "post", "status": "ok", "source_doc_id": "other"}):
        assert not docflow.result(action("post"), entity_id="doc-1", data=data("post"), mode="execute",
                                  response=response, expected_version=None)["success"]


def test_bearbeiten_erwartet_naechste_version_und_entwurf():
    _, _, body = prepare("update", payload={"currency": "EUR", "document_date": "2026-10-19", "items": []})
    assert body["expected_version"] == 7
    ok = {"id": "doc-1", "status": "draft", "version": 8, "items": []}
    assert docflow.result(action("update"), entity_id="doc-1", data=data("update"), mode="execute",
                          response=ok, expected_version=None)["success"]
    assert not docflow.result(action("update"), entity_id="doc-1", data=data("update"), mode="execute",
                              response={**ok, "version": 9}, expected_version=None)["success"]


def test_stornogrund_ist_pflicht():
    with pytest.raises(ValueError, match="Stornogrund"):
        prepare("reverse")
    with pytest.raises(ValueError, match="Stornogrund"):
        prepare("reverse", reason="x")


@pytest.mark.parametrize(("condition", "root", "expected"), [
    ("a", {"a": 1}, True), ("a", {"a": False}, False), ("a.b", {"a": {"b": "x"}}, True),
    ({"path": "s", "equals": "draft"}, {"s": "draft"}, True), ({"path": "s", "notEquals": "draft"}, {"s": "draft"}, False),
    ({"all": ["a", {"not": "b"}]}, {"a": 1}, True), ({"any": ["a", "b"]}, {}, False),
    ({"path": "a", "exists": False}, {}, True)])
def test_bedingungen_wie_condition_engine(condition, root, expected):
    assert docflow.evaluate(condition, root) is expected


# --------------------------------------------------------------------------------------------- Ende zu Ende


def _jwt(**claims) -> str:
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")  # noqa: E731
    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


def test_cli_laedt_belegzustand_und_bucht_ueber_den_adapter(tmp_path, monkeypatch):
    monkeypatch.setenv("VALEO_API_URL", "https://api.invalid")
    monkeypatch.setenv("VALEO_CLI_SESSION", str(tmp_path / "s.json"))
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", _jwt(sub="u", tenant_id="t", identity_type="human", exp=4_000_000_000))
    post = {**action("post"), "key": "buchen", "enabledWhen": "aktion_buchen", "requiresConfirmation": True}
    definition = {"id": "beleg/sales-invoice", "actions": [post],
                  "dataSources": [{"key": "entity", "endpoint": "/api/v1/belege/sales_invoice/{entity_id}/kopf"}]}
    calls = []

    def handler(request):
        calls.append((request.method, request.url.path, json.loads(request.content) if request.content else None))
        if request.url.path.endswith("/screen-definition"):
            return httpx.Response(200, json=definition)
        if request.url.path.endswith("/kopf"):
            return httpx.Response(200, json={"version": 3, "aktion_buchen": True,
                                             "aktionen": [{"key": "buchen", "erlaubt": True}]})
        return httpx.Response(200, json={"command": "post", "status": "ok", "source_doc_id": "doc-9", "posting_id": "p1"})

    lines = []
    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        code = cli.main(["ausfuehren", "beleg/sales-invoice", "buchen", "--id", "doc-9", "--ja", "--idempotenz", "key-12345"],
                        http=http, out=lines.append, stdin=io.StringIO(""))
    assert code == 0 and "Belegaktion abgeschlossen" in "\n".join(lines)
    method, path, body = calls[-1]
    assert (method, path) == ("POST", "/api/v1/docflow/doc-9/post")
    assert body == {"expected_version": 3, "idempotency_key": "key-12345"}
    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        code = cli.main(["ausfuehren", "beleg/sales-invoice", "buchen", "--id", "doc-9", "--ja", "--version", "2"],
                        http=http, out=lines.append, stdin=io.StringIO(""))
    assert code == 1 and "Belegversion hat sich geaendert" in lines[-1] and calls[-1][1].endswith("/kopf")
