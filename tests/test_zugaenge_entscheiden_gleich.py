"""Eine Fachaktion, vier Zugaenge, eine Entscheidung (Nutzerauftrag 09.11.2026).

REST (der dokumentierte Kommandoweg), Studio (was die Maske aus ihrer ScreenDefinition schickt), CLI
(``valeo ausfuehren``) und MCP (``mask.action.execute``) muessen dieselbe fachliche Entscheidung treffen: derselbe
Erfolg, dieselbe Pruefmeldung, dieselben Feldfehler - und im Trockenlauf schreibt keiner etwas. Echte signierte
Tokens, echte Routen; MCP wird nur im Transport auf die echte Route zurueckgefuehrt, nie mit einer Fake-Antwort.

Was bewusst NICHT verglichen wird: Transportregeln, die nur Agenten betreffen (Bestaetigung, Idempotenzschluessel,
Begruendung schon vor dem Weiterleiten). Die prueft ``test_mcp_vorpruefung_ist_strenger_nie_weicher``.
"""
from __future__ import annotations

import io
import json
from typing import Any
from uuid import uuid4

import httpx
import pytest
import sqlalchemy as sa

from app.core.screen_definitions import get_screen_definition
from app.core.tenant_binding import install_tenant_bindings
from app.services import mcp_mask_actions
from main import BearerAuthMiddleware
from valeo_cli import cli
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

ROLLEN = ["admin", "SALES_BEARBEITEN", "SALES_LESEN", "CRM_BEARBEITEN", "CRM_LESEN", "EINKAUF_BEARBEITEN",
          "EINKAUF_LESEN"]

# (Maske, Aktion, entity_id, Eingabe) - gueltige und abgelehnte Faelle je Fachaktion.
FAELLE: list[tuple[str, str, str | None, dict[str, Any]]] = [
    ("admin/nummernkreise", "konfigurieren", None,
     {"range_type": "debtor_account", "prefix": "D", "start_number": 10000, "digit_count": 5}),
    ("admin/nummernkreise", "konfigurieren", None, {"range_type": "irgendwas", "start_number": 1, "digit_count": 5}),
    ("admin/nummernkreise", "konfigurieren", None, {"range_type": "partner_number", "start_number": 1, "digit_count": 11}),
    ("admin/nummernkreise", "stilllegen", "gibt-es-nicht", {}),
    ("admin/report-berechtigungen", "anlegen", None, {"role_id": "controller", "report_key": "finance.bwa"}),
    ("admin/report-berechtigungen", "anlegen", None, {"role_id": "", "report_key": "finance.bwa"}),
    ("admin/rollen-verwaltung", "anlegen", None, {"name": "Disposition", "beschreibung": "Touren"}),
    ("admin/rollen-verwaltung", "anlegen", None, {"name": ""}),
    ("admin/rollen-verwaltung", "entfernen", "gibt-es-nicht", {}),
    ("crm/vertreterprovisionen", "anlegen", None,
     {"gruppe_nr": "P1", "bezeichnung": "Fest", "richtung": "vk", "provisionstyp": "fix", "provisionssatz": 2.5}),
    ("crm/vertreterprovisionen", "anlegen", None,
     {"gruppe_nr": "P2", "bezeichnung": "Fest", "richtung": "vk", "provisionstyp": "fix"}),
    ("crm/vertreterprovisionen", "anlegen", None,
     {"gruppe_nr": "P3", "bezeichnung": "Zu viel", "provisionstyp": "fix", "provisionssatz": 120}),
    ("admin/webshop", "anlegen", None,
     {"shop_url": "https://shop.example", "shop_system": "SHOPWARE6", "api_key": "x" * 12}),
    ("admin/webshop", "anlegen", None, {"shop_url": "shop.example", "shop_system": "SHOPWARE6", "api_key": "x" * 12}),
    ("bestellvorschlag/lager", "speichern", None, {"bezeichnung": "Test"}),
]


def _entscheidung(antwort: dict[str, Any]) -> dict[str, Any]:
    """Was fachlich entschieden wurde - ohne Kennungen, Zeiten und Transportfelder."""
    return {"success": antwort.get("success"), "error": antwort.get("error"),
            "felder": sorted((v.get("field"), v.get("message")) for v in (antwort.get("validationErrors") or []))}


@pytest.fixture
def zugaenge(subject_data, monkeypatch):  # noqa: F811 - Fixture aus test_gdpr_subject_boundary
    from app.api.v1.endpoints import (
        admin_reporting_kommandos,
        admin_rollen_kommandos,
        einkauf_bestellvorschlag_kommandos,
        mask_screen_definition,
        mcp_tool_registry,
        number_ranges_kommandos,
        vertreterprovisionen_kommandos,
        webshop_kommandos,
    )

    client, db, provider, tenant, *_ = subject_data
    for modul in (number_ranges_kommandos, admin_reporting_kommandos, admin_rollen_kommandos,
                  vertreterprovisionen_kommandos, webshop_kommandos):
        client.app.include_router(modul.router, prefix="/api/v1")
    client.app.include_router(einkauf_bestellvorschlag_kommandos.router, prefix="/api/v1")
    client.app.include_router(mask_screen_definition.router, prefix="/api/v1")
    client.app.include_router(mcp_tool_registry.router, prefix="/api/v1")
    install_tenant_bindings(client.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)

    def token(art: str = "human", rollen: list[str] = ROLLEN, sub: str = "parity-mensch") -> str:
        return provider.token(tenant, changes={"sub": sub, "identity_type": art, "roles": rollen,
                                               "scope": "masks:write"})

    weitergeleitet: list[httpx.Request] = []

    def zurueck(request: httpx.Request) -> httpx.Response:
        weitergeleitet.append(request)
        antwort = client.request(request.method, request.url.path, content=request.content,
                                 headers=dict(request.headers))
        return httpx.Response(antwort.status_code, content=antwort.content,
                              headers={"content-type": "application/json"}, request=request)

    original = mcp_mask_actions.execute
    monkeypatch.setattr(mcp_mask_actions, "execute", lambda req, tid, authorization:
                        original(req, tid, authorization, transport=httpx.MockTransport(zurueck)))
    return {"client": client, "db": db, "token": token, "weitergeleitet": weitergeleitet, "tenant": tenant}


def _aktion(maske: str, schluessel: str) -> dict[str, Any]:
    definition = get_screen_definition(maske)
    assert definition is not None, maske
    aktionen = [*definition.get("actions", []), *(a for t in definition.get("tables") or []
                                                   for a in t.get("rowActions") or [])]
    return next(a for a in aktionen if a["key"] == schluessel)


def _pfad(aktion: dict[str, Any], kennung: str | None) -> str:
    return aktion["commandEndpoint"].replace("{entity_id}", kennung or "")


def _mandant_da(z) -> None:
    """Testgeschirr: Der Trockenlauf setzt die gemeinsame Testsitzung zurueck und nimmt die Mandantenzeile des
    Fixtures mit. In Betrieb hat jede Anfrage ihre eigene Sitzung; damit kein Zugang am Geschirr scheitert, steht der
    Mandant vor jedem Aufruf wieder da."""
    z["db"].execute(sa.text("INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:t, :t, :d, true) "
                            "ON CONFLICT (id) DO NOTHING"), {"t": z["tenant"], "d": z["tenant"] + ".invalid"})
    z["db"].flush()


def _rest(z, maske, schluessel, kennung, eingabe) -> dict:
    """Der dokumentierte Weg: OpenAPI-Pfad der Aktion, Trockenlauf."""
    _mandant_da(z)
    pfad = _pfad(_aktion(maske, schluessel), kennung)
    antwort = z["client"].post(pfad, headers={"Authorization": "Bearer " + z["token"]()},
                               json={"_mode": "dryRun", **eingabe})
    assert antwort.status_code == 200, (pfad, antwort.status_code, antwort.text)
    return antwort.json()


def _studio(z, maske, schluessel, kennung, eingabe) -> dict:
    """Was die Maske schickt: Methode, Pfad und nur die Felder, die die Aktion als Eingabe erklaert."""
    _mandant_da(z)
    aktion = _aktion(maske, schluessel)
    erklaert = {f["key"] for f in aktion.get("inputFields") or []}
    unbekannt = set(eingabe) - erklaert
    assert not unbekannt or not erklaert, f"{maske}:{schluessel} kennt die Eingabe {sorted(unbekannt)} nicht"
    antwort = z["client"].request((aktion.get("method") or "POST").upper(), _pfad(aktion, kennung),
                                  headers={"Authorization": "Bearer " + z["token"]()},
                                  json={"_mode": "dryRun", **eingabe})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def _cli(z, maske, schluessel, kennung, eingabe, monkeypatch) -> dict:
    _mandant_da(z)
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", z["token"]())
    zeilen: list[str] = []
    argumente = ["ausfuehren", maske, schluessel, "--daten", "-", "--modus", "dryRun", "--ja", "--json"]
    if kennung:
        argumente += ["--id", kennung]
    code = cli.main(argumente, http=z["client"], out=zeilen.append, stdin=io.StringIO(json.dumps(eingabe)))
    assert zeilen, f"CLI ohne Ausgabe (Code {code})"
    return json.loads(zeilen[-1])


def _mcp(z, maske, schluessel, kennung, eingabe) -> dict:
    _mandant_da(z)
    parameter: dict[str, Any] = {"screen_id": maske, "action": schluessel, "input": eingabe}
    if kennung:
        parameter["entity_id"] = kennung
    antwort = z["client"].post("/api/v1/mcp/tools/call", headers={"Authorization": "Bearer " + z["token"]("agent")},
                               json={"tool_name": "mask.action.execute", "mode": "dryRun", "parameters": parameter})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()["result"]


def _bestand(db) -> dict[str, int]:
    tabellen = ("domain_shared.number_ranges", "domain_shared.admin_report_permissions",
                "domain_shared.vertreter_provisionsgruppen", "domain_shared.webshop_configs",
                "domain_einkauf.bestellvorschlaege", "outbox_events")
    return {t: db.execute(sa.text(f"SELECT count(*) FROM {t}")).scalar() for t in tabellen}  # nosec B608  # reviewed-safe: feste Tabellenliste


@pytest.mark.parametrize("maske,schluessel,kennung,eingabe", FAELLE,
                         ids=[f"{m}:{a}:{i}" for i, (m, a, _k, _e) in enumerate(FAELLE)])
def test_alle_zugaenge_treffen_dieselbe_entscheidung(zugaenge, monkeypatch, maske, schluessel, kennung, eingabe):
    vorher = _bestand(zugaenge["db"])
    rest = _entscheidung(_rest(zugaenge, maske, schluessel, kennung, eingabe))
    studio = _entscheidung(_studio(zugaenge, maske, schluessel, kennung, eingabe))
    werkzeug = _entscheidung(_cli(zugaenge, maske, schluessel, kennung, eingabe, monkeypatch))
    agent = _entscheidung(_mcp(zugaenge, maske, schluessel, kennung, eingabe))
    assert studio == rest, ("Studio weicht von REST ab", studio, rest)
    assert werkzeug == rest, ("CLI weicht von REST ab", werkzeug, rest)
    assert agent == rest, ("MCP weicht von REST ab", agent, rest)
    assert _bestand(zugaenge["db"]) == vorher, "Trockenlauf hat geschrieben"


def test_die_zugaenge_kennen_denselben_weg():
    """Studio-Aktion, CLI-Register und MCP-Karte zeigen fuer jede Fachaktion auf denselben Kommandoweg."""
    import yaml
    from pathlib import Path

    wurzel = Path(__file__).resolve().parents[1]
    register = set(json.loads((wurzel / "config/cli_mask_commands.json").read_text(encoding="utf-8"))["mask_action_ids"])
    karte = {m["mask_action_id"]: m for m in yaml.safe_load(
        (wurzel / "config/mcp_mask_action_map.yaml").read_text(encoding="utf-8"))["mappings"]}
    for maske, schluessel, _kennung, _eingabe in FAELLE:
        kennung = f"mask:{maske}:{schluessel}"
        assert kennung in register, f"{kennung} fehlt der CLI"
        assert kennung in karte, f"{kennung} fehlt der MCP-Karte"
        assert karte[kennung]["coverage"] not in ("unclassified", "open_high"), (kennung, karte[kennung]["coverage"])
        assert _aktion(maske, schluessel).get("commandEndpoint", "").startswith("/api/v1/"), kennung


def test_ohne_rolle_lehnen_alle_zugaenge_ab(zugaenge, monkeypatch):
    """Dieselbe Rechteentscheidung: ohne Admin-Rolle konfiguriert niemand einen Nummernkreis."""
    eingabe = {"range_type": "debtor_account", "start_number": 10000, "digit_count": 5}
    schwach = zugaenge["token"](rollen=["SALES_LESEN"])
    rest = zugaenge["client"].post("/api/v1/admin/number-ranges/actions/konfigurieren",
                                   headers={"Authorization": "Bearer " + schwach}, json={"_mode": "dryRun", **eingabe})
    assert rest.status_code == 403
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", schwach)
    zeilen: list[str] = []
    code = cli.main(["ausfuehren", "admin/nummernkreise", "konfigurieren", "--daten", "-", "--modus", "dryRun",
                     "--ja", "--json"], http=zugaenge["client"], out=zeilen.append,
                    stdin=io.StringIO(json.dumps(eingabe)))
    assert code != 0
    agent = zugaenge["client"].post("/api/v1/mcp/tools/call", headers={
        "Authorization": "Bearer " + zugaenge["token"]("agent", rollen=["SALES_LESEN"])}, json={
        "tool_name": "mask.action.execute", "mode": "dryRun",
        "parameters": {"screen_id": "admin/nummernkreise", "action": "konfigurieren", "input": eingabe}})
    assert agent.status_code == 403


def test_mcp_vorpruefung_ist_strenger_nie_weicher(zugaenge):
    """Agenten brauchen fuer execute Bestaetigung, Idempotenzschluessel und - wo verlangt - die Begruendung, bevor
    ueberhaupt weitergeleitet wird. Strenger als REST ist erlaubt; weicher nie: was REST ablehnt, lehnt MCP auch ab."""
    agent = {"Authorization": "Bearer " + zugaenge["token"]("agent")}

    def rufe(aktion: str, kennung: str | None, **zusatz) -> httpx.Response:
        _mandant_da(zugaenge)
        parameter = {"screen_id": "admin/rollen-verwaltung", "action": aktion, "input": {"name": "Kanal"},
                     **({"entity_id": kennung} if kennung else {})}
        parameter.update(zusatz.pop("parameter", {}))
        return zugaenge["client"].post("/api/v1/mcp/tools/call", headers=agent, json={
            "tool_name": "mask.action.execute", "mode": "execute", "parameters": parameter, **zusatz})

    vorher = len(zugaenge["weitergeleitet"])
    assert rufe("anlegen", None).status_code == 422                     # ohne Idempotenzschluessel
    entfernen = rufe("entfernen", "gibt-es-nicht", idempotency_key=str(uuid4()), parameter={"input": {}, "confirm": True})
    assert entfernen.status_code == 422                                  # Begruendung fehlt
    ohne_bestaetigung = rufe("entfernen", "gibt-es-nicht", idempotency_key=str(uuid4()),
                             parameter={"input": {}, "audit_reason": "Test"})
    assert ohne_bestaetigung.status_code == 422                          # Bestaetigung fehlt
    assert len(zugaenge["weitergeleitet"]) == vorher                     # nichts davon erreicht die Route
    # Und was REST fachlich ablehnt, lehnt auch MCP ab (nie weicher):
    _mandant_da(zugaenge)
    rest = zugaenge["client"].post("/api/v1/admin/rollen/gibt-es-nicht/actions/entfernen", headers={
        "Authorization": "Bearer " + zugaenge["token"]()}, json={"_auditReason": "Test"}).json()
    werkzeug = rufe("entfernen", "gibt-es-nicht", idempotency_key=str(uuid4()),
                    parameter={"input": {}, "audit_reason": "Test", "confirm": True})
    assert rest["success"] is False
    assert werkzeug.status_code == 200 and werkzeug.json()["result"]["success"] is False
    assert werkzeug.json()["result"]["error"] == rest["error"]
