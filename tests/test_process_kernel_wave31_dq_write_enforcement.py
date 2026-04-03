from __future__ import annotations

import asyncio
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.articles import create_article, update_article
from app.api.v1.endpoints.ap_invoices import create_ap_invoice
from app.api.v1.endpoints.agrar_contracts import AgrarContractCreate, create_agrar_contract
from app.api.v1.endpoints.agrar_settlements import SettlementCreate, create_settlement
from app.api.v1.endpoints.creditors import CreditorCreate, create_creditor
from app.api.v1.endpoints.debtors import DebtorCreate, DebtorUpdate, create_debtor, update_debtor
from app.api.v1.endpoints.weighing_tickets import (
    WeighingTicketCreate,
    WeighingTicketUpdate,
    create_weighing_ticket,
    update_weighing_ticket,
)
from app.documents.models import SalesInvoice
from app.api.v1.schemas.inventory import ArticleCreate, ArticleUpdate


class FailDB:
    def execute(self, *args, **kwargs):
        raise AssertionError("DB access should not happen before DQ validation")

    def query(self, *args, **kwargs):
        raise AssertionError("DB access should not happen before DQ validation")

    def commit(self):
        raise AssertionError("commit should not happen before DQ validation")

    def rollback(self):
        raise AssertionError("rollback should not happen before DQ validation")


class _RowResult:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class DebtorUpdateDB:
    def __init__(self):
        address = {
            "contact_person": None,
            "street": "Hauptstrasse 1",
            "postal_code": "12345",
            "city": "Musterstadt",
            "country": "DE",
        }
        self.row = (
            "debtor-1",
            "tenant-1",
            "DB-001",
            "Kunde AG",
            address,
            "30_days",
            Decimal("0.00"),
            True,
            None,
            None,
        )
        self.calls = 0

    def execute(self, *args, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return _RowResult(self.row)
        raise AssertionError("update SQL should not run after DQ rejection")

    def commit(self):
        raise AssertionError("commit should not happen after DQ rejection")

    def rollback(self):
        raise AssertionError("rollback should not happen after DQ rejection")


class _FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class ArticleUpdateDB:
    def __init__(self, article):
        self.article = article

    def query(self, *args, **kwargs):
        return _FakeQuery(self.article)

    def commit(self):
        raise AssertionError("commit should not happen after DQ rejection")

    def refresh(self, *args, **kwargs):
        raise AssertionError("refresh should not happen after DQ rejection")


class WeighingUpdateDB:
    def __init__(self, ticket):
        self.ticket = ticket

    def query(self, *args, **kwargs):
        return _FakeQuery(self.ticket)

    def commit(self):
        raise AssertionError("commit should not happen after DQ rejection")

    def refresh(self, *args, **kwargs):
        raise AssertionError("refresh should not happen after DQ rejection")


def test_create_creditor_rejects_invalid_country_before_db_access():
    payload = CreditorCreate(
        tenant_id="tenant-1",
        creditor_number="KR-001",
        company_name="Lieferant GmbH",
        street="Hauptstrasse 1",
        postal_code="12345",
        city="Musterstadt",
        country="XX",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_creditor(payload, tenant_id="tenant-1", db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Lieferant"


def test_create_agrar_contract_requires_fixed_price_for_fixed_contract_before_db_access():
    payload = AgrarContractCreate(
        contract_number="K-001",
        contract_type="buy",
        harvest_year=2026,
        partner_id="L-001",
        article_id="ART-001",
        pricing_model="fixed",
        fixed_price=None,
        total_quantity_kg=25000.0,
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_agrar_contract(payload, tenant_id="tenant-1", db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Kontrakt"


def test_create_ap_invoice_requires_supplier_before_repo_access():
    invoice = SalesInvoice(
        number="RE-1001",
        date="2026-03-15",
        customerId="",
        dueDate="2026-04-15",
        lines=[],
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_ap_invoice(invoice, db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "APRechnung"


def test_create_settlement_requires_supplier_before_db_access():
    payload = SettlementCreate(
        settlement_number="SET-001",
        supplier_id="",
        gross_quantity_kg=50000.0,
        unit_price_eur_per_ton=225.0,
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_settlement(payload, tenant_id="tenant-1", db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Abrechnung"


def test_create_debtor_rejects_invalid_country_before_db_access():
    payload = DebtorCreate(
        tenant_id="tenant-1",
        debtor_number="DB-001",
        company_name="Kunde AG",
        street="Markt 1",
        postal_code="12345",
        city="Musterstadt",
        country="XX",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_debtor(payload, db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Debitor"


def test_update_debtor_rejects_invalid_country_before_update_sql():
    payload = DebtorUpdate(country="XX")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(update_debtor("debtor-1", payload, db=DebtorUpdateDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Debitor"


def test_create_article_rejects_invalid_vat_before_db_access():
    payload = ArticleCreate(
        tenant_id="tenant-1",
        article_number="ART-001",
        name="Weizen",
        unit="KG",
        category="getreide",
        sales_price=Decimal("25.00"),
        mehrwertsteuer_prozent=Decimal("25.0"),
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_article(payload, tenant_id="tenant-1", db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Artikel"


def test_update_article_rejects_invalid_vat_before_commit():
    article = type(
        "ArticleStub",
        (),
        {
            "id": "art-1",
            "tenant_id": "tenant-1",
            "article_number": "ART-001",
            "name": "Weizen",
            "unit": "KG",
            "mehrwertsteuer_prozent": Decimal("7.0"),
            "barcode": None,
            "deleted_at": None,
            "is_active": True,
        },
    )()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            update_article(
                "art-1",
                ArticleUpdate(mehrwertsteuer_prozent=Decimal("25.0")),
                db=ArticleUpdateDB(article),
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Artikel"


def test_create_weighing_ticket_requires_contract_reference_before_db_access():
    payload = WeighingTicketCreate(
        ticket_number="WS-001",
        vehicle_plate="AB-CD 1234",
        gross_weight=30000.0,
        tare_weight=5000.0,
        reference_doc=None,
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_weighing_ticket(payload, db=FailDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Wiegeschein"


def test_update_weighing_ticket_rejects_missing_vehicle_plate_before_commit():
    ticket = type(
        "TicketStub",
        (),
        {
            "id": "wt-1",
            "ticket_number": "WS-001",
            "reference_doc": "K-001",
            "vehicle_plate": "AB-CD 1234",
            "gross_weight": 30000.0,
            "tare_weight": 5000.0,
            "net_weight": 25000.0,
            "billing_weight": 25000.0,
            "moisture_pct": None,
            "impurities_pct": None,
            "quality_data": None,
        },
    )()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(update_weighing_ticket("wt-1", WeighingTicketUpdate(vehicle_plate=""), db=WeighingUpdateDB(ticket)))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Wiegeschein"
