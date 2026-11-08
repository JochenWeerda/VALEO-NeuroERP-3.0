"""Der generische Belegrouter schreibt nur die Belegarten, die allein ueber ihn gefuehrt werden.

Nutzerentscheidung 14.10.2026: Finanzbelege laufen ausschliesslich ueber ihre Fachwege mit Rollenpruefung. Bis dahin
konnte jede angemeldete Person des Mandanten ueber ``/api/mcp/documents`` eigene Rechnungen, Gutschriften und
Zahlungseingaenge anlegen, aendern und loeschen — an der Rollenpruefung der Fachwege vorbei.

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
from app.documents.router import ROUTER_BELEGARTEN, router
from testgrenze import ersetze_mandant, ersetze_nutzer

WEG = "/api/mcp/documents"
FINANZBELEGE = ["sales_invoice", "ap_invoice", "payment_received", "credit_memo", "debit_memo"]


@pytest.fixture
def haus():
    mandant = f"bro-{uuid.uuid4().hex[:8]}"
    nummern: list[str] = []

    def ablegen(art: str, **daten) -> str:
        nummer = f"BRO-{uuid.uuid4().hex[:10]}"
        beleg = {"status": "ENTWURF", "notes": "vorher", **daten, "number": nummer, "tenantId": mandant}
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
    ersetze_mandant(app, mandant)
    yield {"client": TestClient(app, raise_server_exceptions=False), "ablegen": ablegen, "beleg": beleg,
           "nummern": nummern}
    with SessionLocal() as db:
        db.execute(text("DELETE FROM documents WHERE doc_number = ANY(:n)"), {"n": nummern})
        db.commit()


def test_finanzbelege_gehoeren_nicht_zum_router():
    assert not ROUTER_BELEGARTEN & set(FINANZBELEGE)


@pytest.mark.parametrize("art", FINANZBELEGE)
def test_ein_eigener_finanzbeleg_ist_hier_nicht_aenderbar(haus, art):
    nummer = haus["ablegen"](art)
    antwort = haus["client"].put(f"{WEG}/{art}/{nummer}", json={"notes": "nachher", "status": "BEZAHLT"})
    assert antwort.status_code == 403
    assert haus["beleg"](art, nummer)["notes"] == "vorher"


@pytest.mark.parametrize("art", FINANZBELEGE)
def test_ein_eigener_finanzbeleg_ist_hier_nicht_loeschbar(haus, art):
    nummer = haus["ablegen"](art)
    assert haus["client"].delete(f"{WEG}/{art}/{nummer}").status_code == 403
    assert haus["client"].delete(f"{WEG}/{art}", params={"numbers": [nummer]}).status_code == 403
    assert haus["beleg"](art, nummer) is not None


def test_rechnung_und_zahlungseingang_entstehen_hier_nicht(haus):
    rechnung, zahlung = f"BRO-{uuid.uuid4().hex[:10]}", f"BRO-{uuid.uuid4().hex[:10]}"
    haus["nummern"].extend([rechnung, zahlung])
    c = haus["client"]
    assert c.post(f"{WEG}/sales_invoice", json={
        "number": rechnung, "date": "2026-10-14", "customerId": "K-1", "dueDate": "2026-11-14"}).status_code == 403
    assert c.post(f"{WEG}/payment_received", json={
        "number": zahlung, "date": "2026-10-14", "salesInvoiceId": "R-1", "amount": 10,
        "paymentMethod": "Ueberweisung"}).status_code == 403
    assert haus["beleg"]("sales_invoice", rechnung) is None
    assert haus["beleg"]("payment_received", zahlung) is None


@pytest.mark.parametrize("art", sorted(ROUTER_BELEGARTEN))
def test_die_belegarten_des_routers_bleiben_aenderbar(haus, art):
    nummer = haus["ablegen"](art)
    antwort = haus["client"].put(f"{WEG}/{art}/{nummer}", json={"notes": "nachher"})
    assert antwort.status_code == 200, antwort.text
    assert haus["beleg"](art, nummer)["notes"] == "nachher"
