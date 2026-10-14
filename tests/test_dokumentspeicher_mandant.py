"""Der alte Dokumentspeicher liefert Listen nur im Mandanten der Anmeldung.

Bis 14.10.2026 galt ein Mandantenfilter dort als „dieser Mandant oder kein Mandant“; wer ohne Mandant las,
bekam alle Mandanten. Das Kundenportal (Auftraege, Rechnungen, Lieferscheine, Anfragen) und
``/sales/{doc_type}`` lasen ganz ohne Mandant, und der Bestellweg fiel bei leerer eigener Liste auf die
Bestellungen aller Mandanten zurueck.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import compat
from app.core.database import SessionLocal
from app.core.exceptions import EntityNotFoundError, register_domain_exception_handlers
from app.documents import router_helpers
from app.documents.repository import DocumentRepository
from app.services.compat_helpers import list_docs
from app.services.purchase_order_service import PurchaseOrderService
from testgrenze import ersetze_mandant, ersetze_nutzer


@pytest.fixture
def haus():
    mandant, anderer = f"ds-{uuid.uuid4().hex[:8]}", f"ds-{uuid.uuid4().hex[:8]}"
    nummern: list[str] = []

    def ablegen(art: str, wo: str | None, **daten) -> str:
        nummer = f"DS-{uuid.uuid4().hex[:10]}"
        beleg = {**daten, "number": nummer, "id": nummer, "purchaseOrderNumber": nummer}
        if wo is not None:
            beleg["tenantId"] = wo
        with SessionLocal() as db:
            db.execute(text(
                "INSERT INTO documents (id, doc_type, doc_number, data) VALUES (:id, :a, :n, CAST(:d AS jsonb))"),
                {"id": str(uuid.uuid4()), "a": art, "n": nummer, "d": json.dumps(beleg)})
            db.commit()
        nummern.append(nummer)
        return nummer

    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(compat.router)
    ersetze_nutzer(app, "SALES_ADMIN")
    client = TestClient(app, raise_server_exceptions=False)

    def als(wo: str) -> TestClient:
        ersetze_mandant(app, wo)
        return client

    yield {"mandant": mandant, "anderer": anderer, "ablegen": ablegen, "als": als}
    with SessionLocal() as db:
        db.execute(text("DELETE FROM documents WHERE doc_number = ANY(:n)"), {"n": nummern})
        db.commit()


def _nummern(belege) -> set[str]:
    return {str(b.get("number") or b.get("nummer") or b.get("id")) for b in belege}


# ── Speicher ──────────────────────────────────────────────────────────────────


def test_liste_und_zaehlung_enthalten_weder_fremde_noch_mandantenlose_belege(haus):
    eigen = haus["ablegen"]("sales_order", haus["mandant"])
    fremd = haus["ablegen"]("sales_order", haus["anderer"])
    alt = haus["ablegen"]("sales_order", None)
    with SessionLocal() as db:
        repo = DocumentRepository(db)
        filter_ = {"tenantId": haus["mandant"]}
        gefunden = _nummern(repo.list_documents("sales_order", 0, 5000, filter_))
        assert eigen in gefunden
        assert fremd not in gefunden and alt not in gefunden
        assert repo.count_documents("sales_order", filter_) == 1


def test_ohne_mandant_liefert_die_liste_nichts(haus):
    haus["ablegen"]("sales_order", haus["mandant"])
    haus["ablegen"]("sales_order", None)
    with SessionLocal() as db:
        assert list_docs(db, "sales_order", tenant_id=None) == []
        assert list_docs(db, "sales_order", tenant_id="") == []
        assert compat._list_docs(db, "sales_order", tenant_id=None) == []


def test_kein_rueckfall_auf_den_prozessspeicher(haus, monkeypatch):
    """Eine leere Datenbankliste ist die Antwort — nicht, was zufaellig im Prozess liegt."""
    monkeypatch.setitem(router_helpers._DB, "PO-fluechtig", {"number": "PO-fluechtig", "tenantId": haus["mandant"]})
    with SessionLocal() as db:
        assert list_docs(db, "purchase_order", tenant_id=haus["mandant"]) == []


def test_der_prozessspeicher_filtert_ebenfalls_streng(monkeypatch):
    for nummer, wo in (("PO-eigen", "m1"), ("PO-fremd", "m2"), ("PO-alt", None)):
        monkeypatch.setitem(router_helpers._DB, nummer, {"number": nummer, "tenantId": wo})
    ergebnis = router_helpers.list_from_store("purchase_order", filters={"tenantId": "m1"}, repo=None)
    assert {d["number"] for d in ergebnis["data"] if d["number"].startswith("PO-")} == {"PO-eigen"}


# ── Kundenportal ──────────────────────────────────────────────────────────────

PORTAL = [
    ("/portal/bestellungen", "sales_order"),
    ("/portal/rechnungen", "sales_invoice"),
    ("/portal/anfragen", "customer_inquiry"),
    ("/portal/naehrstoffbilanzen", "sales_delivery"),
]


@pytest.mark.parametrize("weg,art", PORTAL)
def test_das_portal_zeigt_nur_belege_des_eigenen_mandanten(haus, weg, art):
    eigen = haus["ablegen"](art, haus["mandant"])
    fremd = haus["ablegen"](art, haus["anderer"])
    alt = haus["ablegen"](art, None)
    antwort = haus["als"](haus["mandant"]).get(weg)
    assert antwort.status_code == 200, antwort.text
    gefunden = _nummern(antwort.json())
    assert eigen in gefunden
    assert fremd not in gefunden and alt not in gefunden


def test_das_portal_dashboard_zaehlt_nur_eigene_belege(haus):
    haus["ablegen"]("sales_order", haus["mandant"])
    haus["ablegen"]("sales_order", haus["anderer"])
    antwort = haus["als"](haus["mandant"]).get("/portal/dashboard")
    assert antwort.status_code == 200, antwort.text
    kennzahlen = {k["label"]: k["value"] for k in antwort.json()["kpis"]}
    assert kennzahlen["Bestellungen"] == "1"


# ── Verkaufsbruecke ───────────────────────────────────────────────────────────


def test_die_verkaufsbruecke_liefert_nur_den_eigenen_mandanten(haus):
    eigen = haus["ablegen"]("sales_invoice", haus["mandant"])
    fremd = haus["ablegen"]("sales_invoice", haus["anderer"])
    alt = haus["ablegen"]("sales_invoice", None)
    antwort = haus["als"](haus["mandant"]).get("/sales/rechnungen")
    assert antwort.status_code == 200, antwort.text
    gefunden = _nummern(antwort.json()["data"])
    assert eigen in gefunden
    assert fremd not in gefunden and alt not in gefunden


# ── Bestellungen ──────────────────────────────────────────────────────────────


def test_ohne_eigene_bestellungen_kommen_keine_fremden(haus):
    fremd = haus["ablegen"]("purchase_order", haus["anderer"])
    with SessionLocal() as db:
        dienst = PurchaseOrderService(db, haus["mandant"])
        assert dienst.list_purchase_orders(page_size=5000)["data"] == []
        with pytest.raises(EntityNotFoundError):
            dienst.get_purchase_order(fremd)
