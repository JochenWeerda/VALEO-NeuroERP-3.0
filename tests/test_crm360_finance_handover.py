from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.api.v1.endpoints.finance_invoices import _post_sales_invoice_financials
from app.documents.models import SalesInvoice
from app.services.sales_posting_service import SalesPostingService


class Result:
    def __init__(self, *, row=None, mapping=None):
        self._row = row
        self._mapping = mapping

    def first(self):
        return self._mapping if self._mapping is not None else self._row

    def mappings(self):
        return self

    def __iter__(self):
        return iter(())


def test_sales_invoice_posting_creates_posted_journal_and_open_item() -> None:
    db = MagicMock()
    db.execute.side_effect = [
        Result(mapping=None),
        Result(row=("account-1200",)),
        Result(row=("account-8400",)),
        Result(row=("CRM360 Testkunde",)),
        Result(row=None),
        Result(),
    ]
    service = SalesPostingService(db, "tenant-1")
    service._fin = MagicMock()
    service._fin.create.return_value = SimpleNamespace(id="journal-1")

    result = service.post_ausgangsrechnung_with_op(
        invoice_number="SIV-UAT-001",
        invoice_date=date(2026, 6, 9),
        customer_id="customer-1",
        net_amount=Decimal("20.00"),
        tax_amount=Decimal("0.00"),
        gross_amount=Decimal("20.00"),
        posted_by="technical-actor",
    )

    assert result["journal_entry_id"] == "journal-1"
    assert result["open_item_id"]
    service._fin.create.assert_called_once()
    service._fin.post.assert_called_once_with("journal-1", "technical-actor")
    assert "INSERT INTO domain_erp.offene_posten" in str(db.execute.call_args_list[-1].args[0])


def test_sales_invoice_reversal_reverses_journal_and_closes_open_item() -> None:
    db = MagicMock()
    db.execute.side_effect = [
        Result(mapping={"id": "journal-1", "status": "posted"}),
        Result(),
    ]
    service = SalesPostingService(db, "tenant-1")
    service._fin = MagicMock()
    service._fin.reverse.return_value = (
        SimpleNamespace(id="journal-1"),
        SimpleNamespace(id="reversal-1"),
    )

    result = service.reverse_ausgangsrechnung(
        invoice_number="SIV-UAT-001",
        reason="UAT compensation",
    )

    assert result == {
        "journal_entry_id": "journal-1",
        "reversal_entry_id": "reversal-1",
    }
    service._fin.reverse.assert_called_once_with(
        "journal-1", reason="UAT compensation"
    )
    update_sql = str(db.execute.call_args_list[-1].args[0])
    assert "op_status = 'storniert'" in update_sql
    assert "offen = 0" in update_sql


def test_finance_invoice_endpoint_delegates_to_shared_posting_service(monkeypatch) -> None:
    posting = MagicMock()
    posting.post_ausgangsrechnung_with_op.return_value = {
        "journal_entry_id": "journal-1",
        "open_item_id": "op-1",
    }
    monkeypatch.setattr(
        "app.api.v1.endpoints.finance_invoices.SalesPostingService",
        lambda _db, _tenant_id: posting,
    )
    invoice = SalesInvoice(
        number="SIV-UAT-002",
        date="2026-06-09",
        dueDate="2026-07-09",
        customerId="customer-1",
        subtotalNet=20,
        totalTax=0,
        totalGross=20,
    )

    result = _post_sales_invoice_financials(MagicMock(), invoice, "tenant-1")

    assert result["journal_entry_id"] == "journal-1"
    posting.post_ausgangsrechnung_with_op.assert_called_once_with(
        invoice_number="SIV-UAT-002",
        invoice_date="2026-06-09",
        customer_id="customer-1",
        net_amount=20.0,
        tax_amount=0.0,
        gross_amount=20.0,
        due_date="2026-07-09",
    )
