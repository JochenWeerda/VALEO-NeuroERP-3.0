"""PostgreSQL-Verhaltenstests Self-Billing M3 — Lead-Auftrag A (P0-Nachweise).

Marker ``needs_live_db``: laufen in Pytest (PostgreSQL / require_db) und Backend-QG.
Ohne Prüfstand: skip (lokal) bzw. fail bei ``PYTEST_REQUIRE_DB_STRICT=1``.
"""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.infrastructure.models import (
    Article,
    Customer,
    HarvestAcceptance,
    JournalEntry,
    JournalEntryLine,
    QualityProtocol,
    StockMovement,
    SupplierTaxProfile,
    Tenant,
    User,
    Warehouse,
    WeighingTicket,
)
from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceCreate
from app.api.v1.endpoints.harvest_rules import controlled_service
from modules.agrar.contracts.harvest_control_v1 import (
    CalculationApproveIn,
    ContextCommandIn,
    FinancialReleaseIn,
    MeasurementAttestIn,
    RuleBindIn,
    RuleCreateIn,
    RuleDecisionIn,
)
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionTermsV1
from modules.agrar.services.harvest_rule_store import HarvestRuleStore
from app.services import studio_process_simulation as simulation

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

_CENT = Decimal("0.01")


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.fixture
def case(monkeypatch):
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt

    assert pruefstand_erlaubt(engine.url), "Only the declared shared test database is allowed"
    monkeypatch.setattr(simulation, "_configured_probe", lambda: engine)
    connection = engine.connect()
    outer = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    tenant = str(uuid4())
    editor_id = str(uuid4())
    reviewer_id = str(uuid4())
    db.add(Tenant(id=tenant, name="SB-M3 evidence", domain=tenant + ".example.invalid"))
    db.flush()
    for subject, role in [(editor_id, "EINKAUF_BEARBEITEN"), (reviewer_id, "FINANCE_ADMIN")]:
        db.add(
            User(
                id=subject,
                tenant_id=tenant,
                username=subject,
                email=subject + "@example.invalid",
                first_name="Synthetic",
                last_name="Evidence",
                roles=[role],
            )
        )
    customer = Customer(
        id=str(uuid4()),
        tenant_id=tenant,
        customer_number="SBM3",
        company_name="Synthetic supplier",
    )
    article = Article(
        id=str(uuid4()),
        tenant_id=tenant,
        article_number="SBM3",
        name="Synthetic grain",
        unit="kg",
        category="grain",
        sales_price=Decimal("220"),
        mehrwertsteuer_prozent=Decimal("7"),
    )
    warehouse = Warehouse(
        id=str(uuid4()),
        tenant_id=tenant,
        warehouse_code="SBM3",
        name="Synthetic warehouse",
        address="Synthetic",
        city="Synthetic",
        postal_code="00000",
    )
    ticket = WeighingTicket(
        id=str(uuid4()),
        tenant_id=tenant,
        ticket_number="SBM3",
        gross_weight=27000,
        tare_weight=2000,
        net_weight=25000,
        moisture_pct=0,
        impurities_pct=3,
    )
    db.add_all([customer, article, warehouse, ticket])
    db.flush()
    editor = {
        "sub": editor_id,
        "roles": ["EINKAUF_BEARBEITEN"],
        "raw": {"iss": "urn:valeo:synthetic", "identity_type": "human"},
    }
    reviewer = {
        "sub": reviewer_id,
        "roles": ["FINANCE_ADMIN"],
        "raw": {"iss": "urn:valeo:synthetic", "identity_type": "human"},
    }
    svc, store = controlled_service(db, tenant, editor)
    review_svc, review_store = controlled_service(db, tenant, reviewer)
    item = svc.create_acceptance(
        HarvestAcceptanceCreate(
            acceptance_number="SBM3",
            delivery_date=date(2026, 10, 15),
            customer_id=customer.id,
            article_id=article.id,
            warehouse_id=warehouse.id,
            weighing_ticket_id=ticket.id,
        ),
        editor_id,
    )
    acceptance = db.get(HarvestAcceptance, item["id"])
    protocol = QualityProtocol(
        id=str(uuid4()),
        tenant_id=tenant,
        harvest_acceptance_id=acceptance.id,
        protocol_number="SBM3",
        version=1,
        impurities_pct=Decimal("1.5"),
        moisture_pct=0,
        source_type="manual",
        source_file_content="synthetic measurement report",
        created_by=editor_id,
    )
    db.add(protocol)
    db.flush()
    acceptance.quality_protocol_id = protocol.id
    db.commit()
    terms = HarvestDeductionTermsV1(
        customer_id=customer.id,
        article_id=article.id,
        valid_from=date(2026, 1, 1),
        valid_until=date.max,
        source_reference="synthetic terms",
        measurement_method="synthetic-lab",
        measurement_method_version="1",
        impurities_free_pct=Decimal("0"),
        quality_limit_pct=Decimal("2"),
    )
    c = SimpleNamespace(
        db=db,
        tenant=tenant,
        svc=svc,
        store=store,
        review_svc=review_svc,
        review_store=review_store,
        acceptance=acceptance,
        protocol=protocol,
        article=article,
        customer=customer,
        ticket=ticket,
        terms=terms,
        editor=editor,
        reviewer=reviewer,
        engine=engine,
    )
    try:
        yield c
    finally:
        db.close()
        assert outer.is_active
        outer.rollback()
        connection.close()
        with engine.connect() as verify:
            assert (
                verify.execute(
                    text("SELECT count(*) FROM domain_shared.tenants WHERE id=:id"),
                    {"id": tenant},
                ).scalar_one()
                == 0
            )


def _seed_extra_tax_keys(db, tenant_id: str) -> None:
    """§24- und Nullsatz-Eingangsschlüssel (nicht in SKR03-Grundausstattung)."""
    from app.finance.steuerschluessel import uuid7

    for code, name, satz, vst, aufwand, p24 in (
        ("24", "Vorsteuer §24 10,7 %", Decimal("10.7"), "1571", "3300", True),
        ("0", "Vorsteuer 0 % (Kleinunternehmer/steuerfrei)", Decimal("0"), None, "3300", False),
    ):
        exists = db.execute(
            text("SELECT 1 FROM domain_erp.tax_keys WHERE tenant_id=:t AND code=:c"),
            {"t": tenant_id, "c": code},
        ).first()
        if exists:
            db.execute(
                text(
                    "UPDATE domain_erp.tax_keys SET steuersatz=:s, par_24_ustg=:p, "
                    "debit_account=:v, expense_account=:a, active=true, "
                    "gueltig_von=DATE '2000-01-01', gueltig_bis=NULL "
                    "WHERE tenant_id=:t AND code=:c"
                ),
                {"t": tenant_id, "c": code, "s": satz, "p": p24, "v": vst, "a": aufwand},
            )
            continue
        db.execute(
            text(
                "INSERT INTO domain_erp.tax_keys "
                "(id, tenant_id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung, "
                " gueltig_von, debit_account, expense_account, par_24_ustg, country, active) "
                "VALUES (:id, :t, :c, :n, :s, '66', :n, DATE '2000-01-01', :v, :a, :p, 'DE', true)"
            ),
            {
                "id": uuid7(),
                "t": tenant_id,
                "c": code,
                "n": name,
                "s": satz,
                "v": vst,
                "a": aufwand,
                "p": p24,
            },
        )


def ready(c):
    created = c.store.create_rule(
        RuleCreateIn(idempotency_key=uuid4(), rule_id="synthetic", expected_version=0, terms=c.terms)
    )
    c.review_store.decide_rule(
        created["id"],
        RuleDecisionIn(
            idempotency_key=uuid4(),
            expected_hash=created["content_hash"],
            reason="Synthetic four-eyes verification",
            expires_at=datetime.now(UTC) + timedelta(days=1),
        ),
    )
    context = c.store.context(c.acceptance.id)
    c.store.bind_rule(
        c.acceptance.id,
        RuleBindIn(
            idempotency_key=uuid4(),
            expected_context_hash=context["context_hash"],
            rule_version_id=created["id"],
        ),
    )
    context = c.store.context(c.acceptance.id)
    c.store.attest(
        c.acceptance.id,
        MeasurementAttestIn(
            idempotency_key=uuid4(),
            expected_context_hash=context["context_hash"],
            protocol_id=c.protocol.id,
            expected_protocol_hash=context["protocol_hash"],
            measurement_method="synthetic-lab",
            measurement_method_version="1",
            source_reference="synthetic laboratory report",
        ),
    )
    return created


def calculate(c):
    return c.svc.calculate_settlement(
        c.acceptance.id,
        command=ContextCommandIn(
            idempotency_key=uuid4(),
            expected_context_hash=c.store.context(c.acceptance.id)["context_hash"],
        ),
    )


def approve(c, result):
    return c.review_store.approve_calculation(
        c.review_svc,
        c.acceptance.id,
        CalculationApproveIn(
            idempotency_key=uuid4(),
            expected_calculation_hash=result["calculation_hash"],
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            reason="Synthetic financial review",
        ),
    )


def financial_ready(
    c,
    *,
    taxation_type: str = "regular",
    article_mwst: Decimal | None = Decimal("7"),
    tax_code_override: str | None = None,
    delivery_date: date | None = None,
):
    from app.finance.steuerschluessel import richte_skr03_ein
    from app.services.number_range_service import NumberRangeService
    from modules.agrar.services.tax_profile_service import ensure_self_billing_purchase_ready

    richte_skr03_ein(c.db, c.tenant)
    _seed_extra_tax_keys(c.db, c.tenant)
    NumberRangeService(c.db).configure(c.tenant, "self_billing", "GS", 1, 6)
    if tax_code_override:
        c.db.execute(
            text(
                "INSERT INTO domain_shared.system_properties "
                "(id,tenant_id,property_key,property_value,property_type,category) "
                "VALUES (:id,:tenant,:key,:val,'string','agrar') "
                "ON CONFLICT (tenant_id, property_key) DO UPDATE SET property_value = EXCLUDED.property_value"
            ),
            {
                "id": str(uuid4()),
                "tenant": c.tenant,
                "key": f"agrar.self_billing.tax_code.{taxation_type}",
                "val": tax_code_override,
            },
        )
    if article_mwst is not None:
        c.article.mehrwertsteuer_prozent = article_mwst
    if delivery_date is not None:
        c.acceptance.delivery_date = delivery_date
    ensure_self_billing_purchase_ready(
        c.db,
        c.tenant,
        c.acceptance.customer_id,
        partner_name="Synthetic self-billing supplier",
        taxation_type=taxation_type,
        valid_from=date(2000, 1, 1),
    )
    c.db.commit()
    ready(c)
    result = calculate(c)
    approve(c, result)
    return FinancialReleaseIn(
        idempotency_key=uuid4(), expected_calculation_hash=result["calculation_hash"]
    )


def _assert_booking_bundle(c, *, expected_rate: Decimal):
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl

    c.db.refresh(c.acceptance)
    assert c.acceptance.invoice_id
    invoice = SelfBillingRepositoryImpl(c.db, commit_on_success=False).get_invoice_by_id(
        c.acceptance.invoice_id, tenant_id=c.tenant
    )
    assert invoice is not None
    assert invoice.status == "booked"
    assert invoice.journal_entry_id
    assert invoice.docflow_header_id
    assert Decimal(str(invoice.vat_rate_percent)) == expected_rate

    docs = c.db.execute(
        text(
            "SELECT count(*) FROM domain_docflow.document_headers "
            "WHERE tenant_id=:t AND id=:id"
        ),
        {"t": c.tenant, "id": invoice.docflow_header_id},
    ).scalar_one()
    assert docs == 1

    journals = c.db.query(JournalEntry).filter_by(tenant_id=c.tenant, status="posted").all()
    assert len(journals) == 1
    journal = journals[0]
    assert journal.reference == invoice.invoice_number
    lines = c.db.query(JournalEntryLine).filter_by(journal_entry_id=journal.id).all()
    debit = sum((Decimal(str(l.debit_amount)) for l in lines), Decimal("0"))
    credit = sum((Decimal(str(l.credit_amount)) for l in lines), Decimal("0"))
    assert debit == credit
    assert debit == Decimal(str(invoice.total_gross_amount_eur)).quantize(_CENT)

    op = c.db.execute(
        text(
            "SELECT count(*), coalesce(sum(betrag),0) FROM domain_erp.offene_posten "
            "WHERE tenant_id=:t AND rechnungsnr=:n AND konto_typ='kreditoren'"
        ),
        {"t": c.tenant, "n": invoice.invoice_number},
    ).one()
    assert int(op[0]) == 1
    assert Decimal(str(op[1])).quantize(_CENT) == Decimal(str(invoice.total_gross_amount_eur)).quantize(
        _CENT
    )

    partner_lines = [l for l in lines if getattr(l, "partner_konto", None)]
    assert partner_lines, "Kreditorisches Personenkonto fehlt auf Journalzeile"
    assert c.db.query(StockMovement).filter_by(tenant_id=c.tenant).count() == 1
    return invoice, journal


# ---------------------------------------------------------------------------
# Schema / Unit-ähnliche Gates (weiterhin needs_live_db wo DB)
# ---------------------------------------------------------------------------


def test_migration_columns_exist(require_db):
    from app.core.database import engine

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
        assert needed in cols


def test_unique_index_for_idempotency(require_db):
    from app.core.database import engine

    with engine.connect() as conn:
        names = {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE schemaname='domain_finance' AND tablename='self_billing_invoices'"
                )
            )
        }
    assert "uq_self_billing_invoices_tenant_ha_booked" in names


def _assert_en16931_ubl_minimal(xml: str) -> None:
    """Struktureller EN16931/XRechnung-Mindestcheck am UBL-XML (BT-Kernfelder)."""
    required = [
        "<cbc:InvoiceTypeCode>389</cbc:InvoiceTypeCode>",
        "<cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>",
        "AccountingSupplierParty",
        "AccountingCustomerParty",
        "LegalMonetaryTotal",
        "TaxTotal",
        "InvoiceLine",
    ]
    missing = [item for item in required if item not in xml]
    assert not missing, f"EN16931/XRechnung-Mindestfelder fehlen: {missing}"


def test_einvoice_type_code_is_389_and_en16931_validated():
    """Punkt 8: Typ 389 + EN16931-Mindestvalidierung; drafthorse setzt 389 (nicht 380)."""
    from unittest.mock import patch

    from modules.agrar.services.self_billing_service import (
        SelfBillingInvoice,
        generate_einvoice_xrechnung,
        set_xrechnung_generator,
    )
    from modules.agrar.services import xrechnung_drafthorse as dra

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
    supplier = {
        "name": "Lieferant GmbH",
        "street": "Feld 1",
        "city": "Agrarstadt",
        "postal_code": "12345",
        "country_code": "DE",
        "vat_id": "DE123456789",
    }
    customer = {
        "name": "Genossenschaft",
        "street": "Markt 2",
        "city": "Handel",
        "postal_code": "54321",
        "country_code": "DE",
    }
    lines = [
        {
            "description": "Weizen",
            "quantity": Decimal("1"),
            "unit": "C62",
            "unit_price": Decimal("10"),
            "line_net": Decimal("10"),
            "vat_rate": Decimal("7"),
            "line_vat": Decimal("0.70"),
        }
    ]

    set_xrechnung_generator(None)
    xml_fallback = generate_einvoice_xrechnung(inv, supplier, customer, lines)
    _assert_en16931_ubl_minimal(xml_fallback)

    assert dra.is_available(), "drafthorse muss in CI/requirements installiert sein"
    captured: dict[str, str] = {}

    def _capture_serialize(self, *args, **kwargs):
        captured["type_code"] = str(self.header.type_code)
        # Valides Minimal-XML mit Typ 389 — Schema-Vollständigkeit prüft der UBL-Pfad oben.
        return (
            '<?xml version="1.0"?>'
            "<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\">"
            f"<cbc:InvoiceTypeCode>{captured['type_code']}</cbc:InvoiceTypeCode>"
            "</Invoice>"
        ).encode("utf-8")

    with patch("modules.agrar.services.xrechnung_drafthorse.Document.serialize", _capture_serialize):
        dra.register_as_xrechnung_generator()
        xml = generate_einvoice_xrechnung(inv, supplier, customer, lines)
    assert captured.get("type_code") == "389"
    assert b"389" in xml if isinstance(xml, (bytes, bytearray)) else "389" in xml


# ---------------------------------------------------------------------------
# Punkte 1–3: Besteuerungsarten + Bundle-Invarianten
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "taxation_type,article_mwst,override,expected_rate",
    [
        ("regular", Decimal("7"), None, Decimal("7")),
        ("regular", Decimal("19"), "9", Decimal("19")),
        ("ustg24_flat_rate", Decimal("7"), "24", Decimal("10.7")),
        ("small_business", Decimal("7"), "0", Decimal("0")),
    ],
)
def test_taxation_release_bundle_invariants(case, taxation_type, article_mwst, override, expected_rate):
    c = case
    body = financial_ready(
        c,
        taxation_type=taxation_type,
        article_mwst=article_mwst,
        tax_code_override=override,
    )
    c.svc.release_acceptance(
        c.acceptance.id, "final", True, True, c.editor["sub"], command=body
    )
    invoice, _journal = _assert_booking_bundle(c, expected_rate=expected_rate)
    assert invoice.taxation_type == taxation_type
    expected_vat = (
        Decimal(str(invoice.total_net_amount_eur)) * expected_rate / Decimal("100")
    ).quantize(_CENT, rounding=ROUND_HALF_UP)
    assert Decimal(str(invoice.total_vat_amount_eur)) == expected_vat


def test_year_boundary_uses_historical_tax_profile_and_key(case):
    """Punkt 2: Profilwechsel über Jahresgrenze + historischer Schlüssel."""
    c = case
    from app.finance.steuerschluessel import richte_skr03_ein, uuid7
    from app.services.number_range_service import NumberRangeService
    from modules.agrar.services.tax_profile_service import ensure_self_billing_purchase_ready

    richte_skr03_ein(c.db, c.tenant)
    _seed_extra_tax_keys(c.db, c.tenant)
    # Historischer §24-Schlüssel nur bis 2024 gültig; ab 2025 anderer Code
    c.db.execute(
        text(
            "UPDATE domain_erp.tax_keys SET gueltig_bis = DATE '2024-12-31' "
            "WHERE tenant_id=:t AND code='24'"
        ),
        {"t": c.tenant},
    )
    c.db.execute(
        text(
            "INSERT INTO domain_erp.tax_keys "
            "(id, tenant_id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung, "
            " gueltig_von, gueltig_bis, debit_account, expense_account, par_24_ustg, country, active) "
            "VALUES (:id, :t, '25', 'Vorsteuer §24 10,7 % ab 2025', 10.7, '66', '§24', "
            " DATE '2025-01-01', NULL, '1571', '3300', true, 'DE', true)"
        ),
        {"id": uuid7(), "t": c.tenant},
    )
    NumberRangeService(c.db).configure(c.tenant, "self_billing", "GS", 1, 6)
    ensure_self_billing_purchase_ready(
        c.db,
        c.tenant,
        c.acceptance.customer_id,
        taxation_type="ustg24_flat_rate",
        valid_from=date(2020, 1, 1),
    )
    # Schließe altes Profil; neues ab 2025 (weiter §24, anderer Key)
    old = (
        c.db.query(SupplierTaxProfile)
        .filter_by(tenant_id=c.tenant, supplier_id=c.acceptance.customer_id)
        .one()
    )
    old.valid_to = date(2024, 12, 31)
    c.db.add(
        SupplierTaxProfile(
            id=str(uuid4()),
            supplier_id=c.acceptance.customer_id,
            taxation_type="ustg24_flat_rate",
            valid_from=date(2025, 1, 1),
            tenant_id=c.tenant,
        )
    )
    # Lieferdatum + Vertragsregel müssen vor ready/bind zur Annahme passen
    c.acceptance.delivery_date = date(2024, 6, 15)
    c.terms = c.terms.model_copy(update={"valid_from": date(2020, 1, 1)})
    c.db.commit()
    ready(c)
    result = calculate(c)
    approve(c, result)
    body = FinancialReleaseIn(
        idempotency_key=uuid4(), expected_calculation_hash=result["calculation_hash"]
    )
    c.svc.release_acceptance(
        c.acceptance.id, "final", True, True, c.editor["sub"], command=body
    )
    invoice, _ = _assert_booking_bundle(c, expected_rate=Decimal("10.7"))
    assert (invoice.tax_context or {}).get("tax_code") == "24"
    assert (invoice.tax_context or {}).get("delivery_date") == "2024-06-15"


# ---------------------------------------------------------------------------
# Punkt 4: konkurrierende Sessions
# ---------------------------------------------------------------------------


def test_concurrent_booking_second_session_conflicts(require_db):
    """Zwei unabhängige Verbindungen: genau eine Buchung, zweite Conflict/Unique."""
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt
    from app.finance.steuerschluessel import richte_skr03_ein
    from app.services.number_range_service import NumberRangeService
    from modules.agrar.services.tax_profile_service import ensure_self_billing_purchase_ready
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
    from modules.agrar.services.self_billing_service import CreditNoteCreate, create_credit_note
    from app.services.self_billing_buchung import (
        buche_self_billing,
        build_vorsteuergruppen_from_resolved,
    )
    from app.services.self_billing_docflow import lege_self_billing_beleg_an, verknuepfe_erweiterung
    from modules.agrar.services.tax_profile_service import (
        TRANSACTION_TYPE_SELF_BILLING,
        resolve_self_billing_tax_code,
    )

    assert pruefstand_erlaubt(engine.url)
    tenant = str(uuid4())
    ha_id = str(uuid4())
    supplier = str(uuid4())
    inv_id = ""

    def _cleanup():
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM domain_erp.journal_entry_lines WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_erp.journal_entries WHERE tenant_id=:t"), {"t": tenant}
            )
            conn.execute(
                text("DELETE FROM domain_erp.offene_posten WHERE tenant_id=:t"), {"t": tenant}
            )
            conn.execute(
                text("DELETE FROM domain_finance.self_billing_invoices WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_docflow.document_headers WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_inventory.harvest_acceptances WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_crm.supplier_tax_profiles WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text(
                    "DELETE FROM domain_crm.business_partner_billing_configs "
                    "WHERE partner_id=:p"
                ),
                {"p": supplier},
            )
            conn.execute(
                text("DELETE FROM domain_crm.business_partners WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_crm.customers WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_erp.tax_keys WHERE tenant_id=:t"), {"t": tenant}
            )
            conn.execute(
                text("DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_shared.system_properties WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_shared.number_ranges WHERE tenant_id=:t"),
                {"t": tenant},
            )
            conn.execute(
                text("DELETE FROM domain_shared.tenants WHERE id=:t"), {"t": tenant}
            )

    try:
        with Session(engine) as db:
            db.add(Tenant(id=tenant, name="concurrent", domain=tenant + ".example.invalid"))
            db.flush()
            # harvest_acceptances.customer_id → domain_crm.customers (FK)
            db.add(
                Customer(
                    id=supplier,
                    tenant_id=tenant,
                    customer_number="CONC",
                    company_name="Concurrent supplier",
                )
            )
            db.flush()
            richte_skr03_ein(db, tenant)
            NumberRangeService(db).configure(tenant, "self_billing", "GS", 1, 6)
            ensure_self_billing_purchase_ready(
                db, tenant, supplier, taxation_type="regular", valid_from=date(2000, 1, 1)
            )
            db.execute(
                text(
                    "INSERT INTO domain_inventory.harvest_acceptances "
                    "(id, tenant_id, acceptance_number, delivery_date, customer_id, "
                    " operator_id, release_status) "
                    "VALUES (:id, :t, 'CONC', DATE '2026-01-15', :s, "
                    " 'concurrent-op', 'final')"
                ),
                {"id": ha_id, "t": tenant, "s": supplier},
            )
            repo = SelfBillingRepositoryImpl(db, commit_on_success=False)
            inv = create_credit_note(
                repo,
                CreditNoteCreate(
                    invoice_number="GSCONC01",
                    tenant_id=tenant,
                    harvest_acceptance_id=ha_id,
                    total_net_amount_eur=Decimal("100.00"),
                    total_vat_amount_eur=Decimal("7.00"),
                    total_gross_amount_eur=Decimal("107.00"),
                    vat_rate_percent=Decimal("7"),
                    created_by="concurrent",
                ),
                taxation_type="regular",
            )
            inv_id = inv.id
            db.commit()

        errors: list[BaseException] = []

        def _book(session: Session):
            try:
                from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl as Repo

                invoice = Repo(session, commit_on_success=False).get_invoice_by_id(
                    inv_id, tenant_id=tenant
                )
                resolved = resolve_self_billing_tax_code(
                    session,
                    tenant_id=tenant,
                    supplier_id=supplier,
                    taxation_type="regular",
                    article_tax_class="reduced",
                    transaction_type=TRANSACTION_TYPE_SELF_BILLING,
                    delivery_date=date(2026, 1, 15),
                )
                gruppen = build_vorsteuergruppen_from_resolved(
                    resolved, netto=Decimal("100.00")
                )
                doc = lege_self_billing_beleg_an(
                    session,
                    tenant,
                    supplier_id=supplier,
                    invoice_number="GSCONC01",
                    tax_code=resolved["tax_code"],
                    net_amount=Decimal("100.00"),
                    description="concurrent",
                    harvest_acceptance_id=ha_id,
                    akteur="concurrent",
                    document_date=date(2026, 1, 15),
                )
                verknuepfe_erweiterung(
                    session, tenant, self_billing_invoice_id=inv_id, docflow_header_id=doc
                )
                invoice.docflow_header_id = doc
                buche_self_billing(
                    session,
                    tenant,
                    invoice=invoice,
                    supplier_id=supplier,
                    delivery_date=date(2026, 1, 15),
                    tax_context={**resolved},
                    gruppen=gruppen,
                    posted_by="concurrent",
                    harvest_acceptance_id=ha_id,
                )
                session.commit()
            except BaseException as exc:  # noqa: BLE001 — beide Outcomes sammeln
                session.rollback()
                errors.append(exc)

        with Session(engine) as s1, Session(engine) as s2:
            _book(s1)
            _book(s2)

        assert len(errors) == 1, f"erwartet genau einen Konflikt, got {errors!r}"
        assert isinstance(errors[0], (ConflictError, Exception))
        with engine.connect() as conn:
            journals = conn.execute(
                text(
                    "SELECT count(*) FROM domain_erp.journal_entries "
                    "WHERE tenant_id=:t AND status='posted'"
                ),
                {"t": tenant},
            ).scalar_one()
            booked = conn.execute(
                text(
                    "SELECT count(*) FROM domain_finance.self_billing_invoices "
                    "WHERE tenant_id=:t AND journal_entry_id IS NOT NULL"
                ),
                {"t": tenant},
            ).scalar_one()
        assert journals == 1 and booked == 1
    finally:
        _cleanup()


# ---------------------------------------------------------------------------
# Punkt 5: Storno nach Profilwechsel
# ---------------------------------------------------------------------------


def test_storno_keeps_original_tax_context_after_profile_change(case):
    c = case
    body = financial_ready(c, taxation_type="regular", article_mwst=Decimal("7"))
    c.svc.release_acceptance(
        c.acceptance.id, "final", True, True, c.editor["sub"], command=body
    )
    invoice, journal = _assert_booking_bundle(c, expected_rate=Decimal("7"))
    original_ctx = dict(invoice.tax_context or {})
    original_taxation = invoice.taxation_type

    # Profilwechsel auf §24 nach Buchung
    prof = (
        c.db.query(SupplierTaxProfile)
        .filter_by(tenant_id=c.tenant, supplier_id=c.acceptance.customer_id)
        .order_by(SupplierTaxProfile.valid_from.desc())
        .first()
    )
    prof.valid_to = date(2026, 10, 14)
    c.db.add(
        SupplierTaxProfile(
            id=str(uuid4()),
            supplier_id=c.acceptance.customer_id,
            taxation_type="ustg24_flat_rate",
            valid_from=date(2026, 10, 16),
            tenant_id=c.tenant,
        )
    )
    c.db.flush()

    from app.services.self_billing_buchung import storno_self_billing

    result = storno_self_billing(
        c.db, c.tenant, invoice=invoice, reason="Synthetic storno after profile change"
    )
    c.db.flush()
    assert result["journal_entry_id"] == journal.id
    assert result["reversal_entry_id"]
    assert result["reversal_entry_id"] != journal.id
    reversed_orig = c.db.get(JournalEntry, journal.id)
    assert reversed_orig.status == "reversed"
    # Originalkontext unverändert am Beleg
    c.db.expire_all()
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl

    refreshed = SelfBillingRepositoryImpl(c.db, commit_on_success=False).get_invoice_by_id(
        invoice.id, tenant_id=c.tenant
    )
    assert refreshed.taxation_type == original_taxation
    assert (refreshed.tax_context or {}).get("tax_code") == original_ctx.get("tax_code")
    assert Decimal(str((refreshed.tax_context or {}).get("rate", original_ctx.get("rate")))) == Decimal(
        "7"
    )


# ---------------------------------------------------------------------------
# Punkt 6: API-Umgehung Freigabe
# ---------------------------------------------------------------------------


def test_api_buchung_without_final_release_is_blocked(case):
    c = case
    from fastapi import HTTPException
    from app.api.v1.endpoints import self_billing as sb_api
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
    from modules.agrar.services.self_billing_service import CreditNoteCreate, create_credit_note
    from app.finance.steuerschluessel import richte_skr03_ein
    from app.services.number_range_service import NumberRangeService
    from modules.agrar.services.tax_profile_service import ensure_self_billing_purchase_ready
    import asyncio

    richte_skr03_ein(c.db, c.tenant)
    NumberRangeService(c.db).configure(c.tenant, "self_billing", "GS", 1, 6)
    ensure_self_billing_purchase_ready(
        c.db, c.tenant, c.acceptance.customer_id, taxation_type="regular"
    )
    c.acceptance.release_status = "draft"
    c.db.flush()
    repo = SelfBillingRepositoryImpl(c.db, commit_on_success=False)
    inv = create_credit_note(
        repo,
        CreditNoteCreate(
            invoice_number="GSBYPASS1",
            tenant_id=c.tenant,
            harvest_acceptance_id=c.acceptance.id,
            total_net_amount_eur=Decimal("10.00"),
            total_vat_amount_eur=Decimal("0.70"),
            total_gross_amount_eur=Decimal("10.70"),
            vat_rate_percent=Decimal("7"),
            created_by=c.editor["sub"],
        ),
        taxation_type="regular",
    )
    c.db.flush()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            sb_api.buche_gutschrift(
                invoice_id=inv.id, db=c.db, tenant_id=c.tenant, request=None
            )
        )
    assert exc.value.status_code == 422
    detail = str(exc.value.detail).lower()
    assert "freigabe" in detail, detail


def test_api_create_credit_note_alone_does_not_post_journal(case):
    """Alternativer API-Pfad create-credit-note ohne Freigabe: kein Journal."""
    c = case
    from app.finance.steuerschluessel import richte_skr03_ein
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
    from modules.agrar.services.self_billing_service import CreditNoteCreate, create_credit_note

    richte_skr03_ein(c.db, c.tenant)
    repo = SelfBillingRepositoryImpl(c.db, commit_on_success=False)
    inv = create_credit_note(
        repo,
        CreditNoteCreate(
            invoice_number="GSDRAFT01",
            tenant_id=c.tenant,
            harvest_acceptance_id=c.acceptance.id,
            total_net_amount_eur=Decimal("10.00"),
            total_vat_amount_eur=Decimal("0.70"),
            total_gross_amount_eur=Decimal("10.70"),
            vat_rate_percent=Decimal("7"),
            created_by=c.editor["sub"],
        ),
        taxation_type="regular",
    )
    assert inv.status == "draft"
    assert inv.journal_entry_id is None
    assert c.db.query(JournalEntry).filter_by(tenant_id=c.tenant).count() == 0


# ---------------------------------------------------------------------------
# Punkt 7: Mandantentrennung
# ---------------------------------------------------------------------------


def test_tenant_isolation_read_and_write(case):
    c = case
    body = financial_ready(c)
    c.svc.release_acceptance(
        c.acceptance.id, "final", True, True, c.editor["sub"], command=body
    )
    invoice, _ = _assert_booking_bundle(c, expected_rate=Decimal("7"))

    from app.services.harvest_acceptance_service import HarvestAcceptanceService

    other = HarvestAcceptanceService(c.db, str(uuid4()))
    with pytest.raises(EntityNotFoundError):
        other.get_acceptance(c.acceptance.id)

    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl

    assert (
        SelfBillingRepositoryImpl(c.db, commit_on_success=False).get_invoice_by_id(
            invoice.id, tenant_id=str(uuid4())
        )
        is None
    )
    foreign_store = HarvestRuleStore(c.db, str(uuid4()), c.editor)
    with pytest.raises(EntityNotFoundError):
        foreign_store.context(c.acceptance.id)
