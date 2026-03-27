from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal

from app.api.v1.endpoints.agrar_settlements import SettlementCreate, _to_out, create_settlement
from app.infrastructure.models import AgrarSettlement, AgrarSettlementDeduction


class _FakeSettlementQuery:
    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return None


class _FakeDeductionQuery:
    def __init__(self, db: "_FakeDb"):
        self.db = db

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return [obj for obj in self.db.added if isinstance(obj, AgrarSettlementDeduction)]


class _FakeDb:
    def __init__(self):
        self.added: list[object] = []

    def query(self, model):
        if model is AgrarSettlement:
            return _FakeSettlementQuery()
        if model is AgrarSettlementDeduction:
            return _FakeDeductionQuery(self)
        raise AssertionError(f"unexpected model {model}")

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return obj


@dataclass
class _SettlementStub:
    id: str = "set-1"
    settlement_number: str = "SET-1"
    campaign_id: str | None = "camp-1"
    contract_id: str | None = None
    ticket_id: str | None = None
    supplier_id: str = "SUP-1"
    article_id: str | None = "WEIZEN"
    gross_quantity_kg: Decimal = Decimal("1000.000")
    billing_quantity_kg: Decimal = Decimal("950.000")
    unit_price_eur_per_ton: Decimal = Decimal("220.0000")
    gross_amount_eur: Decimal = Decimal("250.00")
    total_deductions_eur: Decimal = Decimal("10.00")
    net_amount_eur: Decimal = Decimal("240.00")
    currency: str = "EUR"
    status: str = "draft"
    posted_journal_ref: str | None = None
    posted_at: object | None = None
    note: str | None = None
    drying_result: dict | None = None
    row_version: int = 1


def test_create_settlement_persists_campaign_reference():
    db = _FakeDb()
    payload = SettlementCreate(
        settlement_number="SET-001",
        campaign_id="camp-1",
        supplier_id="SUP-1",
        gross_quantity_kg=1000.0,
        billing_quantity_kg=950.0,
        unit_price_eur_per_ton=220.0,
    )

    result = asyncio.run(create_settlement(payload, tenant_id="tenant-1", db=db))

    persisted = next(obj for obj in db.added if isinstance(obj, AgrarSettlement))
    assert persisted.campaign_id == "camp-1"
    assert result.campaign_id == "camp-1"


def test_to_out_exposes_campaign_reference():
    out = _to_out(_SettlementStub(), [])

    assert out.campaign_id == "camp-1"
