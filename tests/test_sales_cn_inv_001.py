"""SALES-CN-INV-001 — Gutschrift anlegen → sales_invoice.status = 'GUTGESCHRIEBEN'."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


TENANT = "00000000-0000-0000-0000-000000000001"


def _make_payload(invoice_ref: str | None = "RG-2026-100"):
    p = MagicMock()
    p.tenant_id = TENANT
    p.customer_id = "CUST-001"
    p.customer_name = "Testkunde"
    p.invoice_reference = invoice_ref
    p.reason = "Retoure"
    p.total_amount = 500.0
    p.currency = "EUR"
    p.status = "draft"
    p.notes = ""
    p.lines = []
    p.credit_note_number = "GS-2026-001"
    return p


class TestSalesCnInvBelegbruch:
    @pytest.mark.asyncio
    async def test_invoice_wird_gutgeschrieben(self):
        """Wenn invoice_reference gesetzt → sales_invoice bekommt GUTGESCHRIEBEN."""
        from app.api.v1.endpoints.sales_credit_notes import create_credit_note

        db = MagicMock()
        request = MagicMock()
        invoice_data = {"status": "OFFEN", "number": "RG-2026-100"}

        with (
            patch("app.api.v1.endpoints.sales_credit_notes.assert_customer_allowed_for_invoice"),
            patch("app.api.v1.endpoints.sales_credit_notes.get_repository", return_value=None),
            patch("app.api.v1.endpoints.sales_credit_notes.get_from_store", return_value=invoice_data),
            patch("app.api.v1.endpoints.sales_credit_notes.save_to_store") as mock_save,
            patch("app.api.v1.endpoints.sales_credit_notes.log_fibu_audit"),
            patch("app.api.v1.endpoints.sales_credit_notes.uuid7", return_value="CN-UUID-001"),
        ):
            await create_credit_note(payload=_make_payload("RG-2026-100"), request=request, tenant_id=TENANT, db=db)

        assert mock_save.called
        saved_inv = mock_save.call_args[0][2]
        assert saved_inv["status"] == "GUTGESCHRIEBEN"

    @pytest.mark.asyncio
    async def test_kein_update_ohne_invoice_reference(self):
        """Ohne invoice_reference → kein save_to_store Aufruf."""
        from app.api.v1.endpoints.sales_credit_notes import create_credit_note

        db = MagicMock()
        request = MagicMock()

        with (
            patch("app.api.v1.endpoints.sales_credit_notes.assert_customer_allowed_for_invoice"),
            patch("app.api.v1.endpoints.sales_credit_notes.get_repository", return_value=None),
            patch("app.api.v1.endpoints.sales_credit_notes.get_from_store", return_value=None),
            patch("app.api.v1.endpoints.sales_credit_notes.save_to_store") as mock_save,
            patch("app.api.v1.endpoints.sales_credit_notes.log_fibu_audit"),
            patch("app.api.v1.endpoints.sales_credit_notes.uuid7", return_value="CN-UUID-002"),
        ):
            await create_credit_note(payload=_make_payload(None), request=request, tenant_id=TENANT, db=db)

        assert not mock_save.called
