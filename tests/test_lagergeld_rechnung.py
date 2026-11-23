"""Lagergeld als Ausgangsrechnung an den Einlagerer - gegen die echte Datenbank (M3, 24.11.2026)."""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, get_db
from app.core.exceptions import register_domain_exception_handlers
from app.domains.inventory.api import inventory_auth, storage_fees
from testgrenze import ersetze_nutzer

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    from test_belege_lesen import AUFRAEUMEN as BELEGE

    from app.finance.steuerschluessel import richte_skr03_ein

    mandant = f"lg-{uuid.uuid4().hex[:6]}"
    kunden = [str(uuid.uuid4()), str(uuid.uuid4())]
    lauf, offen = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": mandant})
        richte_skr03_ein(db, mandant)  # Schluessel 3 (19 %, Erloes 8400) und 9 (Vorsteuer, kein Erloeskonto)
        for nr, kunde in enumerate(kunden):
            db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                            "VALUES (:id, :t, :nr, :name)"),
                       {"id": kunde, "t": mandant, "nr": f"K-{nr}", "name": f"Einlagerer {nr}"})
        # Ein Lauf je Mandant, Monat und Art: der noch laufende liegt im Folgemonat.
        for kennung, status, monat in ((lauf, "posted", 10), (offen, "running", 11)):
            db.execute(text(
                "INSERT INTO domain_inventory.consignment_storage_fee_runs (id, tenant_id, period_month, run_type, "
                "status, currency, total_items, total_amount) VALUES (:id, :t, :m, 'post', :s, 'EUR', 3, 85)"),
                {"id": kennung, "t": mandant, "m": date(2026, monat, 1), "s": status})
        for kunde, artikel, menge, satz in ((kunden[0], "WEIZEN", 100, "0.50"), (kunden[0], "GERSTE", 40, "0.25"),
                                            (kunden[1], "RAPS", 50, "0.50")):
            db.execute(text(
                "INSERT INTO domain_inventory.consignment_storage_fee_charges (id, run_id, tenant_id, owner_partner_id, "
                "article_id, warehouse_id, basis_quantity, monthly_rate, amount, currency) "
                "VALUES (:id, :r, :t, :k, :a, 'LAGER-1', :q, CAST(:p AS numeric), :q * CAST(:p AS numeric), 'EUR')"),
                {"id": str(uuid.uuid4()), "r": lauf, "t": mandant, "k": kunde, "a": artikel, "q": menge, "p": satz})
        db.commit()
    try:
        yield {"mandant": mandant, "kunden": kunden, "lauf": lauf, "offen": offen}
    finally:
        with SessionLocal() as db:
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            for sql in (*(s for s in BELEGE if "domain_shared.tenants" not in s),
                        "DELETE FROM domain_inventory.consignment_storage_fee_charges WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.consignment_storage_fee_runs WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": mandant})
            db.commit()


@pytest.fixture
def client(haus):
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(storage_fees.router, prefix="/storage-fees")

    def sitzung():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = sitzung
    app.dependency_overrides[inventory_auth.require_inventory_access] = lambda: "token"
    app.dependency_overrides[inventory_auth.require_inventory_admin] = lambda: "token"
    app.dependency_overrides[inventory_auth.get_current_tenant_id] = lambda: haus["mandant"]
    ersetze_nutzer(app, "LAGER_ADMIN")
    with TestClient(app) as c:
        yield c


def _rechnungen(mandant: str):
    with SessionLocal() as db:
        return db.execute(text(
            "SELECT h.customer_id, h.status, COUNT(i.id), SUM(i.quantity * i.unit_price) "
            "FROM domain_docflow.document_headers h LEFT JOIN domain_docflow.document_items i ON i.header_id = h.id "
            "WHERE h.tenant_id = :t AND h.doc_type = 'sales_invoice' AND h.source_system = 'lagergeld' "
            "GROUP BY h.customer_id, h.status ORDER BY h.customer_id"), {"t": mandant}).fetchall()


def test_je_einlagerer_ein_rechnungsentwurf(client, haus):
    antwort = client.post(f"/storage-fees/runs/{haus['lauf']}/rechnungen", json={"steuerschluessel": "3"})

    assert antwort.status_code == 201, antwort.text
    assert sorted((r["partner_id"], r["positionen"], r["betrag_netto"]) for r in antwort.json()) == sorted([
        (haus["kunden"][0], 2, 60.0), (haus["kunden"][1], 1, 25.0)])
    rechnungen = {str(k): (s, n, float(b)) for k, s, n, b in _rechnungen(haus["mandant"])}
    assert rechnungen == {haus["kunden"][0]: ("draft", 2, 60.0), haus["kunden"][1]: ("draft", 1, 25.0)}


def test_wiederholung_legt_nichts_doppelt_an(client, haus):
    erste = client.post(f"/storage-fees/runs/{haus['lauf']}/rechnungen", json={"steuerschluessel": "3"}).json()
    zweite = client.post(f"/storage-fees/runs/{haus['lauf']}/rechnungen", json={"steuerschluessel": "3"}).json()

    assert sorted(r["beleg_id"] for r in erste) == sorted(r["beleg_id"] for r in zweite)
    assert len(_rechnungen(haus["mandant"])) == 2


def test_vorsteuerschluessel_ist_kein_verkaufsschluessel(client, haus):
    antwort = client.post(f"/storage-fees/runs/{haus['lauf']}/rechnungen", json={"steuerschluessel": "9"})

    assert antwort.status_code == 422
    assert _rechnungen(haus["mandant"]) == []


def test_nur_aus_einem_abgeschlossenen_lauf(client, haus):
    assert client.post(f"/storage-fees/runs/{haus['offen']}/rechnungen",
                       json={"steuerschluessel": "3"}).status_code == 409
    assert client.post(f"/storage-fees/runs/{uuid.uuid4()}/rechnungen",
                       json={"steuerschluessel": "3"}).status_code == 404
    assert _rechnungen(haus["mandant"]) == []
