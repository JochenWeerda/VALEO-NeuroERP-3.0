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
            patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=MagicMock()),
            patch("app.api.v1.endpoints.finance_invoices.get_from_store", return_value=None),
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
            patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=MagicMock()),
            patch("app.api.v1.endpoints.finance_invoices.get_from_store", return_value=None),
        ):
            await create_invoice(invoice=invoice, tenant_id=TENANT, db=db)

        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        dn_updates = [s for s in update_calls if "delivery_notes" in s and "invoice_number" in s]
        assert len(dn_updates) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("existing", [{"tenantId": TENANT}, {"tenantId": "other"}])
async def test_create_rejects_existing_number(existing):
    from app.api.v1.endpoints.finance_invoices import create_invoice
    repo, db = MagicMock(), MagicMock()
    with (patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=repo),
          patch("app.api.v1.endpoints.finance_invoices.get_from_store", return_value=existing),
          patch("app.api.v1.endpoints.finance_invoices.assert_customer_allowed_for_invoice")):
        with pytest.raises(HTTPException) as error:
            await create_invoice(_make_invoice_body(None), TENANT, db)
    assert error.value.status_code == 409
    repo.save_document.assert_not_called()
    db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_rejects_racing_duplicate():
    from app.api.v1.endpoints.finance_invoices import create_invoice
    from app.documents.repository import DocumentAlreadyExists
    repo, db = MagicMock(), MagicMock()
    repo.save_document.side_effect = DocumentAlreadyExists()
    with (patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=repo),
          patch("app.api.v1.endpoints.finance_invoices.get_from_store", return_value=None),
          patch("app.api.v1.endpoints.finance_invoices.assert_customer_allowed_for_invoice")):
        with pytest.raises(HTTPException) as error:
            await create_invoice(_make_invoice_body(None), TENANT, db)
    assert error.value.status_code == 409
    assert repo.save_document.call_args.kwargs == {"commit": False, "create_only": True}
    db.rollback.assert_called_once()
    db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_create_without_repository_fails_closed():
    from app.api.v1.endpoints.finance_invoices import create_invoice
    db = MagicMock()
    with (patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=None),
          patch("app.api.v1.endpoints.finance_invoices.get_from_store", return_value=None),
          patch("app.api.v1.endpoints.finance_invoices.assert_customer_allowed_for_invoice"),
          patch("app.api.v1.endpoints.finance_invoices.save_to_store") as save):
        with pytest.raises(HTTPException) as error:
            await create_invoice(_make_invoice_body(None), TENANT, db)
    assert error.value.status_code == 503
    save.assert_not_called()
    db.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_create_serializes_number_before_check():
    from app.api.v1.endpoints.finance_invoices import create_invoice
    repo, db = MagicMock(), MagicMock()
    events = []
    db.execute.side_effect = lambda statement, *args: events.append(str(statement)) or MagicMock()
    def read(*args):
        assert any("pg_advisory_xact_lock" in event for event in events)
        return None
    with (patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=repo),
          patch("app.api.v1.endpoints.finance_invoices.get_from_store", side_effect=read),
          patch("app.api.v1.endpoints.finance_invoices.assert_customer_allowed_for_invoice")):
        await create_invoice(_make_invoice_body(None), TENANT, db)
    assert any(call.args[1] == {"scope": "sales_invoice.create:RG-2026-100"}
               for call in db.execute.call_args_list if len(call.args) > 1)
