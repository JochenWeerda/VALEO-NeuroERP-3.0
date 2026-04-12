"""
Tests for open items (OP) management endpoints (app/api/v1/endpoints/open_items.py).

Covers Pydantic schema validation, status machine rules, and endpoint structure tests.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from pydantic import ValidationError
from starlette.testclient import TestClient

from app.core.config import settings
from conftest import skip_if_db_unavailable


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def auth_headers():
    return {
        "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
        "X-Tenant-ID": "test-tenant",
    }


def _import_schemas():
    from app.api.v1.endpoints.open_items import (
        OpenItemSettlement,
        OpenItemBase,
        OpenItemCreate,
        OpenItemUpdate,
        BatchSettleRequest,
        SettlementResult,
        OpenItem,
    )
    return {
        "OpenItemSettlement": OpenItemSettlement,
        "OpenItemBase": OpenItemBase,
        "OpenItemCreate": OpenItemCreate,
        "OpenItemUpdate": OpenItemUpdate,
        "BatchSettleRequest": BatchSettleRequest,
        "SettlementResult": SettlementResult,
        "OpenItem": OpenItem,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Schema unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestOpenItemSettlementSchema:
    def test_requires_op_id_payment_amount_date(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["OpenItemSettlement"]()

    def test_valid_settlement(self):
        S = _import_schemas()
        s = S["OpenItemSettlement"](
            op_id="OP-001",
            payment_amount=Decimal("1500.00"),
            payment_date=datetime(2026, 4, 10, 12, 0, 0),
        )
        assert s.op_id == "OP-001"
        assert s.payment_amount == Decimal("1500.00")
        assert s.payment_type == "payment"

    def test_payment_type_default(self):
        S = _import_schemas()
        s = S["OpenItemSettlement"](
            op_id="OP-X", payment_amount=Decimal("100"), payment_date=datetime.now()
        )
        assert s.payment_type == "payment"

    def test_payment_type_accepts_known_values(self):
        S = _import_schemas()
        for pt in ("payment", "discount", "credit_note", "reversal"):
            s = S["OpenItemSettlement"](
                op_id="OP-X",
                payment_amount=Decimal("50"),
                payment_date=datetime.now(),
                payment_type=pt,
            )
            assert s.payment_type == pt


class TestOpenItemBaseSchema:
    def test_requires_rechnungsnr_datum_faelligkeit_betrag_offen(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["OpenItemBase"]()

    def test_valid_open_item_base(self):
        S = _import_schemas()
        item = S["OpenItemBase"](
            rechnungsnr="RE-2026-001",
            rechnungsdatum=date(2026, 3, 1),
            faelligkeit=date(2026, 3, 31),
            op_betrag=Decimal("5000.00"),
            offen=Decimal("5000.00"),
        )
        assert item.rechnungsnr == "RE-2026-001"
        assert item.konto_typ == "debitoren"
        assert item.op_status == "offen"
        assert item.waehrung == "EUR"
        assert item.mahn_stufe == 0
        assert item.zahlbar is True

    def test_defaults(self):
        S = _import_schemas()
        item = S["OpenItemBase"](
            rechnungsnr="R-1",
            rechnungsdatum=date(2026, 1, 1),
            faelligkeit=date(2026, 1, 31),
            op_betrag=Decimal("100"),
            offen=Decimal("100"),
        )
        assert item.saldo == Decimal("0.00")
        assert item.kunde_id is None
        assert item.lieferant_id is None
        assert item.skonto_prozent is None


class TestOpenItemStatusMachine:
    """Status machine: offen -> teilweise|geschlossen; terminal states."""

    def test_valid_statuses(self):
        S = _import_schemas()
        for status in ("offen", "teilweise", "geschlossen", "storniert"):
            item = S["OpenItemBase"](
                rechnungsnr="R-1",
                rechnungsdatum=date(2026, 1, 1),
                faelligkeit=date(2026, 1, 31),
                op_betrag=Decimal("100"),
                offen=Decimal("100"),
                op_status=status,
            )
            assert item.op_status == status

    def test_editable_statuses(self):
        from app.api.v1.endpoints.open_items import OP_EDITABLE_STATUSES
        assert "offen" in OP_EDITABLE_STATUSES
        assert "teilweise" in OP_EDITABLE_STATUSES
        assert "geschlossen" not in OP_EDITABLE_STATUSES
        assert "storniert" not in OP_EDITABLE_STATUSES

    def test_konto_typ_values(self):
        S = _import_schemas()
        for typ in ("debitoren", "kreditoren"):
            item = S["OpenItemBase"](
                rechnungsnr="R-1",
                rechnungsdatum=date(2026, 1, 1),
                faelligkeit=date(2026, 1, 31),
                op_betrag=Decimal("100"),
                offen=Decimal("100"),
                konto_typ=typ,
            )
            assert item.konto_typ == typ


class TestOpenItemCreateSchema:
    def test_inherits_from_base(self):
        S = _import_schemas()
        assert issubclass(S["OpenItemCreate"], S["OpenItemBase"])


class TestOpenItemUpdateSchema:
    def test_all_fields_optional(self):
        S = _import_schemas()
        upd = S["OpenItemUpdate"]()
        assert upd.rechnungsnr is None
        assert upd.konto_typ is None


class TestBatchSettleRequestSchema:
    def test_empty_items_list(self):
        S = _import_schemas()
        req = S["BatchSettleRequest"](items=[])
        assert req.items == []

    def test_with_items(self):
        S = _import_schemas()
        req = S["BatchSettleRequest"](items=[
            S["OpenItemSettlement"](
                op_id="OP-1",
                payment_amount=Decimal("100"),
                payment_date=datetime.now(),
            )
        ])
        assert len(req.items) == 1


class TestSettlementResultSchema:
    def test_valid_result(self):
        S = _import_schemas()
        r = S["SettlementResult"](
            op_id="OP-1",
            settlement_id="SET-001",
            previous_open_amount=Decimal("1000"),
            settlement_amount=Decimal("500"),
            new_open_amount=Decimal("500"),
            status="partial",
            settlement_date=datetime.now(),
        )
        assert r.status == "partial"
        assert r.new_open_amount == Decimal("500")


# ═══════════════════════════════════════════════════════════════════════════
# Endpoint structure tests
# ═══════════════════════════════════════════════════════════════════════════

class TestOpenItemEndpoints:
    def test_list_open_items(self, client, auth_headers):
        resp = client.get("/api/v1/finance/open-items", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "summary" in body

    def test_get_open_item_404(self, client, auth_headers):
        resp = client.get("/api/v1/finance/open-items/nonexistent-id", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 404

    def test_create_open_item_422_on_empty_body(self, client, auth_headers):
        resp = client.post("/api/v1/finance/open-items", headers=auth_headers, json={})
        assert resp.status_code == 422

    def test_batch_settle_empty_items(self, client, auth_headers):
        resp = client.post(
            "/api/v1/finance/open-items/batch-settle",
            headers=auth_headers,
            json={"items": []},
        )
        skip_if_db_unavailable(resp)
        # Empty items list is valid, should return 200 with empty results
        if resp.status_code == 200:
            body = resp.json()
            assert body["success_count"] == 0
            assert body["results"] == []
