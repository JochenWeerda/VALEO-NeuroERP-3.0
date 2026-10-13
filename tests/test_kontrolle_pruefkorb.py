"""Pruefkorb des Controllers: Arbeitsliste, Lagebild und Maske (FIN-CONTROL-002).

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import docflow, kontrolle
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.core.screen_definitions import get_screen_definition
from app.core.screen_governance import governance_errors, ux_lint
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from testgrenze import ersetze_mandant

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["FINANCE_ADMIN", "SALES_BEARBEITEN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CARL = {"sub": "carl", "name": "c.boekhoff", "roles": ["controller"]}
LAGER = {"sub": "lars", "name": "l.janssen", "roles": ["LAGER_ADMIN"]}

AUFRAEUMEN = (
    "DELETE FROM domain_docflow.control_findings WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
    "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


def _befund(mandant: str, code: str, schwere: str, *, wer: str = "bernd", betrag: str | None = "100.00",
            subjekt: str = "journal_entry", subjekt_id: str | None = None, vor_tagen: int = 0,
            freigabe: str | None = None) -> str:
    kennung = str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_docflow.control_findings (id, tenant_id, subject_type, subject_id, action, code, severity, "
            "text, amount, actor, approval_id, created_at) VALUES (:id, :t, :s, :sid, 'post', :c, :sev, :txt, :b, :wer, "
            ":f, clock_timestamp() - make_interval(days => :tage))"),
            {"id": kennung, "t": mandant, "s": subjekt, "sid": subjekt_id or str(uuid.uuid4()), "c": code, "sev": schwere,
             "txt": f"Hinweis zu {code}", "b": betrag, "wer": wer, "f": freigabe, "tage": vor_tagen})
        db.commit()
    return kennung


@pytest.fixture
def haus(monkeypatch):
    mandant, anderer = f"pk-{uuid.uuid4().hex[:8]}", f"pk-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        for m in (mandant, anderer):
            db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": m})
        richte_skr03_ein(db, mandant)
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(kontrolle.router, prefix="/kontrolle")
    app.include_router(docflow.router, prefix="/docflow")
    ersetze_mandant(app, mandant)
    client = TestClient(app, raise_server_exceptions=False)

    def als(nutzer: dict) -> TestClient:
        app.dependency_overrides[get_current_user] = lambda: nutzer
        return client

    yield {"mandant": mandant, "anderer": anderer, "als": als, "app": app}
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for m in (mandant, anderer):
            for sql in AUFRAEUMEN:
                db.execute(text(sql), {"t": m})
        db.commit()


def _liste(haus, wer: dict = CARL, **params) -> dict:
    antwort = haus["als"](wer).get("/kontrolle/pruefkorb", params=params)
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


# ── Arbeitsliste ──────────────────────────────────────────────────────────────

def test_der_korb_zeigt_offene_befunde_kritische_zuerst_und_die_aeltesten_davor(haus):
    m = haus["mandant"]
    neu = _befund(m, "betrag", "warnung")
    alt = _befund(m, "massenimport", "warnung", vor_tagen=9)
    kritisch = _befund(m, "dublette", "kritisch", freigabe=str(uuid.uuid4()))
    _befund(haus["anderer"], "dublette", "kritisch")                      # fremder Mandant
    seite = _liste(haus)
    assert [z["id"] for z in seite["items"]] == [kritisch, alt, neu]
    assert (seite["total"], seite["page"], seite["page_size"]) == (3, 1, 50)
    erste = seite["items"][0]
    # Bezeichnungen statt interner Schluessel.
    assert (erste["art"], erste["schwere_text"], erste["vorgang"], erste["aktion"]) == (
        "Mögliche Dublette", "Kritisch", "Hauptbuchbuchung", "Buchen")
    assert erste["freigegeben"] is True and erste["status"] == "offen" and erste["source_route"] is None
    assert seite["items"][1]["alter_tage"] == 9


def test_blaettern_suchen_sortieren_und_filtern(haus):
    m = haus["mandant"]
    for nummer in range(5):
        _befund(m, "betrag", "warnung", betrag=f"{nummer + 1}000.00", wer="bernd" if nummer % 2 else "anna")
    kritisch = _befund(m, "geschuetztes_konto", "kritisch", betrag="50.00")
    zweite = _liste(haus, page=2, limit=4)
    assert zweite["total"] == 6 and len(zweite["items"]) == 2 and zweite["page"] == 2
    teuer = _liste(haus, sort="betrag", sort_dir="desc")["items"]
    assert [float(z["betrag"]) for z in teuer][:2] == [5000.0, 4000.0]
    # Eine unbekannte Sortierspalte faellt auf die Vorgabe zurueck, statt in die Abfrage zu gelangen.
    assert _liste(haus, sort="id; DROP TABLE x")["items"][0]["id"] == kritisch
    assert [z["id"] for z in _liste(haus, q="geschützt")["items"]] == [kritisch]
    assert _liste(haus, q="anna")["total"] == 3
    nach = lambda **plan: _liste(haus, filter_plan=json.dumps(plan))  # noqa: E731
    assert nach(schwere={"op": "eq", "value": "kritisch"})["total"] == 1
    assert nach(art={"op": "contains", "value": "Schwelle"})["total"] == 5
    assert nach(ausgeloest_von={"op": "contains", "value": "bern"})["total"] == 3   # zwei Warnungen und der kritische
    assert haus["als"](CARL).get("/kontrolle/pruefkorb", params={"filter_plan": "{kaputt"}).status_code == 422


def test_gepruefte_befunde_verlassen_die_liste_und_bleiben_auffindbar(haus):
    befund = _befund(haus["mandant"], "betrag", "warnung")
    antwort = haus["als"](CARL).post(f"/kontrolle/befunde/{befund}/pruefung", json={"note": "Jahresbonus, belegt"})
    assert antwort.status_code == 200, antwort.text
    assert _liste(haus)["total"] == 0
    geprueft = _liste(haus, filter_plan=json.dumps({"status": {"op": "eq", "value": "geprueft"}}))["items"]
    assert [(z["status_text"], z["geprueft_von"], z["bewertung"]) for z in geprueft] == [("Geprüft", "carl", "Jahresbonus, belegt")]
    assert _liste(haus, filter_plan=json.dumps({"status": {"op": "eq", "value": "alle"}}))["total"] == 1


def test_ein_befund_am_beleg_nennt_belegart_und_nummer_und_fuehrt_zum_beleg(haus):
    nummer = f"PK-{uuid.uuid4().hex[:8]}"
    beleg = haus["als"](ANNA).post("/docflow/", json={
        "doc_type": "sales_invoice", "doc_number": nummer, "status": "open", "customer_id": "kunde-1",
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 100, "tax_code": "3"}]})
    assert beleg.status_code == 200, beleg.text
    kennung = beleg.json()["id"]
    _befund(haus["mandant"], "betrag", "warnung", subjekt="docflow_document", subjekt_id=kennung)
    zeile = _liste(haus)["items"][0]
    assert (zeile["vorgang"], zeile["beleg"], zeile["source_route"]) == ("Rechnung", nummer, f"/belege/sales_invoice/{kennung}")
    assert _liste(haus, q=nummer)["total"] == 1


def test_den_korb_liest_wer_mit_finanzen_oder_kontrolle_betraut_ist(haus):
    _befund(haus["mandant"], "betrag", "warnung")
    for weg in ("/kontrolle/pruefkorb", "/kontrolle/lagebild"):
        assert haus["als"](LAGER).get(weg).status_code == 403
        assert haus["als"](BERND).get(weg).status_code == 200      # die Buchhaltung sieht, was an ihren Vorgaengen auffiel
    ersetze_mandant(haus["app"], haus["anderer"])
    try:
        assert _liste(haus)["total"] == 0 and haus["als"](CARL).get("/kontrolle/lagebild").json()["offen"] == 0
    finally:
        ersetze_mandant(haus["app"], haus["mandant"])


# ── Lagebild ──────────────────────────────────────────────────────────────────

def test_ein_leerer_korb_meldet_keine_auffaelligkeiten(haus):
    lage = haus["als"](CARL).get("/kontrolle/lagebild").json()
    assert (lage["offen"], lage["kritisch_offen"], lage["wartend"], lage["hinweise"]) == (0, 0, 0, [])
    assert lage["lage"] == "Keine offenen Auffälligkeiten."


def test_das_lagebild_sagt_worauf_der_controller_zuerst_sehen_sollte(haus):
    m = haus["mandant"]
    _befund(m, "dublette", "kritisch", wer="anna", betrag="900.00", freigabe=str(uuid.uuid4()))
    _befund(m, "betrag", "warnung", betrag="12000.00", vor_tagen=10)
    _befund(m, "betrag", "warnung", betrag="11000.00", vor_tagen=8)
    erledigt = _befund(m, "storno_haeufung", "warnung", betrag=None)
    assert haus["als"](CARL).post(f"/kontrolle/befunde/{erledigt}/pruefung", json={"note": "Umstellung der Tour"}).status_code == 200
    _befund(haus["anderer"], "dublette", "kritisch")
    lage = haus["als"](CARL).get("/kontrolle/lagebild").json()
    assert (lage["offen"], lage["kritisch_offen"], lage["warnung_offen"], lage["wartend"], lage["geprueft_30_tage"]) == (3, 1, 2, 2, 1)
    assert float(lage["betrag_offen"]) == 23900.0
    assert lage["nach_art"] == [{"art": "Betrag über der Schwelle", "anzahl": 2}, {"art": "Mögliche Dublette", "anzahl": 1}]
    # Drei Befunde in 30 Tagen bei derselben Person (auch der schon gepruefte zaehlt): eine Haeufung.
    assert lage["haeufungen"] == [{"ausgeloest_von": "bernd", "anzahl": 3}]
    assert lage["hinweise"] == [
        "1 kritischer Befund wurde freigegeben und ist noch nicht bewertet.",
        "2 Befunde warten seit mehr als 7 Tagen.",
        "3 Befunde in 30 Tagen bei bernd.",
        "Häufigste Art: Betrag über der Schwelle (2).",
    ]
    assert lage["lage"] == " ".join(lage["hinweise"])


# ── Maske ─────────────────────────────────────────────────────────────────────

def test_die_maske_ist_eine_arbeitsliste_ohne_interne_schluessel():
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness

    definition = get_screen_definition("finance/pruefkorb")
    assert definition is not None and definition["adapter"] == {"type": "native", "sourceId": "finance/pruefkorb", "temporary": False}
    assert definition["layout"]["floorplan"] == "worklist"
    assert governance_errors(definition) == [] and list(ux_lint(definition)) == []
    assert _check_readiness(definition)["generatorReady"] is True
    tabelle = definition["tables"][0]
    assert tabelle["serverPagination"] is True and tabelle["rowRouteTemplate"] == "{source_route}"
    spalten = {s["key"] for s in tabelle["columns"]}
    assert not spalten & {"code", "subject_type", "subject_id", "severity", "approval_id"}
    bewerten = next(a for a in tabelle["rowActions"] if a["key"] == "pruefen")
    assert bewerten["visibleWhen"] == {"field": "status", "values": ["offen"]}


def test_was_die_maske_zeigt_liefert_der_server(haus):
    """Jede Spalte und jede Kennzahl der Definition hat ein Feld in der Antwort — sonst bliebe sie still leer."""
    _befund(haus["mandant"], "betrag", "warnung")
    definition = get_screen_definition("finance/pruefkorb")
    zeile = _liste(haus)["items"][0]
    assert {s["key"] for s in definition["tables"][0]["columns"]} <= set(zeile)
    lage = haus["als"](CARL).get("/kontrolle/lagebild").json()
    assert {k["key"] for k in definition["summary"]} <= set(lage)
    wege = {q["key"]: q["endpoint"] for q in definition["dataSources"]}
    assert wege == {"entity": "/api/v1/kontrolle/lagebild", "befunde": "/api/v1/kontrolle/pruefkorb"}
