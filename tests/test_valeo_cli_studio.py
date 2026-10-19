"""MASK-CLI Meilenstein 2 — Masken per CLI ueber die Studio-API erzeugen, ohne eigenen Weg daneben."""
from __future__ import annotations

import base64
import io
import json

import httpx
import pytest

from valeo_cli import cli


def _jwt(**claims) -> str:
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")  # noqa: E731
    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


HUMAN = _jwt(sub="u1", tenant_id="t1", identity_type="human", exp=4_000_000_000)


@pytest.fixture(autouse=True)
def umgebung(tmp_path, monkeypatch):
    monkeypatch.setenv("VALEO_API_URL", "https://api.invalid")
    monkeypatch.setenv("VALEO_OIDC_ISSUER", "https://idp.invalid/realms/fixture")
    monkeypatch.setenv("VALEO_CLI_SESSION", str(tmp_path / "sitzung.json"))

PROPOSAL = {"schemaVersion": 1, "id": "tenant/lieferanten-bewertung", "domain": "einkauf", "mode": "list",
            "title": "Lieferanten-Bewertung",
            "adapter": {"type": "native", "sourceId": "tenant/lieferanten-bewertung", "temporary": True}}


class Studio:
    """Studio-Server-Fake: Revisionspruefung, Wiederholungsschluessel und Rechte wie studio_drafts.py."""

    def __init__(self, can_publish=False):
        self.drafts: dict[str, dict] = {}
        self.calls: list[tuple[str, str, dict | None]] = []
        self.can_publish = can_publish
        self.keys: set[str] = set()

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content) if request.content else None
        path = request.url.path.removeprefix("/api/v1/studio")
        self.calls.append((request.method, path, body))
        if path == "/propose":
            return httpx.Response(200, json=self._report(PROPOSAL))
        if path == "/validate":
            return httpx.Response(200, json=self._report(body["definition"]))
        if path == "/native-sources":
            return httpx.Response(200, json={"items": [{"screen_id": "agrar/duenger", "title": "Duenger",
                                                        "source_hash": "a" * 64}], "total": 1})
        if path == "/native-imports":
            assert body["expected_source_hash"] == "a" * 64
            return httpx.Response(200, json=self._save({**PROPOSAL, "id": "tenant/native-x"}, body))
        if path == "/drafts" and request.method == "POST":
            if any(d["definition"]["id"] == body["definition"]["id"] for d in self.drafts.values()):
                return httpx.Response(409, json={"detail": "screen_id_bereits_vorhanden"})
            return httpx.Response(200, json={**self._save(body["definition"], body), **self._report(body["definition"])})
        draft_id = path.split("/")[2] if path.startswith("/drafts/") else None
        draft = self.drafts.get(draft_id)
        if path == f"/drafts/{draft_id}" and request.method == "GET":
            return httpx.Response(200, json=draft)
        if request.method in ("PUT", "POST") and draft is not None:
            if body["expected_revision"] != draft["revision"]:
                return httpx.Response(409, json={"detail": "entwurf_seit_anzeige_geaendert"})
            if path.endswith("/publish") and not self.can_publish:
                return httpx.Response(403, json={"detail": "Menschliche Administration fuer Studio-Publikation erforderlich"})
            if path.endswith("/simulate"):
                return httpx.Response(200, json={**draft, "simulation": {"passed": False, "profile": "grain.v1",
                                                                         "failed_checks": ["domain_not_covered"]}})
            status = {"submit-review": "review", "publish": "published_temp", "retire": "retired"}.get(path.split("/")[-1])
            definition = body.get("definition", draft["definition"])
            draft.update(definition=definition, status=status or draft["status"], revision=f"{len(self.calls):064x}")
            return httpx.Response(200, json={**draft, "route": "/studio/run/x" if status == "published_temp" else None})
        return httpx.Response(404, json={"detail": "nicht gefunden"})

    @staticmethod
    def _report(definition):
        bad = definition.get("adapter", {}).get("sourceId") != definition.get("id")
        return {"definition": definition, "definitionReady": not bad,
                "violations": ["adapter_muss_native_und_an_screen_id_gebunden_sein"] if bad else [],
                "readiness": {"errors": ["[non_temporary] adapter.temporary=true"], "warnings": []}}

    def _save(self, definition, body):
        assert body["idempotency_key"] not in self.keys, "jeder neue Aufruf braucht einen neuen Schluessel"
        self.keys.add(body["idempotency_key"])
        draft_id = f"d{len(self.drafts) + 1}"
        self.drafts[draft_id] = {"id": draft_id, "status": "draft", "revision": "0" * 64,
                                 "screen_id": definition["id"], "definition": definition}
        return self.drafts[draft_id]


def run(argv, studio, monkeypatch, stdin=""):
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", HUMAN)
    lines: list[str] = []
    with httpx.Client(transport=httpx.MockTransport(studio)) as http:
        code = cli.main(["studio", *argv], http=http, out=lines.append, ask=lambda _: "", stdin=io.StringIO(stdin))
    return code, "\n".join(lines)


def test_vorschlag_mit_eigener_kennung_zieht_die_adapterbindung_mit(monkeypatch):
    studio = Studio()
    code, out = run(["vorschlag", "Lieferanten mit Ort", "--maske", "tenant/eigene", "--speichern"], studio, monkeypatch)
    assert code == 0 and "Entwurf angelegt: d1" in out
    saved = studio.drafts["d1"]["definition"]
    assert saved["id"] == "tenant/eigene" and saved["adapter"]["sourceId"] == "tenant/eigene"
    assert "nicht blockierend" in out and "Fehler" not in out


def test_fremde_adapterbindung_bleibt_und_der_server_entscheidet(monkeypatch, tmp_path):
    datei = tmp_path / "d.json"
    datei.write_text(json.dumps({**PROPOSAL, "adapter": {"type": "native", "sourceId": "agrar/duenger"}}), encoding="utf-8")
    code, out = run(["pruefen", str(datei)], Studio(), monkeypatch)
    assert code == 1 and "adapter_muss_native" in out


def test_vorschlag_mit_verstoessen_wird_nicht_gespeichert(monkeypatch):
    studio = Studio()
    original = Studio._report
    monkeypatch.setattr(Studio, "_report", staticmethod(lambda d: {**original(d), "violations": ["x"],
                                                                     "definitionReady": False}))
    code, out = run(["vorschlag", "irgendwas", "--speichern"], studio, monkeypatch)
    assert code == 1 and "Nicht gespeichert" in out and not studio.drafts


def test_aendern_nur_mit_gesehener_revision(monkeypatch, tmp_path):
    studio = Studio()
    run(["vorschlag", "x", "--speichern"], studio, monkeypatch)
    datei = tmp_path / "e.json"
    run(["zeigen", "d1", "--ausgabe", str(datei)], studio, monkeypatch)
    code, out = run(["speichern", str(datei), "--entwurf", "d1"], studio, monkeypatch)
    assert code == 2 and "Revision" in out
    code, _ = run(["speichern", str(datei), "--entwurf", "d1", "--revision", "0" * 64], studio, monkeypatch)
    assert code == 0
    code, out = run(["speichern", str(datei), "--entwurf", "d1", "--revision", "0" * 64], studio, monkeypatch)
    assert code == 1 and "entwurf_seit_anzeige_geaendert" in out, "veraltete Revision ist ein fachlicher Konflikt"


def test_speichern_akzeptiert_die_ausgabe_von_zeigen_und_stdin(monkeypatch):
    studio = Studio()
    code, _ = run(["speichern", "-"], studio, monkeypatch, stdin=json.dumps({"definition": {**PROPOSAL, "id": "tenant/a",
                                                                                           "adapter": {"sourceId": "tenant/a"}}}))
    assert code == 0 and studio.drafts["d1"]["screen_id"] == "tenant/a"


def test_lebenslauf_pruefung_simulation_freigabe(monkeypatch):
    studio = Studio()
    run(["vorschlag", "x", "--speichern"], studio, monkeypatch)
    code, out = run(["pruefung", "d1"], studio, monkeypatch)
    assert code == 0 and "review" in out
    reviewed = studio.drafts["d1"]["revision"]
    code, out = run(["simulieren", "d1"], studio, monkeypatch)
    assert code == 1 and "domain_not_covered" in out
    code, out = run(["freigeben", "d1"], studio, monkeypatch)
    assert code == 2 and "--revision" in out, "freigegeben wird nur, was man gesehen hat"
    code, out = run(["freigeben", "d1", "--revision", reviewed], studio, monkeypatch)
    assert code == 3 and "Administration" in out
    studio.can_publish = True
    code, out = run(["freigeben", "d1", "--revision", reviewed], studio, monkeypatch)
    assert code == 0 and "published_temp" in out and "/studio/run/x" in out


def test_uebernehmen_bindet_den_angezeigten_quellhash(monkeypatch):
    studio = Studio()
    code, out = run(["uebernehmen", "agrar/duenger"], studio, monkeypatch)
    assert code == 0 and "Uebernommen" in out
    code, out = run(["uebernehmen", "gibt/es-nicht"], studio, monkeypatch)
    assert code == 2 and "Keine uebernehmbare Maske" in out


def test_wiederholung_mit_gleichem_schluessel(monkeypatch):
    studio = Studio()
    run(["vorschlag", "x", "--speichern", "--idempotenz", "k-1"], studio, monkeypatch)
    sent = [body for method, path, body in studio.calls if path == "/drafts" and method == "POST"]
    assert sent[0]["idempotency_key"] == "k-1"


@pytest.mark.parametrize("cmd", [["katalog"], ["quellen"], ["entwuerfe"]])
def test_lesende_befehle_schreiben_nichts(monkeypatch, cmd):
    studio = Studio()
    studio_catalog = {"version": "v", "dataSources": [], "actions": [], "permissions": {}}
    original = studio.__call__

    def handler(request):
        if request.url.path.endswith("/catalog"):
            return httpx.Response(200, json=studio_catalog)
        if request.url.path.endswith("/drafts") and request.method == "GET":
            return httpx.Response(200, json={"drafts": []})
        return original(request)

    code, _ = run(cmd, handler, monkeypatch)
    assert code == 0 and all(method == "GET" for method, _, _ in studio.calls)


CATALOG = {"version": "v", "permissions": {"canDesign": True},
           "dataSources": [{"key": "duenger", "label": "Duenger", "endpoint": "/api/v1/agrar/duenger"}],
           "actions": [{"key": "freigeben", "label": "Freigeben", "dangerLevel": "moderate",
                        "commandEndpoint": "/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben",
                        "forbiddenForAgents": False},
                       {"key": "stornieren", "label": "Stornieren", "dangerLevel": "high",
                        "commandEndpoint": "/api/v1/x/{entity_id}/stornieren", "forbiddenForAgents": True}]}


def test_neu_setzt_nur_katalogquellen_und_katalogaktionen_zusammen():
    from valeo_cli.studio import compose
    d = compose(CATALOG, screen_id="tenant/d", title="D", domain="agrar", source_key="duenger",
                columns=[("name", "Name")], action_keys=["stornieren"])
    assert d["dataSources"] == [{"key": "duenger", "endpoint": "/api/v1/agrar/duenger", "pageSize": 50}]
    [action] = d["actions"]
    assert action["dangerLevel"] == "high" and action["forbiddenForAgents"] is True and action["requiresConfirmation"]
    assert d["agentContract"]["editableFields"] == [] and d["adapter"]["sourceId"] == "tenant/d"
    assert d["agentContract"]["availableActions"][0]["requiresHumanApproval"] is True
    with pytest.raises(ValueError, match="nicht im Studio-Katalog"):
        compose(CATALOG, screen_id="tenant/d", title="D", domain="agrar", source_key="frei",
                columns=[("a", "A")], action_keys=[])
    with pytest.raises(ValueError, match="nicht im Studio-Katalog"):
        compose(CATALOG, screen_id="tenant/d", title="D", domain="agrar", source_key="duenger",
                columns=[("a", "A")], action_keys=["eigene"])
    with pytest.raises(ValueError, match="--spalte"):
        compose(CATALOG, screen_id="tenant/d", title="D", domain="agrar", source_key="duenger",
                columns=[], action_keys=[])


def test_lesende_agrarliste_aus_neu_passt_ins_freigabeprofil():
    from app.core.studio_release import profile_errors
    from valeo_cli.studio import compose
    d = compose(CATALOG, screen_id="tenant/d", title="D", domain="agrar", source_key="duenger",
                columns=[("name", "Name")], action_keys=[])
    assert profile_errors(d) == []


def test_neu_prueft_beim_server_und_speichert_nur_ohne_verstoss(monkeypatch):
    studio = Studio()
    original = studio.__call__

    def handler(request):
        if request.url.path.endswith("/catalog"):
            return httpx.Response(200, json=CATALOG)
        return original(request)

    code, out = run(["neu", "--maske", "tenant/d", "--titel", "D", "--domaene", "agrar", "--quelle", "duenger",
                     "--spalte", "name=Name", "--speichern"], handler, monkeypatch)
    assert code == 0 and "Entwurf angelegt" in out
    assert [p for m, p, _ in studio.calls] == ["/validate", "/drafts"]
    code, out = run(["neu", "--maske", "tenant/e", "--titel", "E", "--domaene", "agrar", "--quelle", "frei",
                     "--spalte", "x"], handler, monkeypatch)
    assert code == 2 and "nicht im Studio-Katalog" in out
