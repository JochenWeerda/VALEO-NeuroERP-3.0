"""FIN-STORNO-001 — storno_invoice → sales_invoice.status = 'STORNIERT' im Store."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


TENANT = "00000000-0000-0000-0000-000000000001"


class TestFinStornoStoreBelegbruch:
    @pytest.mark.asyncio
    async def test_invoice_wird_storniert_im_store(self):
        """storno_invoice setzt Rechnungsdokument im Store auf STORNIERT."""
        from app.api.v1.endpoints.finance_invoices import storno_invoice

        db = MagicMock()
        # journal_entry row
        je_row = MagicMock()
        je_row.__getitem__ = lambda self, i: ("JE-001", "booked")[i]
        je_row.__iter__ = lambda self: iter(("JE-001", "booked"))
        db.execute.return_value.fetchone.return_value = (je_row[0], "booked")

        invoice_data = {"status": "GEBUCHT", "number": "RG-2026-200"}

        reversal_mock = MagicMock()
        reversal_mock.id = "REV-001"

        with (
            patch("app.api.v1.endpoints.finance_invoices.FinanceTransactionService") as mock_svc,
            patch("app.api.v1.endpoints.finance_invoices._resolve_open_items_table", return_value="domain_erp.offene_posten"),
            patch("app.api.v1.endpoints.finance_invoices.get_repository", return_value=None),
            patch("app.api.v1.endpoints.finance_invoices.get_from_store", return_value=invoice_data),
            patch("app.api.v1.endpoints.finance_invoices.save_to_store") as mock_save,
            patch("app.api.v1.endpoints.finance_invoices.log_fibu_audit"),
        ):
            mock_svc.return_value.reverse.return_value = (MagicMock(id="JE-001"), reversal_mock)
            result = await storno_invoice(invoice_number="RG-2026-200", tenant_id=TENANT, db=db)

        assert result["ok"] is True
        assert mock_save.called
        saved = mock_save.call_args[0][2]
        assert saved["status"] == "STORNIERT"
