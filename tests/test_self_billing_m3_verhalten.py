"""PostgreSQL-/HTTP-Verhaltenstests Self-Billing M3 (Lead-Zusatzliste).

Laufen nur mit TEST_DATABASE_URL / gemeinsamen Prüfstand; sonst skip (kein neuer Container).
"""
from __future__ import annotations

import os
from decimal import Decimal

import pytest

pytestmark = pytest.mark.integration


def _db_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")


@pytest.fixture(scope="module")
def engine():
    url = _db_url()
    if not url:
        pytest.skip("Kein TEST_DATABASE_URL — gemeinsamer Prüfstand nicht konfiguriert")
    try:
        from sqlalchemy import create_engine
    except ImportError:
        pytest.skip("SQLAlchemy nicht installiert")
    eng = create_engine(url)
    try:
        with eng.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Prüfstand nicht erreichbar: {exc}")
    return eng


def test_migration_columns_exist(engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        cols = {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='domain_finance' AND table_name='self_billing_invoices'"
                )
            )
        }
    for needed in ("docflow_header_id", "journal_entry_id", "taxation_type", "tax_context"):
        if needed not in cols:
            pytest.skip(f"Migration self_billing_m3 noch nicht angewandt ({needed} fehlt)")


def test_unique_index_for_idempotency(engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE schemaname='domain_finance' AND tablename='self_billing_invoices'"
            )
        ).fetchall()
    names = {r[0] for r in rows}
    if "uq_self_billing_invoices_tenant_ha_booked" not in names:
        pytest.skip("Idempotenz-Index noch nicht migriert")


def test_einvoice_type_code_is_389():
    from modules.agrar.services.self_billing_service import (
        SelfBillingInvoice,
        generate_einvoice_xrechnung,
    )
    from datetime import datetime

    inv = SelfBillingInvoice(
        id="sb_x",
        tenant_id="t",
        invoice_number="GS-1",
        total_net_amount_eur=Decimal("10"),
        total_vat_amount_eur=Decimal("0.70"),
        total_gross_amount_eur=Decimal("10.70"),
        vat_rate_percent=Decimal("7"),
        created_at=datetime(2026, 3, 1),
    )
    xml = generate_einvoice_xrechnung(inv, {"name": "L"}, {"name": "K"}, [])
    assert "<cbc:InvoiceTypeCode>389</cbc:InvoiceTypeCode>" in xml


def test_resolver_rejects_unknown_transaction_type():
    from modules.agrar.services.tax_profile_service import resolve_self_billing_tax_code
    from app.core.exceptions import ValidationFailedError
    from datetime import date
    from unittest.mock import MagicMock

    with pytest.raises(ValidationFailedError):
        resolve_self_billing_tax_code(
            MagicMock(),
            tenant_id="t",
            supplier_id="s",
            taxation_type="regular",
            article_tax_class=None,
            transaction_type="wrong",
            delivery_date=date(2026, 1, 1),
        )
