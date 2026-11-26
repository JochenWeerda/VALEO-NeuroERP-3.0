"""Personenkonten im Hauptbuch (M3, Nutzerentscheid 26.11.2026) - gegen die echte DB."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.finance.personenkonto import kreditorkonto_fuer_lieferant, saldenliste, sammelkonten
from app.finance.steuerschluessel import richte_skr03_ein

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    t = f"pk-{uuid.uuid4().hex[:6]}"
    kunde, partner, lieferant, lpartner = (str(uuid.uuid4()) for _ in range(4))
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        richte_skr03_ein(db, t)
        for nr, name, typ in (("1400", "Forderungen LuL", "asset"), ("8400", "Erloese 19 %", "revenue"),
                              ("1776", "Umsatzsteuer 19 %", "liability")):
            db.execute(text("INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, "
                            "account_type, is_active) VALUES (:id, :t, :nr, :n, :typ, true) ON CONFLICT DO NOTHING"),
                       {"id": f"{t}-{nr}", "t": t, "nr": nr, "n": name, "typ": typ})
        db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
                        "is_customer, debtor_account) VALUES (:p, :t, 'P1', 'Hof Janssen', true, '10001')"),
                   {"p": partner, "t": t})
        db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, "
                        "business_partner_id) VALUES (:id, :t, 'K1', 'Hof Janssen', :p)"), {"id": kunde, "t": t, "p": partner})
        db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
                        "is_supplier, creditor_account) VALUES (:p, :t, 'P2', 'Saatzucht', true, '70001')"),
                   {"p": lpartner, "t": t})
        db.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, partner_id, firmenname) "
                        "VALUES (CAST(:id AS uuid), :t, 'L1', :p, 'Saatzucht')"), {"id": lieferant, "t": t, "p": lpartner})
        db.commit()
    try:
        yield {"t": t, "kunde": kunde, "lieferant": lieferant}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                        "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                        "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                        "DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t",
                        "DELETE FROM domain_crm.customers WHERE tenant_id = :t",
                        "DELETE FROM domain_crm.business_partners WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t"):
                try:
                    with db.begin_nested():
                        db.execute(text(sql), {"t": t})
                except Exception:  # noqa: BLE001 - je nach Lauf leer; GoBD-Sperren auf Journalzeilen
                    pass
            db.commit()


def test_ausgangsrechnung_traegt_das_personenkonto_und_die_saldenliste_zeigt_es(haus):
    from app.services.sales_posting_service import SalesPostingService

    t = haus["t"]
    with SessionLocal() as db:
        SalesPostingService(db, t).post_ausgangsrechnung_with_op(
            invoice_number=f"AR-{uuid.uuid4().hex[:4]}", invoice_date=date(2026, 11, 2), customer_id=haus["kunde"],
            net_amount=Decimal("100.00"), tax_amount=Decimal("19.00"), gross_amount=Decimal("119.00"),
            posted_by="test")
    with SessionLocal() as db:
        konto = db.execute(text(
            "SELECT l.partner_konto FROM domain_erp.journal_entry_lines l JOIN domain_erp.chart_of_accounts k "
            "ON k.id = l.account_id WHERE l.tenant_id = :t AND k.account_number = '1400'"), {"t": t}).scalar_one()
        salden = saldenliste(db, t)

    assert konto == "10001"
    assert salden["personenkonten"] == {"10001": {"sammelkonto": "1400", "saldo": "119.00"}}
    assert salden["ohne_personenkonto"] == {}


def test_skr03_sammelkonten_sind_1400_und_1600_nicht_die_bank(haus):
    with SessionLocal() as db:
        assert sammelkonten(db, haus["t"]) == ["1400", "1600"]


def test_kreditorkonto_kommt_vom_partner_des_lieferanten(haus):
    with SessionLocal() as db:
        assert kreditorkonto_fuer_lieferant(db, haus["t"], haus["lieferant"]) == "70001"
        assert kreditorkonto_fuer_lieferant(db, haus["t"], "L1") == "70001"
        assert kreditorkonto_fuer_lieferant(db, haus["t"], None) is None


def test_ohne_kontenrahmen_keine_sammelkonten():
    with SessionLocal() as db:
        ergebnis = saldenliste(db, f"ohne-{uuid.uuid4().hex[:6]}")
    assert ergebnis["personenkonten"] == {}
    assert "nicht festgelegt" in ergebnis["hinweis"]


def test_verkaufsgutschrift_mindert_den_personenkontosaldo(haus):
    from app.finance.steuerschluessel import Steuergruppe
    from app.services.finance_belegbuchung import buche_verkaufsgutschrift
    from app.services.sales_posting_service import SalesPostingService

    t = haus["t"]
    with SessionLocal() as db:
        SalesPostingService(db, t).post_ausgangsrechnung_with_op(
            invoice_number=f"AR-{uuid.uuid4().hex[:4]}", invoice_date=date(2026, 11, 2), customer_id=haus["kunde"],
            net_amount=Decimal("100.00"), tax_amount=Decimal("19.00"), gross_amount=Decimal("119.00"), posted_by="test")
    with SessionLocal() as db:
        buche_verkaufsgutschrift(
            db, t, nummer=f"GS-{uuid.uuid4().hex[:4]}", datum="2026-11-05", rechnungsnummer=None, posted_by="test",
            kunden_id=haus["kunde"], gruppen=[Steuergruppe(tax_code="U19", satz=Decimal("19"), netto=Decimal("10.00"),
                                                           steuer=Decimal("1.90"), erloeskonto="8400",
                                                           steuerkonto="1776")])
        db.commit()
    with SessionLocal() as db:
        salden = saldenliste(db, t)

    assert salden["personenkonten"]["10001"]["saldo"] == "107.10"  # 119,00 - 11,90
    assert salden["ohne_personenkonto"] == {}


def test_kreditorkonto_des_mitglieds_ueber_die_mitgliedschaft(haus):
    from app.finance.personenkonto import kreditorkonto_fuer_mitglied

    t = haus["t"]
    with SessionLocal() as db:
        partner = db.execute(text("SELECT partner_id FROM domain_crm.business_partners WHERE tenant_id = :t "
                                  "AND creditor_account = '70001'"), {"t": t}).scalar_one()
        db.execute(text("INSERT INTO domain_crm.business_partner_cooperative_memberships (id, tenant_id, partner_id, "
                        "membership_number) VALUES (:id, :t, :p, 'M-17')"), {"id": str(uuid.uuid4()), "t": t, "p": partner})
        db.commit()
        konto = kreditorkonto_fuer_mitglied(db, t, "M-17")
        unbekannt = kreditorkonto_fuer_mitglied(db, t, "M-99")
        db.execute(text("DELETE FROM domain_crm.business_partner_cooperative_memberships WHERE tenant_id = :t"), {"t": t})
        db.commit()

    assert konto == "70001"
    assert unbekannt is None
