"""Unit tests for GoBD booking integration points.

Covers:
- SalesPostingService.book_warenabgang
- SalesPostingService.book_ausgangsrechnung
- ProcurementService._book_bestellung_obligo (via freigebe_bestellung)
- EinkaufCompatService._book_wareneingang (via create_goods_receipt)
- storno_invoice endpoint logic (FinanceTransactionService.reverse round-trip)
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch, call

import pytest

from app.core.exceptions import ValidationFailedError
from app.services.sales_posting_service import SalesPostingService, _coerce_date
from app.services.finance_transaction_service import FinanceTransactionService


TENANT = "tenant-test"


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_fin_mock():
    """Return a mock FinanceTransactionService whose create() records args."""
    fin = MagicMock(spec=FinanceTransactionService)
    fin.create.return_value = MagicMock(id="je-001", entry_number="WA-LS-001")
    return fin


def _make_svc(fin_mock=None):
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (1,)
    svc = SalesPostingService(db, TENANT)
    if fin_mock is not None:
        svc._fin = fin_mock
    return svc


# ── _coerce_date ──────────────────────────────────────────────────────────────

def test_coerce_date_from_date():
    d = date(2026, 3, 15)
    assert _coerce_date(d) == d


def test_coerce_date_from_str():
    assert _coerce_date("2026-03-15") == date(2026, 3, 15)


def test_coerce_date_from_datetime():
    # datetime is a subclass of date — _coerce_date returns it as-is (still compares equal to date)
    dt = datetime(2026, 3, 15, 10, 0, 0)
    result = _coerce_date(dt)
    assert result.year == 2026 and result.month == 3 and result.day == 15


def test_coerce_date_none():
    assert _coerce_date(None) is None


def test_coerce_date_invalid():
    assert _coerce_date("not-a-date") is None


# ── book_warenabgang — skip on zero cost ──────────────────────────────────────

def test_warenabgang_skips_zero_cost():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang("dn-1", "LS-001", [{"qty": 10, "unit_price": 0}])
    fin.create.assert_not_called()


def test_warenabgang_skips_empty_positions():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang("dn-1", "LS-001", [])
    fin.create.assert_not_called()


# ── book_warenabgang — creates correct JournalEntry ──────────────────────────

def test_warenabgang_creates_entry_with_correct_accounts():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang(
        "dn-1", "LS-001",
        [{"qty": 5, "unit_price": 100}],
        delivery_date="2026-03-15",
    )
    fin.create.assert_called_once()
    kwargs = fin.create.call_args.kwargs
    assert kwargs["entry_number"] == "WA-LS-001"
    assert kwargs["reference"] == "LS-001"
    assert kwargs["source"] == "delivery_note"
    assert kwargs["period"] == "2026-03"
    lines = kwargs["lines"]
    assert len(lines) == 2
    debit_line = next(l for l in lines if l["debit_amount"] > 0)
    credit_line = next(l for l in lines if l["credit_amount"] > 0)
    assert debit_line["account_id"] == SalesPostingService.ACCOUNT_COGS   # 7000
    assert credit_line["account_id"] == SalesPostingService.ACCOUNT_INVENTORY  # 2000
    assert debit_line["debit_amount"] == pytest.approx(500.0)
    assert credit_line["credit_amount"] == pytest.approx(500.0)


def test_warenabgang_aggregates_multiple_positions():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    positions = [
        {"menge": 3, "einstandspreis": 10},
        {"menge": 2, "einstandspreis": 25},
    ]
    svc.book_warenabgang("dn-1", "LS-002", positions, delivery_date="2026-03-15")
    kwargs = fin.create.call_args.kwargs
    lines = kwargs["lines"]
    total = next(l for l in lines if l["debit_amount"] > 0)["debit_amount"]
    assert total == pytest.approx(80.0)  # 3*10 + 2*25


def test_warenabgang_uses_fallback_field_names():
    """Accepts 'quantity'/'cost_price' field names as well as 'qty'/'unit_price'."""
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang("dn-1", "LS-003",
                         [{"quantity": 4, "cost_price": 50}],
                         delivery_date="2026-01-10")
    kwargs = fin.create.call_args.kwargs
    total = next(l for l in kwargs["lines"] if l["debit_amount"] > 0)["debit_amount"]
    assert total == pytest.approx(200.0)


def test_warenabgang_falls_back_to_today_when_no_date():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang("dn-1", "LS-004", [{"qty": 1, "unit_price": 50}])
    kwargs = fin.create.call_args.kwargs
    assert kwargs["entry_date"] == date.today()


# ── book_ausgangsrechnung ─────────────────────────────────────────────────────

def test_ausgangsrechnung_skips_zero_gross():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_ausgangsrechnung("RE-001", "2026-03-01", 0, 0, 0)
    fin.create.assert_not_called()


def test_ausgangsrechnung_without_tax_creates_two_lines():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_ausgangsrechnung("RE-001", "2026-03-01", net_amount=100, tax_amount=0, gross_amount=100)
    kwargs = fin.create.call_args.kwargs
    assert len(kwargs["lines"]) == 2
    assert kwargs["entry_number"] == "AR-RE-001"
    assert kwargs["source"] == "sales_invoice"


def test_ausgangsrechnung_with_tax_creates_three_lines():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_ausgangsrechnung("RE-002", "2026-03-01", net_amount=100, tax_amount=19, gross_amount=119)
    kwargs = fin.create.call_args.kwargs
    lines = kwargs["lines"]
    assert len(lines) == 3
    accounts = {l["account_id"] for l in lines}
    assert SalesPostingService.ACCOUNT_RECEIVABLES in accounts  # 1200
    assert SalesPostingService.ACCOUNT_REVENUE in accounts      # 8400
    assert SalesPostingService.ACCOUNT_TAX in accounts          # 1776


def test_ausgangsrechnung_correct_amounts():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_ausgangsrechnung("RE-003", date(2026, 4, 1), 500, 95, 595)
    kwargs = fin.create.call_args.kwargs
    lines = kwargs["lines"]
    debit = next(l for l in lines if l.get("debit_amount", 0) > 0)
    assert debit["debit_amount"] == pytest.approx(595.0)
    assert kwargs["period"] == "2026-04"


# ── _book_bestellung_obligo ───────────────────────────────────────────────────

def _make_bestellung(netto_summe, bestellnummer="BE-001", bestelldatum=None):
    b = MagicMock()
    b.netto_summe = netto_summe
    b.bestellnummer = bestellnummer
    b.bestelldatum = bestelldatum or date(2026, 3, 10)
    return b


def test_obligo_skips_zero_netto():
    from app.services.procurement_service import ProcurementService
    db = MagicMock()
    svc = ProcurementService(db, TENANT)
    b = _make_bestellung(netto_summe=0)
    with patch.object(FinanceTransactionService, "create") as mock_create:
        svc._book_bestellung_obligo(b)
        mock_create.assert_not_called()


def test_obligo_creates_entry_correct_accounts():
    from app.services.procurement_service import ProcurementService
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (1,)
    svc = ProcurementService(db, TENANT)
    b = _make_bestellung(netto_summe=Decimal("1500.00"), bestellnummer="BE-042")

    with patch.object(FinanceTransactionService, "create", return_value=MagicMock(id="j1")) as mock_create:
        svc._book_bestellung_obligo(b)
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs["entry_number"] == "OBLIGO-BE-042"
        assert kwargs["source"] == "procurement"
        lines = kwargs["lines"]
        debit = next(l for l in lines if l["debit_amount"] > 0)
        credit = next(l for l in lines if l["credit_amount"] > 0)
        assert debit["account_id"] == "6000"
        assert credit["account_id"] == "1600"
        assert debit["debit_amount"] == pytest.approx(1500.0)
        assert credit["credit_amount"] == pytest.approx(1500.0)


def test_obligo_uses_bestelldatum_as_entry_date():
    from app.services.procurement_service import ProcurementService
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (1,)
    svc = ProcurementService(db, TENANT)
    b = _make_bestellung(netto_summe=Decimal("200"), bestelldatum=date(2026, 5, 20))

    with patch.object(FinanceTransactionService, "create", return_value=MagicMock(id="j2")) as mock_create:
        svc._book_bestellung_obligo(b)
        kwargs = mock_create.call_args.kwargs
        assert kwargs["entry_date"] == date(2026, 5, 20)
        assert kwargs["period"] == "2026-05"


# ── _book_wareneingang ────────────────────────────────────────────────────────

def _make_einkauf_svc():
    from app.services.einkauf_compat_service import EinkaufCompatService
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (1,)
    return EinkaufCompatService(db, TENANT)


def test_wareneingang_skips_zero_cost():
    svc = _make_einkauf_svc()
    with patch.object(FinanceTransactionService, "create") as mock_create:
        svc._book_wareneingang("r-001", "2026-03-01", [{"received_quantity": 5, "unit_cost": 0}])
        mock_create.assert_not_called()


def test_wareneingang_skips_empty_items():
    svc = _make_einkauf_svc()
    with patch.object(FinanceTransactionService, "create") as mock_create:
        svc._book_wareneingang("r-001", "2026-03-01", [])
        mock_create.assert_not_called()


def test_wareneingang_creates_entry_correct_accounts():
    svc = _make_einkauf_svc()
    items = [{"accepted_quantity": 10, "unit_cost": 20}]

    with patch.object(FinanceTransactionService, "create", return_value=MagicMock(id="j3")) as mock_create:
        svc._book_wareneingang("receipt-abc123", "2026-03-15", items)
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["source"] == "goods_receipt"
        assert kwargs["period"] == "2026-03"
        lines = kwargs["lines"]
        debit = next(l for l in lines if l["debit_amount"] > 0)
        credit = next(l for l in lines if l["credit_amount"] > 0)
        assert debit["account_id"] == "2000"
        assert credit["account_id"] == "1600"
        assert debit["debit_amount"] == pytest.approx(200.0)


def test_wareneingang_accepts_alternative_field_names():
    """Handles receivedQuantity/unitPrice as well as accepted_quantity/unit_cost."""
    svc = _make_einkauf_svc()
    items = [{"receivedQuantity": 3, "unitPrice": 50}]

    with patch.object(FinanceTransactionService, "create", return_value=MagicMock(id="j4")) as mock_create:
        svc._book_wareneingang("r-002", "2026-04-01", items)
        kwargs = mock_create.call_args.kwargs
        total = next(l for l in kwargs["lines"] if l["debit_amount"] > 0)["debit_amount"]
        assert total == pytest.approx(150.0)


def test_wareneingang_is_nonblocking_on_finance_error():
    """Finance booking failure must not propagate — receipt creation must succeed."""
    svc = _make_einkauf_svc()
    items = [{"accepted_quantity": 5, "unit_cost": 10}]

    with patch.object(FinanceTransactionService, "create", side_effect=RuntimeError("DB down")):
        # Should NOT raise
        svc._book_wareneingang("r-003", "2026-05-01", items)


# ── SalesPostingService — non-blocking delivery note booking ──────────────────

def test_warenabgang_is_nonblocking_on_finance_error():
    """book_warenabgang itself raises — caller (endpoint) wraps in try/except."""
    fin = _make_fin_mock()
    fin.create.side_effect = RuntimeError("DB down")
    svc = _make_svc(fin)
    # The service itself propagates — the endpoint wraps it
    with pytest.raises(RuntimeError, match="DB down"):
        svc.book_warenabgang("dn-1", "LS-005", [{"qty": 1, "unit_price": 100}])


# ── FinanceTransactionService.reverse — storno round-trip ────────────────────

def _make_posted_entry(entry_id="e-posted"):
    entry = MagicMock()
    entry.id = entry_id
    entry.tenant_id = TENANT
    entry.status = "posted"
    entry.entry_number = f"AR-RE-{entry_id}"
    entry.description = "Ausgangsrechnung"
    entry.reference = "RE-001"
    entry.entry_date = datetime(2026, 3, 1)
    entry.total_debit = Decimal("119")
    entry.total_credit = Decimal("119")
    entry.sequence_number = 5
    entry.hash_current = "abc"
    entry.hash_prev = None
    entry.document_type = "AR_INVOICE"
    entry.reversed_entry_id = None
    return entry


def test_storno_reverse_sets_original_to_reversed():
    """FinanceTransactionService.reverse() marks original as 'reversed'."""
    original = _make_posted_entry("e-orig")

    line = MagicMock()
    line.account_id = "1200"
    line.debit = Decimal("119")
    line.credit = Decimal("0")
    line.description = "Forderung"

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = original
    db.query.return_value.filter.return_value.all.return_value = [line]
    db.execute.return_value.fetchone.return_value = (6,)

    added = []
    db.add.side_effect = lambda obj: added.append(obj)

    svc = FinanceTransactionService(db, TENANT)
    with patch("app.services.finance_transaction_service.JournalEntry") as MockEntry, \
         patch("app.services.finance_transaction_service.JournalEntryLine"):
        mock_reversal = MagicMock()
        mock_reversal.id = "e-rev"
        mock_reversal.sequence_number = None
        mock_reversal.hash_current = None
        MockEntry.return_value = mock_reversal

        orig_out, rev_out = svc.reverse("e-orig", reason="Storno RE-001")

    assert original.status == "reversed"
    db.commit.assert_called_once()


def test_storno_reverse_raises_on_draft():
    """Cannot reverse a draft entry."""
    entry = MagicMock()
    entry.status = "draft"
    entry.tenant_id = TENANT

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    db.execute.return_value.fetchone.return_value = (1,)

    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(ValidationFailedError):
        svc.reverse("e-draft")


def test_storno_reversal_lines_are_swapped():
    """Reversal entry lines have debit/credit swapped vs original."""
    original = _make_posted_entry("e-swap")

    line = MagicMock()
    line.account_id = "1200"
    line.debit = Decimal("595")
    line.credit = Decimal("0")
    line.description = "Forderung"

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = original
    db.query.return_value.filter.return_value.all.return_value = [line]
    db.execute.return_value.fetchone.return_value = (7,)

    line_kwargs_captured = []

    def capture_line(**kwargs):
        line_kwargs_captured.append(kwargs)
        return MagicMock()

    db.add.return_value = None

    svc = FinanceTransactionService(db, TENANT)
    with patch("app.services.finance_transaction_service.JournalEntry") as MockEntry, \
         patch("app.services.finance_transaction_service.JournalEntryLine") as MockLine:
        mock_rev = MagicMock()
        mock_rev.id = "e-rev"
        mock_rev.sequence_number = None
        mock_rev.hash_current = None
        MockEntry.return_value = mock_rev
        MockLine.side_effect = lambda **kw: (line_kwargs_captured.append(kw), MagicMock())[1]

        svc.reverse("e-swap", reason="test")

    assert len(line_kwargs_captured) == 1
    rev_line = line_kwargs_captured[0]
    # Debit and credit are swapped
    assert rev_line["debit"] == line.credit    # 0
    assert rev_line["credit"] == line.debit    # 595
