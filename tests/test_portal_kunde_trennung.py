"""Kundentrennung im Portal (TENANT-DOC-001): das Kundenkonto kommt nur aus Anmeldung und gepruefter Zuordnung.

Bis 14.10.2026 sah jede angemeldete Person ueber ``/api/v1/portal/*`` die Belege aller Kunden des Mandanten;
``/portal/feldbuch`` nahm den Kunden aus dem Parameter ``customer_id``. Mandant und Kunde sind zwei Grenzen und
werden hier getrennt geprueft: fremder Kunde im selben Mandanten, gleicher Kunde im fremden Mandanten, manipulierter
Kopf und Parameter, widerrufene und mandantenfremde Zuordnung, Anmeldung ohne Zuordnung und ohne Rolle.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.api.v1.endpoints.compat import router as compat_router
from app.api.v1.endpoints.portal_kundenzugaenge import router as zugang_router
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.tenant import get_tenant_id


def _id(praefix: str) -> str:
    return f"{praefix}-{uuid.uuid4().hex[:10]}"


@pytest.fixture
def welt():
    """Zwei Mandanten; in A die Kunden K1 und K2, in B ein Kunde mit derselben ID wie K1."""
    a, b = _id("pk-a"), _id("pk-b")
    k1, k2 = _id("K1"), _id("K2")
    belege: list[str] = []
    with SessionLocal() as db:
        for t in (a, b):
            db.execute(text("INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:i, :i, :i, TRUE)"),
                       {"i": t})
        for t, k in ((a, k1), (a, k2), (b, k1)):
            # Die Kundennummer ist systemweit eindeutig (customers_customer_number_key), daher je Mandant eine eigene.
            db.execute(text("INSERT INTO domain_crm.customers (id, customer_number, company_name, tenant_id) "
                            "VALUES (:k || ':' || :t, :k || ':' || :t, :k, :t)"), {"k": k, "t": t})
        db.commit()

    def kid(t: str, k: str) -> str:
        return f"{k}:{t}"

    def beleg(art: str, t: str, kunde: str, **daten) -> str:
        nummer = _id("PKB")
        inhalt = {"number": nummer, "tenantId": t, "customerId": kunde, "date": "2026-10-14", "status": "offen",
                  **daten}
        with SessionLocal() as db:
            db.execute(text(
                "INSERT INTO documents (id, doc_type, doc_number, data) VALUES (:id, :a, :n, CAST(:d AS jsonb))"),
                {"id": str(uuid.uuid4()), "a": art, "n": nummer, "d": json.dumps(inhalt)})
            db.commit()
        belege.append(nummer)
        return nummer

    def zuordnen(t: str, subject: str, kunde: str, widerrufen: bool = False, rolle: str = "inhaber") -> None:
        with SessionLocal() as db:
            db.execute(text(
                "INSERT INTO domain_portal.kundenzugaenge (id, tenant_id, subject, customer_id, rolle, angelegt_von, "
                "widerrufen_von, widerrufen_am) VALUES (:id, :t, :s, :c, :r, 'test', :wv, :wa)"),
                {"id": str(uuid.uuid4()), "t": t, "s": subject, "c": kunde, "r": rolle,
                 "wv": "test" if widerrufen else None, "wa": "2026-10-14" if widerrufen else None})
            db.commit()

    app = FastAPI()
    app.include_router(compat_router, prefix="/api/v1")
    app.include_router(zugang_router, prefix="/api/v1")
    client = TestClient(app, raise_server_exceptions=False)

    def als(t: str, subject: str, *rollen: str) -> TestClient:
        app.dependency_overrides[get_tenant_id] = lambda: t
        app.dependency_overrides[get_current_user] = lambda: {"sub": subject, "name": subject, "roles": list(rollen)}
        return client

    yield {"a": a, "b": b, "k1": kid(a, k1), "k2": kid(a, k2), "k1b": kid(b, k1), "beleg": beleg,
           "zuordnen": zuordnen, "als": als}
    with SessionLocal() as db:
        db.execute(text("DELETE FROM documents WHERE doc_number = ANY(:n)"), {"n": belege})
        db.execute(text("DELETE FROM domain_crm.customers WHERE tenant_id IN (:a, :b)"), {"a": a, "b": b})
        db.execute(text("DELETE FROM domain_shared.tenants WHERE id IN (:a, :b)"), {"a": a, "b": b})
        db.commit()


def _nummern(antwort) -> set[str]:
    assert antwort.status_code == 200, antwort.text
    return {z["nummer"] for z in antwort.json()}


# ── Kundengrenze ──────────────────────────────────────────────────────────────


def test_ein_portalkunde_sieht_nur_die_belege_seines_kontos(welt):
    eigen = welt["beleg"]("sales_invoice", welt["a"], welt["k1"])
    nachbar = welt["beleg"]("sales_invoice", welt["a"], welt["k2"])
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    c = welt["als"](welt["a"], "hof-1")
    assert _nummern(c.get("/api/v1/portal/rechnungen")) == {eigen}
    assert nachbar not in _nummern(c.get("/api/v1/portal/rechnungen"))


@pytest.mark.parametrize("weg", ["anfragen", "bestellungen", "rechnungen"])
def test_jede_belegliste_ist_kundenbezogen(welt, weg):
    art = {"anfragen": "customer_inquiry", "bestellungen": "sales_order", "rechnungen": "sales_invoice"}[weg]
    eigen = welt["beleg"](art, welt["a"], welt["k1"])
    welt["beleg"](art, welt["a"], welt["k2"])
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    assert _nummern(welt["als"](welt["a"], "hof-1").get(f"/api/v1/portal/{weg}")) == {eigen}


def test_ein_fremdes_konto_im_kopf_ist_verboten(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    antwort = welt["als"](welt["a"], "hof-1").get("/api/v1/portal/rechnungen", headers={"X-Kundenkonto": welt["k2"]})
    assert antwort.status_code == 403


def test_ein_kunde_im_parameter_zaehlt_nicht(welt):
    eigen = welt["beleg"]("sales_delivery", welt["a"], welt["k1"])
    fremd = welt["beleg"]("sales_delivery", welt["a"], welt["k2"])
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    antwort = welt["als"](welt["a"], "hof-1").get("/api/v1/portal/feldbuch", params={"customer_id": welt["k2"]})
    assert antwort.status_code == 200, antwort.text
    gefunden = {z["id"] for z in antwort.json()}
    assert eigen in gefunden and fremd not in gefunden


def test_mehrere_konten_verlangen_eine_auswahl_aus_der_zugeordneten_menge(welt):
    r1 = welt["beleg"]("sales_invoice", welt["a"], welt["k1"])
    r2 = welt["beleg"]("sales_invoice", welt["a"], welt["k2"])
    welt["zuordnen"](welt["a"], "gemeinschaft", welt["k1"])
    welt["zuordnen"](welt["a"], "gemeinschaft", welt["k2"], rolle="berater")
    c = welt["als"](welt["a"], "gemeinschaft")
    assert c.get("/api/v1/portal/rechnungen").status_code == 409
    assert _nummern(c.get("/api/v1/portal/rechnungen", headers={"X-Kundenkonto": welt["k1"]})) == {r1}
    assert _nummern(c.get("/api/v1/portal/rechnungen", headers={"X-Kundenkonto": welt["k2"]})) == {r2}
    konten = {k["customer_id"]: k["rolle"] for k in c.get("/api/v1/portal/kundenkonten").json()}
    assert konten == {welt["k1"]: "inhaber", welt["k2"]: "berater"}


def test_eine_widerrufene_zuordnung_gibt_keinen_zugang(welt):
    welt["beleg"]("sales_invoice", welt["a"], welt["k1"])
    welt["zuordnen"](welt["a"], "hof-alt", welt["k1"], widerrufen=True)
    assert welt["als"](welt["a"], "hof-alt").get("/api/v1/portal/rechnungen").status_code == 403


def test_ohne_zuordnung_und_ohne_rolle_kein_zugang(welt):
    c = welt["als"](welt["a"], "irgendwer", "user")
    for weg in ("dashboard", "rechnungen", "bestellungen", "feldbuch", "shop"):
        assert c.get(f"/api/v1/portal/{weg}").status_code == 403, weg


# ── Mandantengrenze ───────────────────────────────────────────────────────────


def test_eine_zuordnung_gilt_nur_in_ihrem_mandanten(welt):
    welt["zuordnen"](welt["b"], "hof-b", welt["k1b"])
    assert welt["als"](welt["a"], "hof-b").get("/api/v1/portal/rechnungen").status_code == 403


def test_derselbe_kunde_im_fremden_mandanten_bleibt_fremd(welt):
    """Ein Beleg in B mit genau der Kunden-ID aus A (etwa eine Altnummer) erscheint in A nicht."""
    eigen = welt["beleg"]("sales_invoice", welt["a"], welt["k1"])
    fremd = welt["beleg"]("sales_invoice", welt["b"], welt["k1"])
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    assert _nummern(welt["als"](welt["a"], "hof-1").get("/api/v1/portal/rechnungen")) == {eigen}
    assert fremd


def test_ein_konto_eines_fremden_mandanten_ist_nicht_zuordenbar(welt):
    c = welt["als"](welt["a"], "leitung", "CRM_ADMIN")
    antwort = c.post("/api/v1/portal/kundenzugaenge",
                     json={"subject": "hof-x", "customer_id": welt["k1b"], "rolle": "inhaber"})
    assert antwort.status_code == 404


# ── Interne Betreuung ─────────────────────────────────────────────────────────


def test_die_interne_betreuung_waehlt_einen_kunden_des_mandanten(welt):
    eigen = welt["beleg"]("sales_order", welt["a"], welt["k2"])
    c = welt["als"](welt["a"], "innendienst", "SALES_LESEN")
    assert c.get("/api/v1/portal/bestellungen").status_code == 400
    assert _nummern(c.get("/api/v1/portal/bestellungen", headers={"X-Kundenkonto": welt["k2"]})) == {eigen}
    assert c.get("/api/v1/portal/bestellungen", headers={"X-Kundenkonto": welt["k1b"]}).status_code == 404


def test_unterlagen_ohne_kundenbezug_erscheinen_nicht(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    c = welt["als"](welt["a"], "hof-1")
    for weg in ("dokumente", "vertraege", "zertifikate"):
        antwort = c.get(f"/api/v1/portal/{weg}")
        assert antwort.status_code == 200 and antwort.json() == [], weg


# ── Verwaltung der Zuordnungen ────────────────────────────────────────────────


def test_zuordnen_und_widerrufen_nur_mit_leitungsrolle(welt):
    neu = {"subject": "hof-neu", "customer_id": welt["k1"], "rolle": "buchhaltung"}
    assert welt["als"](welt["a"], "innendienst", "SALES_BEARBEITEN").post(
        "/api/v1/portal/kundenzugaenge", json=neu).status_code == 403
    c = welt["als"](welt["a"], "leitung", "SALES_ADMIN")
    angelegt = c.post("/api/v1/portal/kundenzugaenge", json=neu)
    assert angelegt.status_code == 201, angelegt.text
    assert angelegt.json()["angelegt_von"] == "leitung" and angelegt.json()["rolle"] == "buchhaltung"
    assert c.post("/api/v1/portal/kundenzugaenge", json={**neu, "rolle": "chef"}).status_code == 422
    assert c.post("/api/v1/portal/kundenzugaenge", json=neu).status_code == 409
    zid = angelegt.json()["id"]
    assert welt["als"](welt["b"], "leitung-b", "SALES_ADMIN").post(
        f"/api/v1/portal/kundenzugaenge/{zid}/widerrufen").status_code == 404
    widerruf = welt["als"](welt["a"], "leitung", "SALES_ADMIN").post(f"/api/v1/portal/kundenzugaenge/{zid}/widerrufen")
    assert widerruf.status_code == 200 and widerruf.json()["widerrufen_von"] == "leitung"
    assert welt["als"](welt["a"], "hof-neu").get("/api/v1/portal/rechnungen").status_code == 403


def test_eine_zuordnung_ist_nicht_loeschbar(welt):
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    with SessionLocal() as db, pytest.raises(DBAPIError):
        db.execute(text("DELETE FROM domain_portal.kundenzugaenge WHERE tenant_id = :t"), {"t": welt["a"]})


# ── Lieferscheine und Nachhaltigkeitsexport ───────────────────────────────────


def test_lieferscheine_und_export_nur_des_eigenen_kontos(welt):
    lieferung = {"date": "2031-05-01", "totalNutrientNKg": 10.0}
    eigen = welt["beleg"]("sales_delivery", welt["a"], welt["k1"], **lieferung)
    welt["beleg"]("sales_delivery", welt["a"], welt["k2"], **lieferung)
    welt["beleg"]("sales_delivery", welt["b"], welt["k1"], **lieferung)
    welt["zuordnen"](welt["a"], "hof-1", welt["k1"])
    c = welt["als"](welt["a"], "hof-1")
    liste = c.get("/api/v1/portal/lieferscheine")
    assert liste.status_code == 200, liste.text
    assert {d["number"] for d in liste.json()["data"]} == {eigen}
    export = c.get("/api/v1/portal/nachhaltigkeit/export.csv", params={"year": 2031, "customer_id": welt["k2"]})
    assert export.status_code == 200, export.text
    zeilen = dict(z.split(";", 1) for z in export.text.lstrip("﻿").splitlines() if ";" in z)
    assert zeilen["Anzahl Lieferscheine"] == "1"
    assert welt["als"](welt["a"], "irgendwer", "user").get(
        "/api/v1/portal/nachhaltigkeit/export.pdf", params={"year": 2031}).status_code == 403
