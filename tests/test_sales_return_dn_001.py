"""SALES-RETURN-001 — Retoure anlegen → delivery_notes.status='returned' + Invoice GUTGESCHRIEBEN."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


TENANT = "00000000-0000-0000-0000-000000000001"


def _make_payload(dn_ref: str | None = "LS-2026-001", inv_ref: str | None = "RG-2026-100"):
    p = MagicMock()
    p.tenant_id = TENANT
    p.customer_id = "CUST-001"
    p.customer_name = "Testkunde"
    p.return_number = "RET-2026-001"
    p.delivery_note_reference = dn_ref
    p.invoice_reference = inv_ref
    p.reason = "Beschädigt"
    p.return_type = "Retoure"
    p.status = "draft"
    p.notes = ""
    p.model_dump = lambda exclude=None: {
        k: v for k, v in {
            "customer_id": "CUST-001", "customer_name": "Testkunde",
            "return_number": "RET-2026-001", "delivery_note_reference": dn_ref,
            "invoice_reference": inv_ref, "reason": "Beschädigt",
            "return_type": "Retoure", "status": "draft", "notes": "",
        }.items() if not exclude or k not in exclude
    }
    return p


class TestSalesReturnBelegbruch:
    @pytest.mark.asyncio
    async def test_delivery_note_wird_returned(self):
        """Retoure mit DN-Ref → delivery_notes UPDATE ausgeführt."""
        from app.api.v1.endpoints.sales_credit_notes import create_return

        db = MagicMock()

        with (
            patch("app.api.v1.endpoints.sales_credit_notes.assert_customer_allowed_for_delivery"),
            patch("app.api.v1.endpoints.sales_credit_notes.get_repository", return_value=None),
            patch("app.api.v1.endpoints.sales_credit_notes.get_from_store", return_value={"status": "delivered"}),
            patch("app.api.v1.endpoints.sales_credit_notes.save_to_store"),
            patch("app.api.v1.endpoints.sales_credit_notes.uuid7", return_value="RET-UUID-001"),
        ):
            await create_return(payload=_make_payload(), tenant_id=TENANT, db=db)

        all_sqls = [str(c.args[0]) for c in db.execute.call_args_list]
        dn_updates = [s for s in all_sqls if "delivery_notes" in s and "returned" in s]
        assert len(dn_updates) > 0

    @pytest.mark.asyncio
    async def test_invoice_wird_gutgeschrieben_bei_retoure(self):
        """Retoure mit Rechnungsreferenz → save_to_store mit GUTGESCHRIEBEN."""
        from app.api.v1.endpoints.sales_credit_notes import create_return

        db = MagicMock()
        invoice_data = {"status": "OFFEN"}

        with (
            patch("app.api.v1.endpoints.sales_credit_notes.assert_customer_allowed_for_delivery"),
            patch("app.api.v1.endpoints.sales_credit_notes.get_repository", return_value=None),
            patch("app.api.v1.endpoints.sales_credit_notes.get_from_store", return_value=invoice_data),
            patch("app.api.v1.endpoints.sales_credit_notes.save_to_store") as mock_save,
            patch("app.api.v1.endpoints.sales_credit_notes.uuid7", return_value="RET-UUID-002"),
        ):
            await create_return(payload=_make_payload(dn_ref=None), tenant_id=TENANT, db=db)

        assert mock_save.called
        saved = mock_save.call_args[0][2]
        assert saved["status"] == "GUTGESCHRIEBEN"
