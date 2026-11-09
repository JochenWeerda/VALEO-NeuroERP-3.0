"""Belegliste aus DocFlow (Familie ``beleg-liste``, BELEG-052: DocFlow ist der einzige Belegspeicher).

Die Beleglisten lasen bis 08.11.2026 die Eigenspeicher (``/sales/invoices``, ``/einkauf/bestellungen``,
``/finance/ap/invoices`` …); deren Zeilen oeffneten teils ``/belege/purchase_invoice/{id}`` mit Kennungen, die
DocFlow nicht kennt. Jetzt liest jede Liste ``GET /belege/{belegart}``: dieselben Belege wie die Belegmaske,
dieselben Rechte, Betraege nur mit Preisrecht. Geprueft an den Referenzbelegen eines eigenen Mandanten.
"""
from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import belege as belege_endpunkt
from app.core.database import SessionLocal
from app.services import docflow_service
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = pytest.mark.integration

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(scope="module")
def satz():
    from test_belege_lesen import AUFRAEUMEN

    mandant = f"bli-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "Belegliste Test")
        db.commit()
        angelegt = _modul("referenzbelege_anlegen").lege_an(db, mandant)
    yield {"mandant": mandant, "belege": angelegt}
    patch.undo()
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


@pytest.fixture(scope="module")
def app_und_client(satz):
    app = FastAPI()
    app.include_router(belege_endpunkt.router, prefix="/belege")
    ersetze_mandant(app, satz["mandant"])
    return app, TestClient(app)


def _liste(app_und_client, satz, belegart: str, *rollen: str, mandant: str | None = None):
    app, client = app_und_client
    ersetze_nutzer(app, *rollen)
    return client.get(f"/belege/{belegart}", headers={"X-Tenant-ID": mandant or satz["mandant"]})


def test_liste_zeigt_genau_die_docflow_belege_der_belegart(app_und_client, satz):
    erwartet = {b["id"] for b in satz["belege"] if b["doc_type"] == "sales_invoice"}
    assert erwartet, "Referenzbelege ohne Ausgangsrechnung"
    antwort = _liste(app_und_client, satz, "sales_invoice", "admin")
    assert antwort.status_code == 200, antwort.text
    zeilen = antwort.json()["items"]
    assert {z["id"] for z in zeilen} == erwartet
    assert all(z["belegart"] == "sales_invoice" and z["id"] == z["beleg_id"] for z in zeilen)
    assert all(z["brutto"] is not None and z["waehrung"] for z in zeilen)


def test_ohne_preisrecht_keine_betraege(app_und_client, satz):
    antwort = _liste(app_und_client, satz, "sales_invoice", "LAGER_LESEN")
    assert antwort.status_code == 200, antwort.text
    zeilen = antwort.json()["items"]
    assert zeilen and all(z["netto"] is None and z["brutto"] is None and z["waehrung"] is None for z in zeilen)


def test_ohne_leserecht_keine_liste(app_und_client, satz):
    assert _liste(app_und_client, satz, "purchase_order", "SALES_LESEN").status_code == 403


def test_mengenbelege_tragen_nie_betraege(app_und_client, satz):
    zeilen = _liste(app_und_client, satz, "sales_delivery", "admin").json()["items"]
    assert all(z["brutto"] is None for z in zeilen)


def test_fremder_mandant_sieht_nichts(satz):
    fremd = FastAPI()
    fremd.include_router(belege_endpunkt.router, prefix="/belege")
    ersetze_mandant(fremd, f"leer-{uuid.uuid4().hex[:6]}")
    ersetze_nutzer(fremd, "admin")
    antwort = TestClient(fremd).get("/belege/sales_invoice")
    assert antwort.status_code == 200 and antwort.json()["items"] == []


def test_unbekannte_belegart(app_und_client, satz):
    assert _liste(app_und_client, satz, "lieferavis", "admin").status_code == 404


def test_mcp_suche_liest_dieselbe_quelle(satz):
    from types import SimpleNamespace

    from app.services.mcp_beleg_tools import beleg_suchen

    with SessionLocal() as db:
        anfrage = SimpleNamespace(mode="execute", tool_name="beleg.suchen",
                                  parameters={"belegart": "sales_invoice", "limit": 50})
        ergebnis = beleg_suchen(db, anfrage, "agent", satz["mandant"], {"roles": ["admin"]})
    erwartet = {b["id"] for b in satz["belege"] if b["doc_type"] == "sales_invoice"}
    assert {z["beleg_id"] for z in ergebnis["items"]} == erwartet


# ── Belegdruck (BELEG-052 Stufe 2b) ────────────────────────────────────────────

def test_belegdruck_liefert_ein_pdf_des_belegs(app_und_client, satz):
    import base64

    beleg = next(b for b in satz["belege"] if b["doc_type"] == "sales_invoice")
    app, client = app_und_client
    ersetze_nutzer(app, "admin")
    antwort = client.get(f"/belege/sales_invoice/{beleg['id']}/druck")
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["dateiname"].startswith("sales_invoice_") and daten["dateiname"].endswith(".pdf")
    assert base64.b64decode(daten["pdf"]).startswith(b"%PDF")


def test_belegdruck_braucht_das_leserecht(app_und_client, satz):
    beleg = next(b for b in satz["belege"] if b["doc_type"] == "purchase_order")
    app, client = app_und_client
    ersetze_nutzer(app, "SALES_LESEN")
    assert client.get(f"/belege/purchase_order/{beleg['id']}/druck").status_code == 403


def test_jede_belegvariante_kann_drucken():
    from app.core.belegvertrag import BELEGARTEN
    from app.core.screen_definitions import get_screen_definition

    for art in BELEGARTEN:
        definition = get_screen_definition(f"beleg/{art.replace('_', '-')}", tenant_id="t-druck")
        aktion = next(a for a in definition["actions"] if a["key"] == "drucken")
        assert aktion["download"]["endpoint"] == f"/api/v1/belege/{art}/{{entity_id}}/druck"
        assert aktion["download"]["mediaType"] == "application/pdf"


# ── Beleg versenden (BELEG-052 Stufe 2b) ───────────────────────────────────────

@pytest.fixture()
def versand_app(satz, monkeypatch):
    from app.api.v1.endpoints import beleg_versand
    from app.services import mail_versand

    gesendet: list[tuple] = []
    monkeypatch.setattr(mail_versand, "sende_mail",
                        lambda empf, betreff, text_, **kw: gesendet.append((empf, betreff, kw)) or "<id@test>")
    app = FastAPI()
    app.include_router(beleg_versand.router)
    ersetze_mandant(app, satz["mandant"])
    ersetze_nutzer(app, "admin")
    return TestClient(app), gesendet


def test_versand_schickt_das_pdf_an_den_empfaenger(versand_app, satz):
    client, gesendet = versand_app
    beleg = next(b for b in satz["belege"] if b["doc_type"] == "sales_invoice"
                 and b["rolle"] not in ("vk-rechnung-storno",))
    antwort = client.post(f"/belege/sales_invoice/{beleg['id']}/actions/versenden",
                          json={"empfaenger": "buchhaltung@hof.example", "_idempotencyKey": str(uuid.uuid4())}).json()
    if not antwort["success"] and "Stand" in (antwort.get("error") or ""):
        pytest.skip(f"Referenzbeleg nicht versendbar: {antwort['error']}")
    assert antwort["success"] is True, antwort
    empfaenger, betreff, kw = gesendet[-1]
    assert empfaenger == "buchhaltung@hof.example" and betreff.startswith("Rechnung")
    assert kw["verwendung"] == "verkauf" and kw["anhaenge"][0][1].startswith(b"%PDF")


def test_trockenlauf_versendet_nichts(versand_app, satz):
    client, gesendet = versand_app
    beleg = next(b for b in satz["belege"] if b["doc_type"] == "purchase_order")
    vorher = len(gesendet)
    client.post(f"/belege/purchase_order/{beleg['id']}/actions/versenden",
                json={"_mode": "dryRun", "empfaenger": "einkauf@lieferant.example"})
    assert len(gesendet) == vorher


def test_ohne_adresse_kein_versand(versand_app, satz):
    client, gesendet = versand_app
    beleg = next(b for b in satz["belege"] if b["doc_type"] == "sales_offer")
    antwort = client.post(f"/belege/sales_offer/{beleg['id']}/actions/versenden", json={}).json()
    assert antwort["success"] is False
