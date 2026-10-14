"""Der generische Belegrouter ``/api/mcp/documents`` arbeitet nur im Mandanten der Anmeldung.

Bis 14.10.2026 lasen, aenderten und loeschten GET/PUT/DELETE per Nummer jede Belegart jedes Mandanten — auch
Lieferantengutschriften und Rechnungen, an den abgesicherten Finanzwegen vorbei. Anlegen ueberschrieb einen
fremden Beleg gleicher Nummer und setzte keinen Mandanten. Die Liste las nur den Prozessspeicher.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.documents.router import router
from testgrenze import ersetze_mandant, ersetze_nutzer

WEG = "/api/mcp/documents"


@pytest.fixture
def haus():
    mandant, anderer = f"br-{uuid.uuid4().hex[:8]}", f"br-{uuid.uuid4().hex[:8]}"
    nummern: list[str] = []

    def ablegen(art: str, wo: str | None, **daten) -> str:
        nummer = daten.pop("nummer", None) or f"BR-{uuid.uuid4().hex[:10]}"
        beleg = {"status": "ENTWURF", **daten, "number": nummer}
        if wo is not None:
            beleg["tenantId"] = wo
        with SessionLocal() as db:
            db.execute(text(
                "INSERT INTO documents (id, doc_type, doc_number, data) VALUES (:id, :a, :n, CAST(:d AS jsonb))"),
                {"id": str(uuid.uuid4()), "a": art, "n": nummer, "d": json.dumps(beleg)})
            db.commit()
        nummern.append(nummer)
        return nummer

    def beleg(art: str, nummer: str) -> dict | None:
        with SessionLocal() as db:
            roh = db.execute(text("SELECT data FROM documents WHERE doc_type = :a AND doc_number = :n"),
                             {"a": art, "n": nummer}).scalar()
        return roh if roh is None or isinstance(roh, dict) else json.loads(roh)

    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "SALES_ADMIN")
    client = TestClient(app, raise_server_exceptions=False)

    def als(wo: str) -> TestClient:
        ersetze_mandant(app, wo)
        return client

    yield {"mandant": mandant, "anderer": anderer, "ablegen": ablegen, "beleg": beleg, "als": als,
           "nummern": nummern}
    with SessionLocal() as db:
        db.execute(text("DELETE FROM documents WHERE doc_number = ANY(:n)"), {"n": nummern})
        db.commit()


# ── Lesen ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("art", ["purchase_order", "credit_memo", "sales_invoice"])
def test_ein_fremder_oder_mandantenloser_beleg_ist_nicht_lesbar(haus, art):
    eigen = haus["ablegen"](art, haus["mandant"])
    fremd = haus["ablegen"](art, haus["anderer"])
    alt = haus["ablegen"](art, None)
    c = haus["als"](haus["mandant"])
    assert c.get(f"{WEG}/{art}/{eigen}").json()["data"]["number"] == eigen
    assert c.get(f"{WEG}/{art}/{fremd}").status_code == 404
    assert c.get(f"{WEG}/{art}/{alt}").status_code == 404


def test_die_liste_kommt_aus_der_datenbank_und_nur_aus_dem_eigenen_mandanten(haus):
    eigen = haus["ablegen"]("purchase_order", haus["mandant"])
    fremd = haus["ablegen"]("purchase_order", haus["anderer"])
    alt = haus["ablegen"]("purchase_order", None)
    antwort = haus["als"](haus["mandant"]).get(f"{WEG}/purchase_order", params={"limit": 1000})
    assert antwort.status_code == 200, antwort.text
    gefunden = {d["number"] for d in antwort.json()["data"]}
    assert gefunden == {eigen}
    assert fremd not in gefunden and alt not in gefunden
    assert antwort.json()["total"] == 1


# ── Aendern und Loeschen ──────────────────────────────────────────────────────


def test_ein_fremder_beleg_ist_nicht_aenderbar(haus):
    fremd = haus["ablegen"]("credit_memo", haus["anderer"], totalGross=100)
    antwort = haus["als"](haus["mandant"]).put(f"{WEG}/credit_memo/{fremd}", json={"totalGross": 1})
    assert antwort.status_code == 404
    assert haus["beleg"]("credit_memo", fremd)["totalGross"] == 100


def test_aendern_kann_den_mandanten_nicht_umsetzen(haus):
    eigen = haus["ablegen"]("purchase_order", haus["mandant"], notes="alt")
    antwort = haus["als"](haus["mandant"]).put(
        f"{WEG}/purchase_order/{eigen}", json={"notes": "neu", "tenantId": haus["anderer"]})
    assert antwort.status_code == 200, antwort.text
    gespeichert = haus["beleg"]("purchase_order", eigen)
    assert gespeichert["notes"] == "neu" and gespeichert["tenantId"] == haus["mandant"]


def test_ein_fremder_beleg_ist_nicht_loeschbar(haus):
    fremd = haus["ablegen"]("sales_invoice", haus["anderer"])
    assert haus["als"](haus["mandant"]).delete(f"{WEG}/sales_invoice/{fremd}").status_code == 404
    assert haus["beleg"]("sales_invoice", fremd) is not None


def test_der_eigene_beleg_ist_loeschbar(haus):
    eigen = haus["ablegen"]("sales_invoice", haus["mandant"])
    assert haus["als"](haus["mandant"]).delete(f"{WEG}/sales_invoice/{eigen}").status_code == 200
    assert haus["beleg"]("sales_invoice", eigen) is None


def test_die_sammelloeschung_trifft_nur_eigene_belege(haus):
    eigen = haus["ablegen"]("purchase_order", haus["mandant"])
    fremd = haus["ablegen"]("purchase_order", haus["anderer"])
    antwort = haus["als"](haus["mandant"]).delete(f"{WEG}/purchase_order", params={"numbers": [eigen, fremd]})
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["deleted"] == [eigen]
    assert haus["beleg"]("purchase_order", eigen) is None
    assert haus["beleg"]("purchase_order", fremd) is not None


def test_der_nachhaltigkeitsexport_rechnet_nur_eigene_lieferscheine(haus):
    lieferung = {"date": "2031-03-01", "customerId": "K-1", "totalNutrientNKg": 10.0}
    haus["ablegen"]("sales_delivery", haus["mandant"], **lieferung)
    haus["ablegen"]("sales_delivery", haus["anderer"], **lieferung)
    haus["ablegen"]("sales_delivery", None, **lieferung)
    antwort = haus["als"](haus["mandant"]).get(
        f"{WEG}/analytics/sales-delivery-sustainability/export.csv", params={"year": 2031})
    assert antwort.status_code == 200, antwort.text
    zeilen = dict(z.split(";", 1) for z in antwort.text.lstrip("﻿").splitlines() if ";" in z)
    assert zeilen["Anzahl Lieferscheine"] == "1"
    assert zeilen["Summe N (kg)"] == "10.000"


# ── Anlegen ───────────────────────────────────────────────────────────────────

ANLAGE = {
    "purchase_order": {"date": "2026-10-14", "supplierId": "SUP-1", "status": "ENTWURF"},
    "sales_order": {"date": "2026-10-14", "customerId": "K-1", "status": "ENTWURF"},
    "sales_invoice": {"date": "2026-10-14", "customerId": "K-1", "dueDate": "2026-11-14", "status": "ENTWURF"},
}


@pytest.mark.parametrize("art", sorted(ANLAGE))
def test_ein_neuer_beleg_traegt_den_mandanten(haus, art):
    nummer = f"BR-{uuid.uuid4().hex[:10]}"
    haus["nummern"].append(nummer)
    antwort = haus["als"](haus["mandant"]).post(f"{WEG}/{art}", json={**ANLAGE[art], "number": nummer})
    assert antwort.status_code == 200, antwort.text
    assert haus["beleg"](art, nummer)["tenantId"] == haus["mandant"]


@pytest.mark.parametrize("art", sorted(ANLAGE))
def test_anlegen_ueberschreibt_keinen_fremden_beleg(haus, art):
    fremd = haus["ablegen"](art, haus["anderer"], notes="fremd")
    antwort = haus["als"](haus["mandant"]).post(
        f"{WEG}/{art}", json={**ANLAGE[art], "number": fremd, "notes": "uebernommen"})
    assert antwort.status_code == 409
    gespeichert = haus["beleg"](art, fremd)
    assert gespeichert["notes"] == "fremd" and gespeichert["tenantId"] == haus["anderer"]
