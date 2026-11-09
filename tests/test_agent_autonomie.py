"""Risikobasierte Agentenautonomie (ADR-086) gegen die echte Datenbank, alles in einer zurueckgerollten Transaktion.

Geprueft: Ohne fachlich freigegebene Politik bucht kein Agent autonom. Mit Freigabe, Delegation und Testnachweis
bucht er eine Routinegutschrift selbst - aber nie, wenn die Risiko-Engine eine unabhaengige Freigabe verlangt, ein
Pruefagent einwendet oder das Qualitaetsmodell kippt (dann wird die Delegation automatisch entzogen). Kein Agent gibt
frei, delegiert oder bewertet sich selbst; jede Entscheidung steht unveraenderlich im Protokoll.
"""
from __future__ import annotations

import importlib.util
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

WURZEL = Path(__file__).resolve().parents[1]
DB_URL = __import__("os").environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")
AGENT = "agent-buchhaltung-7"


def _migration():
    spec = importlib.util.spec_from_file_location("autonomie", WURZEL / "alembic/versions/agent_autonomie_20261109.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture
def welt(monkeypatch):
    from app.finance.steuerschluessel import richte_skr03_ein

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    aussen = verbindung.begin()
    if not verbindung.execute(sa.text("SELECT to_regclass('domain_shared.agent_delegations')")).scalar():
        with Operations.context(MigrationContext.configure(verbindung)):
            _migration().upgrade()
    db = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    mandant, kunde = f"au-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    db.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": mandant})
    richte_skr03_ein(db, mandant)
    db.execute(sa.text("INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, "
                       "account_type, is_active) VALUES (:id, :t, '1400', 'Forderungen', 'asset', true)"),
               {"id": f"{mandant}-1400", "t": mandant})
    db.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                       "VALUES (:id, :t, 'kunde-1', 'Hof Autonom')"), {"id": kunde, "t": mandant})
    db.flush()
    welt = {"db": db, "mandant": mandant, "kunde": kunde}
    welt["rechnung"] = _rechnung(welt, "RE-AU-1", 1190.0)
    try:
        yield welt
    finally:
        db.close()
        aussen.rollback()
        verbindung.close()


def _rechnung(welt, nummer: str, brutto: float) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    return DocflowService(welt["db"], welt["mandant"], "verkauf-1").create_document(DocflowCreateRequest(
        doc_type="sales_invoice", doc_number=nummer, customer_id=welt["kunde"],
        items=[DocflowLineInput(article_number="W", quantity=1, unit_price=round(brutto / 1.19, 2), tax_code="3")]))


def _gutschrift(welt, netto: float, *, mit_rechnung: bool = True) -> str:
    from app.services.gutschrift_docflow import lege_entwurf_an

    return lege_entwurf_an(welt["db"], welt["mandant"], nummer=f"GS-AU-{uuid.uuid4().hex[:5]}", kunde="kunde-1",
                           rechnung="RE-AU-1" if mit_rechnung else None, akteur="verkauf-1",
                           zeilen=[{"description": "Retoure", "quantity": 1, "unit_price": netto, "tax_code": "3"}])


def _person(sub: str, *rollen: str) -> dict:
    return {"sub": sub, "name": sub, "roles": list(rollen), "raw": {"preferred_username": sub, "sub": sub}}


def _agentenidentitaet(sub: str = AGENT) -> dict:
    return {"sub": sub, "roles": ["FINANCE_BEARBEITEN"], "raw": {"sub": sub, "identity_type": "agent", "agent_id": sub}}


def _mcp(welt, agent: str = AGENT) -> TestClient:
    from app.api.v1.endpoints.mcp_tool_registry import get_current_user as mcp_nutzer
    from app.api.v1.endpoints.mcp_tool_registry import get_db as mcp_get_db
    from app.api.v1.endpoints.mcp_tool_registry import router as mcp_router

    app = FastAPI()
    app.include_router(mcp_router)
    app.dependency_overrides[mcp_nutzer] = lambda: {"sub": agent, "scopes": ["sales:write"],
                                                    "raw": {"tenant_id": welt["mandant"]}}
    app.dependency_overrides[mcp_get_db] = lambda: welt["db"]
    return TestClient(app, raise_server_exceptions=False)


def _rest(welt, nutzer: dict) -> TestClient:
    from app.api.v1.endpoints import agent_autonomie
    from app.auth.deps import get_current_user
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id

    app = FastAPI()
    app.include_router(agent_autonomie.router)
    app.dependency_overrides[get_current_user] = lambda: nutzer
    app.dependency_overrides[get_db] = lambda: welt["db"]
    app.dependency_overrides[get_tenant_id] = lambda: welt["mandant"]
    return TestClient(app, raise_server_exceptions=False)


def _buche(welt, gutschrift: str, mode: str = "execute"):
    return _mcp(welt).post("/mcp/tools/call", json={
        "tool_name": "sales.gutschrift.buchen", "mode": mode, "idempotency_key": f"auto-{gutschrift}",
        "parameters": {"credit_note_id": gutschrift}})


def _status(welt, beleg: str) -> str:
    return welt["db"].execute(sa.text("SELECT status FROM domain_docflow.document_headers WHERE id = :i"),
                              {"i": beleg}).scalar()


def _bereit(welt, *, max_brutto: float | None = None, test: str = "test_bestanden") -> None:
    """Fachliche Freigabe der Politik, Delegation durch eine Person mit dem Recht, Testnachweis der CI."""
    gf = _rest(welt, _person("gf-1", "GESCHAEFTSFUEHRUNG"))
    assert gf.post("/agenten/autonomie/politik/actions/freigeben",
                   json={"notiz": "Fachlich geprueft und fuer Routinegutschriften freigegeben."}).status_code == 200
    fibu = _rest(welt, _person("fibu-1", "FINANCE_BEARBEITEN"))
    antwort = fibu.post("/agenten/autonomie/delegationen/actions/anlegen", json={
        "agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen", **({"max_brutto": max_brutto} if max_brutto else {})})
    assert antwort.status_code == 200, antwort.text
    ci = _rest(welt, {"sub": "service-account-ci", "roles": ["CI_TESTNACHWEIS"],
                      "raw": {"preferred_username": "service-account-ci"}})
    assert ci.post("/agenten/autonomie/qualitaet/actions/erfassen", json={
        "agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen", "art": test,
        "detail": {"suite": "tests/test_agent_autonomie.py"}}).status_code == 200


def _gruende(antwort) -> list[str]:
    """Gruende des zentralen Tors - oder die Meldung der Risiko-Engine, wenn sie selbst eine Freigabe verlangt."""
    detail = antwort.json()["detail"]
    return detail["gruende"] if isinstance(detail, dict) else [str(detail)]


# ── Ohne Politikfreigabe keine Autonomie ─────────────────────────────────────────────────────────────────────────


def test_ohne_fachliche_freigabe_bucht_kein_agent_autonom(welt):
    gutschrift = _gutschrift(welt, 100)
    antwort = _buche(welt, gutschrift)
    assert antwort.status_code == 409
    assert any("nicht fachlich freigegeben" in g for g in _gruende(antwort))
    assert _status(welt, gutschrift) == "draft"
    zeile = welt["db"].execute(sa.text("SELECT outcome FROM domain_shared.agent_autonomy_decisions WHERE "
                                       "tenant_id = :t AND subject_id = :s"), {"t": welt["mandant"], "s": gutschrift}).scalar()
    assert zeile == "freigabe"


def test_die_politikfreigabe_ist_eine_eigene_fachliche_entscheidung(welt):
    url = "/agenten/autonomie/politik/actions/freigeben"
    notiz = {"notiz": "Fachlich geprueft und freigegeben fuer den Mandanten."}
    assert _rest(welt, _person("fibu-1", "FINANCE_BEARBEITEN")).post(url, json=notiz).status_code == 403  # Rolle
    assert _rest(welt, _agentenidentitaet()).post(url, json=notiz).status_code == 422                    # Agent
    assert _rest(welt, _person("claude-code", "GESCHAEFTSFUEHRUNG")).post(url, json=notiz).status_code == 422  # Autor
    assert _rest(welt, _person("gf-1", "GESCHAEFTSFUEHRUNG")).post(url, json={"notiz": "ok"}).status_code == 422
    frei = _rest(welt, _person("gf-1", "GESCHAEFTSFUEHRUNG")).post(url, json=notiz)
    assert frei.status_code == 200 and frei.json()["freigegeben"] is True


def test_eine_geaenderte_politik_ist_nicht_freigegeben(welt):
    from app.services import agent_autonomie

    original = agent_autonomie.lade_politik()
    agent_autonomie.gib_politik_frei(welt["db"], welt["mandant"], _person("gf-1", "GESCHAEFTSFUEHRUNG"),
                                     "Fachlich geprueft und freigegeben.", original)
    geaendert_inhalt = {**original.inhalt, "faehigkeiten": {"sales.gutschrift.buchen": {
        **original.inhalt["faehigkeiten"]["sales.gutschrift.buchen"], "hoechstbetrag_brutto": 999999}}}
    geaendert = agent_autonomie.Politik(inhalt=geaendert_inhalt, abdruck=agent_autonomie.abdruck_von(geaendert_inhalt))
    assert agent_autonomie.politik_freigabe(welt["db"], welt["mandant"], original) is not None
    assert agent_autonomie.politik_freigabe(welt["db"], welt["mandant"], geaendert) is None


def test_delegiert_wird_nur_ein_eigenes_recht_und_nie_ueber_die_politikgrenze(welt):
    url = "/agenten/autonomie/delegationen/actions/anlegen"
    auftrag = {"agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen"}
    assert _rest(welt, _person("lager-1", "CONTROLLING")).post(url, json=auftrag).status_code == 403  # Recht fehlt
    assert _rest(welt, _agentenidentitaet("agent-anderer")).post(url, json=auftrag).status_code == 422
    zu_viel = _rest(welt, _person("fibu-1", "FINANCE_BEARBEITEN")).post(url, json={**auftrag, "max_brutto": 5000})
    assert zu_viel.status_code == 422 and "Politikgrenze" in zu_viel.text
    assert _rest(welt, _person("fibu-1", "FINANCE_BEARBEITEN")).post(url, json=auftrag).status_code == 200


# ── Der Regelfall: Routinegutschrift autonom ─────────────────────────────────────────────────────────────────────


def test_routinegutschrift_bucht_der_agent_autonom_und_protokolliert_alles(welt):
    _bereit(welt)
    gutschrift = _gutschrift(welt, 100)  # 119 EUR, mit Bezugsrechnung
    gebucht = _buche(welt, gutschrift)
    assert gebucht.status_code == 200, gebucht.text
    assert gebucht.json()["posted"] is True and gebucht.json()["policy_version"] == "1.0.0"
    assert _status(welt, gutschrift) == "posted"
    assert _buche(welt, gutschrift).json()["replayed"] is True  # derselbe Auftrag: eine Buchung
    db, t = welt["db"], welt["mandant"]
    assert db.execute(sa.text("SELECT outcome FROM domain_shared.agent_autonomy_decisions WHERE tenant_id = :t "
                              "AND subject_id = :s ORDER BY decided_at DESC LIMIT 1"), {"t": t, "s": gutschrift}).scalar() == "autonom"
    assert db.execute(sa.text("SELECT count(*) FROM domain_shared.agent_quality_events WHERE tenant_id = :t "
                              "AND kind = 'ausgefuehrt'"), {"t": t}).scalar() == 1


def test_der_trockenlauf_sagt_autonom_und_bucht_nicht(welt):
    """Letzter Schritt des Tests: Der Trockenlauf rollt die (im Test geteilte) Sitzung zurueck."""
    _bereit(welt)
    gutschrift = _gutschrift(welt, 100)
    trocken = _buche(welt, gutschrift, "dryRun")
    assert trocken.status_code == 200, trocken.text
    assert trocken.json()["autonom"] is True and trocken.json()["risk"] == "R2"


def test_ueber_der_delegierten_grenze_bucht_ein_mensch(welt):
    _bereit(welt, max_brutto=100)
    antwort = _buche(welt, _gutschrift(welt, 100))  # 119 > 100
    assert antwort.status_code == 409 and any("delegierten Grenze" in g for g in _gruende(antwort))


def test_verlangt_die_risiko_engine_eine_freigabe_bucht_kein_agent(welt, monkeypatch):
    from app.core.freigabe import Anforderung, Befund
    from app.services.docflow_freigabe import DocflowFreigabe

    _bereit(welt)
    kritisch = Anforderung("R3", "Moegliche Dublette.", (Befund("dublette", "kritisch", "Moegliche Dublette."),))
    monkeypatch.setattr(DocflowFreigabe, "anforderung", lambda self, v, aktion: kritisch)
    gutschrift = _gutschrift(welt, 100)
    antwort = _buche(welt, gutschrift)
    assert antwort.status_code == 409 and any("Freigabe erforderlich (R3)" in g for g in _gruende(antwort))
    assert _status(welt, gutschrift) == "draft"


def test_ein_einwand_des_pruefagenten_fuehrt_zum_menschen(welt):
    _bereit(welt)
    gutschrift = _gutschrift(welt, 100, mit_rechnung=False)  # ohne Bezugsrechnung
    antwort = _buche(welt, gutschrift)
    assert antwort.status_code == 409 and any("Bezugsrechnung" in g for g in _gruende(antwort))
    assert welt["db"].execute(sa.text("SELECT count(*) FROM domain_shared.agent_quality_events WHERE tenant_id = :t "
                                      "AND kind = 'einwand'"), {"t": welt["mandant"]}).scalar() == 1


def test_ein_ausgefallener_pruefagent_ist_ein_einwand_kein_ja(welt, monkeypatch):
    from app.services import agent_pruefagenten

    def kaputt(db, kontext):
        raise RuntimeError("Modell nicht erreichbar")

    monkeypatch.setitem(agent_pruefagenten._REGISTER, "plausibilitaet",
                        agent_pruefagenten.Pruefagent(kennung="pruefagent:plausibilitaet", pruefe_vorgang=kaputt))
    _bereit(welt)
    antwort = _buche(welt, _gutschrift(welt, 100))
    assert antwort.status_code == 409 and any("ausgefallen" in g for g in _gruende(antwort))


def test_ein_pruefagent_prueft_keinen_eigenen_vorgang(welt, monkeypatch):
    from app.services import agent_pruefagenten

    monkeypatch.setitem(agent_pruefagenten._REGISTER, "plausibilitaet",
                        agent_pruefagenten.Pruefagent(kennung=AGENT, pruefe_vorgang=lambda db, k: []))
    _bereit(welt)
    antwort = _buche(welt, _gutschrift(welt, 100))
    assert antwort.status_code == 409 and any("keinen eigenen Vorgang" in g for g in _gruende(antwort))


# ── Qualitaetsmodell: Verschlechterung entzieht die Autonomie ────────────────────────────────────────────────────


def test_korrigierte_buchungen_entziehen_die_delegation_automatisch(welt):
    _bereit(welt)
    fibu = _rest(welt, _person("fibu-2", "FINANCE_BEARBEITEN"))
    for _ in range(2):  # Startphase: mehr als ein korrigierter Fehler
        antwort = fibu.post("/agenten/autonomie/qualitaet/actions/erfassen", json={
            "agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen", "art": "korrigiert", "vorgang": "GS-x"})
        assert antwort.status_code == 200, antwort.text
    assert antwort.json()["qualitaet"]["im_rahmen"] is False
    db, t = welt["db"], welt["mandant"]
    entzug = db.execute(sa.text("SELECT revoked_by, revoke_reason FROM domain_shared.agent_delegations "
                                "WHERE tenant_id = :t AND agent_id = :a"), {"t": t, "a": AGENT}).first()
    assert entzug[0] == "qualitaetsmodell" and "korrigierte" in entzug[1]
    assert db.execute(sa.text("SELECT count(*) FROM domain_docflow.control_findings WHERE tenant_id = :t "
                              "AND code = 'agent_qualitaet'"), {"t": t}).scalar() == 1
    antwort = _buche(welt, _gutschrift(welt, 100))
    assert antwort.status_code == 409 and any("Keine gueltige Delegation" in g for g in _gruende(antwort))


def test_fehlgeschlagener_testnachweis_entzieht_die_autonomie(welt):
    _bereit(welt, test="test_fehlgeschlagen")
    antwort = _buche(welt, _gutschrift(welt, 100))
    assert antwort.status_code == 409
    assert any("Testnachweis ist fehlgeschlagen" in g or "Keine gueltige Delegation" in g for g in _gruende(antwort))


def test_kein_agent_bewertet_sich_selbst_und_keine_maschine_meldet_eine_korrektur(welt):
    selbst = _rest(welt, _person(AGENT, "FINANCE_BEARBEITEN")).post("/agenten/autonomie/qualitaet/actions/erfassen", json={
        "agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen", "art": "test_bestanden"})
    assert selbst.status_code == 422
    maschine = _rest(welt, {"sub": "service-account-ci", "roles": ["CI_TESTNACHWEIS"],
                            "raw": {"preferred_username": "service-account-ci"}})
    assert maschine.post("/agenten/autonomie/qualitaet/actions/erfassen", json={
        "agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen", "art": "korrigiert"}).status_code == 403


def test_das_entscheidungsprotokoll_ist_unveraenderlich(welt):
    _buche(welt, _gutschrift(welt, 100))
    db = welt["db"]
    with pytest.raises(sa.exc.DBAPIError, match="nicht geaendert"):
        with db.begin_nested():
            db.execute(sa.text("UPDATE domain_shared.agent_autonomy_decisions SET outcome = 'autonom' "
                               "WHERE tenant_id = :t"), {"t": welt["mandant"]})


def test_der_vorschlagsweg_bleibt_unveraendert(welt):
    """Ohne Autonomie: propose -> Freigabe durch einen Menschen -> buchen (tests/test_gutschrift_umsatzsteuer.py)."""
    antwort = _mcp(welt).post("/mcp/tools/call", json={"tool_name": "sales.gutschrift.buchen", "mode": "execute",
                                                       "idempotency_key": "x" * 10, "parameters": {}})
    assert antwort.status_code == 422  # genau eines: proposal_id oder credit_note_id
    assert Decimal("1000.00") == Decimal(str(
        __import__("app.services.agent_autonomie", fromlist=["x"]).lade_politik()
        .faehigkeit("sales.gutschrift.buchen")["hoechstbetrag_brutto"])).quantize(Decimal("0.01"))


# ── Agent Trust und lernende Governance ──────────────────────────────────────────────────────────────────────────


def test_die_vertrauensstufe_folgt_freigabe_delegation_und_qualitaet(welt):
    rest = _rest(welt, _person("gf-1", "GESCHAEFTSFUEHRUNG"))
    frage = {"agent_id": AGENT, "faehigkeit": "sales.gutschrift.buchen"}
    assert rest.get("/agenten/autonomie/vertrauen", params=frage).json()["stufe"] == "A0"
    _bereit(welt)
    assert rest.get("/agenten/autonomie/vertrauen", params=frage).json()["stufe"] == "A2"
    fibu = _rest(welt, _person("fibu-2", "FINANCE_BEARBEITEN"))
    fibu.post("/agenten/autonomie/qualitaet/actions/erfassen", json={**frage, "art": "test_fehlgeschlagen"})
    stand = rest.get("/agenten/autonomie/vertrauen", params=frage).json()
    assert stand["stufe"] == "A0" and stand["delegation"] is None  # Testnachweis gekippt: Delegation entzogen


def test_die_governance_lernt_aber_die_politik_aendert_sich_nicht_selbst(welt):
    from app.services import agent_autonomie

    _bereit(welt)
    abdruck_vorher = agent_autonomie.lade_politik().abdruck
    db, t = welt["db"], welt["mandant"]
    for nr in range(40):  # lange fehlerfreie Bilanz
        agent_autonomie.erfasse(db, t, agent_id=AGENT, faehigkeit="sales.gutschrift.buchen", art="ausgefuehrt",
                                durch="autonomie", vorgang=f"GS-{nr}")
    [erweitern] = agent_autonomie.lernvorschlaege(db, t)
    assert erweitern["richtung"] == "erweitern" and erweitern["aenderung"]["hoechstbetrag_brutto"] == 1500.0
    agent_autonomie.erfasse(db, t, agent_id=AGENT, faehigkeit="sales.gutschrift.buchen", art="korrigiert",
                            durch="fibu-2", vorgang="GS-0")
    [einschraenken] = agent_autonomie.lernvorschlaege(db, t)
    assert einschraenken["richtung"] == "einschraenken" and einschraenken["aenderung"]["hoechstbetrag_brutto"] == 500.0
    # Kein Vorschlag wirkt: Politik und Freigabe bleiben, bis ein Mensch eine neue Fassung freigibt.
    assert agent_autonomie.lade_politik().abdruck == abdruck_vorher
    assert agent_autonomie.politik_freigabe(db, t) is not None


# ── Durchsetzung an der zentralen Stelle (Freigabe-Engine) - nicht nur im MCP-Werkzeug ─────────────────────────


def _direkt_buchen(welt, beleg: str, *, als: str | None):
    """Der Buchungsweg ohne MCP-Werkzeug (wie REST /docflow/{id}/post): DocFlow -> Freigabe-Engine -> Tor."""
    from app.api.v1.schemas.docflow_schemas import DocflowPostRequest
    from app.services.agent_autonomie import als_agent
    from app.services.docflow_service import DocflowService

    with als_agent(als):
        return DocflowService(welt["db"], welt["mandant"], als or "fibu-1").post_document(
            beleg, DocflowPostRequest(idempotency_key=f"direkt-{beleg}", posted_by=als or "fibu-1"))


def test_auch_der_direkte_buchungsweg_fragt_die_autonomiepolitik(welt):
    from app.services.agent_autonomie import AutonomieVerweigert

    gutschrift = _gutschrift(welt, 100)
    with pytest.raises(AutonomieVerweigert) as fehler:
        _direkt_buchen(welt, gutschrift, als=AGENT)  # z. B. ein Agententoken mit Buchungsrolle auf REST
    assert any("nicht fachlich freigegeben" in g for g in fehler.value.gruende)
    welt["db"].rollback()
    assert _status(welt, gutschrift) == "draft"


def test_ein_mensch_bucht_dieselbe_gutschrift_wie_bisher(welt):
    gutschrift = _gutschrift(welt, 100)
    _direkt_buchen(welt, gutschrift, als=None)  # FIN-CONTROL-001 unveraendert: Routine ohne zweite Person
    assert _status(welt, gutschrift) == "posted"


def test_ohne_faehigkeit_in_der_politik_bucht_kein_agent_und_die_ablehnung_bleibt(welt):
    from app.services.agent_autonomie import AutonomieVerweigert

    _bereit(welt)
    rechnung = _rechnung(welt, "RE-AU-2", 119.0)  # Ausgangsrechnung: keine Faehigkeit in der Politik
    with pytest.raises(AutonomieVerweigert) as fehler:
        _direkt_buchen(welt, rechnung, als=AGENT)
    assert fehler.value.ergebnis == "abgelehnt" and "sales_invoice/post" in fehler.value.gruende[0]
    welt["db"].rollback()  # das Kommando rollt zurueck - das Protokoll der Ablehnung nicht
    engine = sa.create_engine(DB_URL)
    with engine.connect() as getrennt:
        zahl = getrennt.execute(sa.text("SELECT count(*) FROM domain_shared.agent_autonomy_decisions WHERE "
                                        "tenant_id = :t AND subject_id = :s AND outcome = 'abgelehnt'"),
                                {"t": welt["mandant"], "s": rechnung}).scalar()
    engine.dispose()
    assert zahl == 1


def test_ein_menschlich_freigegebener_vorgang_ist_kein_autonomiefall(welt):
    from app.services.agent_autonomie import menschlich_freigegeben

    gutschrift = _gutschrift(welt, 100)
    with menschlich_freigegeben(gutschrift):
        _direkt_buchen(welt, gutschrift, als=AGENT)  # ohne Politik und Delegation: ein Mensch hat es freigegeben
    assert _status(welt, gutschrift) == "posted"


def test_angezeigte_stufe_und_durchsetzung_stimmen_ueberein(welt):
    from app.services.agent_autonomie import AutonomieVerweigert, vertrauen

    def stufe() -> str:
        return vertrauen(welt["db"], welt["mandant"], AGENT, "sales.gutschrift.buchen")["stufe"]

    def darf() -> bool:
        gutschrift = _gutschrift(welt, 100)
        try:
            with welt["db"].begin_nested():
                _direkt_buchen(welt, gutschrift, als=AGENT)
                raise RuntimeError("zurueck")  # nur pruefen, nicht behalten
        except AutonomieVerweigert:
            return False
        except RuntimeError:
            return True

    assert (stufe(), darf()) == ("A0", False)
    _bereit(welt)
    assert (stufe(), darf()) == ("A2", True)


def test_ein_agent_wird_auch_an_seinem_token_erkannt(monkeypatch):
    from types import SimpleNamespace

    import app.core.identity_context as kontext
    from app.services.agent_autonomie import handelnder_agent

    monkeypatch.setattr(kontext, "current_identity", lambda: SimpleNamespace(claims={"sub": "a-9", "identity_type": "agent"}))
    assert handelnder_agent() == "a-9"
    monkeypatch.setattr(kontext, "current_identity", lambda: SimpleNamespace(claims={"sub": "m-1", "identity_type": "human"}))
    assert handelnder_agent() is None
