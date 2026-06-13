"""SALES-INV-DN-001 — SalesInvoice.sourceDelivery → delivery_notes.invoice_number befüllen."""
from __future__ import annotations

from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi import HTTPException


TENANT = "00000000-0000-0000-0000-000000000001"


def _make_invoice_body(source_delivery: str | None = "LS-001"):
    inv = MagicMock()
    inv.number = "RG-2026-100"
    inv.date = "2026-06-13"
    inv.customerId = "CUST-001"
    inv.sourceDelivery = source_delivery
    inv.sourceOrder = None
    inv.paymentTerms = "net30"
    inv.dueDate = "2026-07-13"
    inv.status = "ENTWURF"
    inv.notes = ""
    inv.lines = []
    inv.subtotalNet = 1000.0
    inv.totalTax = 190.0
    inv.totalGross = 1190.0
    inv.model_dump = lambda: {
        "number": inv.number, "date": inv.date, "customerId": inv.customerId,
        "sourceDelivery": inv.sourceDelivery, "status": inv.status,
        "totalGross": inv.totalGross,
    }
    return inv


class TestSalesInvoiceDNLink:
    @pytest.mark.asyncio
    async def test_delivery_note_invoice_number_wird_gesetzt(self):
        from app.api.v1.endpoints.finance_invoices import create_invoice

        db = MagicMock()
        invoice = _make_invoice_body("LS-001")

        with (
            patch("app.api.v1.endpoints.finance_invoices.assert_customer_allowed_for_invoice"),
            patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=None),
            patch("app.api.v1.endpoints.finance_invoices.save_to_store", return_value={"ok": True}),
        ):
            result = await create_invoice(invoice=invoice, tenant_id=TENANT, db=db)

        assert result["ok"] is True
        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        dn_updates = [s for s in update_calls if "delivery_notes" in s and "invoice_number" in s]
        assert len(dn_updates) > 0, "delivery_notes.invoice_number wurde nicht aktualisiert"

    @pytest.mark.asyncio
    async def test_kein_update_ohne_source_delivery(self):
        from app.api.v1.endpoints.finance_invoices import create_invoice

        db = MagicMock()
        invoice = _make_invoice_body(source_delivery=None)

        with (
            patch("app.api.v1.endpoints.finance_invoices.assert_customer_allowed_for_invoice"),
            patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=None),
            patch("app.api.v1.endpoints.finance_invoices.save_to_store", return_value={"ok": True}),
        ):
            await create_invoice(invoice=invoice, tenant_id=TENANT, db=db)

        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        dn_updates = [s for s in update_calls if "delivery_notes" in s and "invoice_number" in s]
        assert len(dn_updates) == 0
