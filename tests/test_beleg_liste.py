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
