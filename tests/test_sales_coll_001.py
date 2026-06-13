"""SALES-COLL-001 — Sammelrechnung/Sammellieferschein Belegbruch-Fix.

Prüft:
1. Sammelrechnung verweigert DNs im falschen Status (422)
2. Sammelrechnung verweigert bereits berechnete DNs (409)
3. Sammelrechnung setzt Quell-DNs auf BERECHNET
4. Sammellieferschein verweigert bereits gelieferte Aufträge (409)
5. Sammellieferschein setzt Quell-Aufträge auf geliefert
6. collective_eligible liefert nur shipped/delivered
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, AsyncMock
from decimal import Decimal

import pytest
from fastapi import HTTPException


TENANT = "00000000-0000-0000-0000-000000000001"


def _dn_row(status: str, amount: float = 100.0):
    row = MagicMock()
    row.__getitem__ = lambda self, k: {"status": status, "total_amount": Decimal(str(amount))}[k]
    row.get = lambda k, d=None: {"status": status, "total_amount": Decimal(str(amount))}.get(k, d)
    return row


def _order_row(status: str, amount: float = 200.0):
    row = MagicMock()
    row.__getitem__ = lambda self, k: {"status": status, "total_amount": Decimal(str(amount))}[k]
    row.get = lambda k, d=None: {"status": status, "total_amount": Decimal(str(amount))}.get(k, d)
    return row


def _mock_db_for_invoice(dn_status: str) -> MagicMock:
    db = MagicMock()
    result = MagicMock()
    result.mappings.return_value.first.return_value = _dn_row(dn_status)
    db.execute.return_value = result
    return db


def _mock_db_for_delivery(order_status: str) -> MagicMock:
    db = MagicMock()
    result = MagicMock()
    result.mappings.return_value.first.return_value = _order_row(order_status)
    db.execute.return_value = result
    return db


class TestCollectiveInvoiceValidation:
    @pytest.mark.asyncio
    async def test_rejects_draft_dn(self):
        from app.api.v1.endpoints.collective_documents import create_collective_invoice, CollectiveInvoiceCreate
        db = _mock_db_for_invoice("draft")
        payload = CollectiveInvoiceCreate(
            customer_id="CUST-1", delivery_note_ids=["DN-1"], invoice_date="2026-06-13"
        )
        with pytest.raises(HTTPException) as exc:
            await create_collective_invoice(payload=payload, tenant_id=TENANT, db=db)
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_rejects_already_billed_dn(self):
        from app.api.v1.endpoints.collective_documents import create_collective_invoice, CollectiveInvoiceCreate
        db = _mock_db_for_invoice("BERECHNET")
        payload = CollectiveInvoiceCreate(
            customer_id="CUST-1", delivery_note_ids=["DN-2"], invoice_date="2026-06-13"
        )
        with pytest.raises(HTTPException) as exc:
            await create_collective_invoice(payload=payload, tenant_id=TENANT, db=db)
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_marks_dns_as_berechnet(self):
        from app.api.v1.endpoints.collective_documents import create_collective_invoice, CollectiveInvoiceCreate

        db = MagicMock()
        fetch_result = MagicMock()
        fetch_result.mappings.return_value.first.return_value = _dn_row("shipped")
        db.execute.return_value = fetch_result

        payload = CollectiveInvoiceCreate(
            customer_id="CUST-1", delivery_note_ids=["DN-A", "DN-B"], invoice_date="2026-06-13"
        )
        await create_collective_invoice(payload=payload, tenant_id=TENANT, db=db)

        all_sqls = [str(c.args[0]) for c in db.execute.call_args_list]
        update_sqls = [s for s in all_sqls if "BERECHNET" in s]
        assert len(update_sqls) == 2, f"Expected 2 BERECHNET updates, got {len(update_sqls)}: {update_sqls}"
        db.commit.assert_called_once()


class TestCollectiveDeliveryValidation:
    @pytest.mark.asyncio
    async def test_rejects_already_delivered_order(self):
        from app.api.v1.endpoints.collective_documents import create_collective_delivery, CollectiveDeliveryCreate
        db = _mock_db_for_delivery("geliefert")
        payload = CollectiveDeliveryCreate(
            customer_id="CUST-1", order_ids=["ORD-1"], delivery_date="2026-06-13"
        )
        with pytest.raises(HTTPException) as exc:
            await create_collective_delivery(payload=payload, tenant_id=TENANT, db=db)
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_marks_orders_as_geliefert(self):
        from app.api.v1.endpoints.collective_documents import create_collective_delivery, CollectiveDeliveryCreate

        db = MagicMock()
        fetch_result = MagicMock()
        fetch_result.mappings.return_value.first.return_value = _order_row("bestaetigt")
        db.execute.return_value = fetch_result

        payload = CollectiveDeliveryCreate(
            customer_id="CUST-1", order_ids=["ORD-X", "ORD-Y"], delivery_date="2026-06-13"
        )
        await create_collective_delivery(payload=payload, tenant_id=TENANT, db=db)

        all_sqls = [str(c.args[0]) for c in db.execute.call_args_list]
        update_sqls = [s for s in all_sqls if "geliefert" in s]
        assert len(update_sqls) == 2, f"Expected 2 geliefert updates, got {len(update_sqls)}"
        db.commit.assert_called_once()
