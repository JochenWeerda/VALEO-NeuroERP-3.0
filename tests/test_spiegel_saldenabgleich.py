"""Spiegelbetrieb: monatlicher Saldenabgleich je Personenkonto (M6, 26.11.2026) - gegen die echte DB; liest nur."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.finance.steuerschluessel import richte_skr03_ein
from app.services.legacy_interface_adapter_service import LegacyInterfaceAdapterService
from app.services.spiegel_saldenabgleich import abgleichen

pytestmark = pytest.mark.integration

MAPPING = {"TYP": "record_type", "QUELLE": "source_ref", "KONTO": "konto", "JAHR": "jahr", "MONAT": "monat",
           "SALDO": "saldo"}
VERTRAG = {"encoding": "utf-8", "record_types": ["kontosaldo"], "sample_hash": "synthetisch", "export_stand": "Test"}


@pytest.fixture
def haus():
    t = f"sa-{uuid.uuid4().hex[:6]}"
    kunden = {}
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        richte_skr03_ein(db, t)
        for nr, name, typ in (("1400", "Forderungen LuL", "asset"), ("8400", "Erloese 19 %", "revenue"),
                              ("1776", "Umsatzsteuer 19 %", "liability")):
            db.execute(text("INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, "
                            "account_type, is_active) VALUES (:id, :t, :nr, :n, :typ, true) ON CONFLICT DO NOTHING"),
                       {"id": f"{t}-{nr}", "t": t, "nr": nr, "n": name, "typ": typ})
        for konto in ("10001", "10004"):
            partner, kunde = str(uuid.uuid4()), str(uuid.uuid4())
            db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
                            "is_customer, debtor_account) VALUES (:p, :t, :nr, :nr, true, :k)"),
                       {"p": partner, "t": t, "nr": f"P{konto}", "k": konto})
            db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, "
                            "business_partner_id) VALUES (:id, :t, :nr, :nr, :p)"),
                       {"id": kunde, "t": t, "nr": f"K{konto}", "p": partner})
            kunden[konto] = kunde
        db.commit()
    LegacyInterfaceAdapterService(SessionLocal(), t).configure(
        "l3_spiegel", {"format_contract": VERTRAG, "field_mapping": MAPPING}, actor="test", reason="M6-Test")
    try:
        yield t, kunden
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_integration.spiegel_protokoll WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_staging WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_audit WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_profiles WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                        "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                        "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
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


def _rechnung(t: str, kunde: str, brutto: str) -> None:
    from app.services.sales_posting_service import SalesPostingService

    netto = (Decimal(brutto) / Decimal("1.19")).quantize(Decimal("0.01"))
    with SessionLocal() as db:
        SalesPostingService(db, t).post_ausgangsrechnung_with_op(
            invoice_number=f"AR-{uuid.uuid4().hex[:5]}", invoice_date=date(2026, 11, 10), customer_id=kunde,
            net_amount=netto, tax_amount=Decimal(brutto) - netto, gross_amount=Decimal(brutto), posted_by="test")


def _batch(t: str, records: list[dict]) -> str:
    with SessionLocal() as db:
        dienst = LegacyInterfaceAdapterService(db, t)
        batch = dienst.intake("l3_spiegel", f"sa-{uuid.uuid4().hex[:4]}", {"records": records}, actor="test")["id"]
        for schritt in (dienst.stage, dienst.reconcile, dienst.approve):
            schritt(batch, actor="test", reason="M6")
        return batch


def _saldo(konto: str, betrag: str) -> dict:
    return {"TYP": "kontosaldo", "QUELLE": f"{konto}/2026-11", "KONTO": konto, "JAHR": "2026", "MONAT": "11",
            "SALDO": betrag}


def test_monatsabgleich_findet_gleich_abweichend_fehlend_und_fehlt_in_l3(haus):
    t, kunden = haus
    _rechnung(t, kunden["10001"], "119.00")
    _rechnung(t, kunden["10004"], "10.00")
    batch = _batch(t, [_saldo("10001", "119,00"), _saldo("10002", "50.00"), _saldo("10003", "0")])
    with SessionLocal() as db:
        ergebnis = abgleichen(db, t, batch, actor="test", reason="M6")

    assert ergebnis["stichtag"] == "2026-11-30"
    assert (ergebnis["unveraendert"], ergebnis["fehler"]) == (2, 1)  # 10001 gleich, 10003 beidseitig 0
    assert ergebnis["fehlt_in_l3"] == [{"konto": "10004", "valeo_saldo": "10.00"}]
    assert ergebnis["abweichungsfrei"] is False


def test_abweichender_saldo_und_abweichungsfreier_monat(haus):
    t, kunden = haus
    _rechnung(t, kunden["10001"], "119.00")
    with SessionLocal() as db:
        abweichend = abgleichen(db, t, _batch(t, [_saldo("10001", "100.00")]), actor="test", reason="M6")
    with SessionLocal() as db:
        sauber = abgleichen(db, t, _batch(t, [_saldo("10001", "119.00")]), actor="test", reason="M6")

    assert abweichend["geaendert"] == 1
    assert sauber["abweichungsfrei"] is True
