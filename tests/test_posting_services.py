"""Unit tests for GoBD booking integration points.

Covers:
- SalesPostingService.book_warenabgang
- SalesPostingService.book_ausgangsrechnung
- HarvestAcceptanceService._book_self_billing_credit_note
- storno_invoice endpoint logic (FinanceTransactionService.reverse round-trip)
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

import pytest

from app.core.business_time import business_today
from app.core.exceptions import ValidationFailedError
from app.services.sales_posting_service import SalesPostingService, _coerce_date
from app.services.finance_transaction_service import FinanceTransactionService


TENANT = "tenant-test"


@pytest.fixture(autouse=True)
def explicit_account_identity(monkeypatch):
    monkeypatch.setattr(FinanceTransactionService, "check_period_open", lambda self, period: None)
    monkeypatch.setattr(FinanceTransactionService, "account_id_for_number", lambda self, number: "id-" + number)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_fin_mock():
    """Return a mock FinanceTransactionService whose create() records args."""
    fin = MagicMock(spec=FinanceTransactionService)
    fin.create.return_value = MagicMock(id="je-001", entry_number="WA-LS-001")
    fin.account_id_for_number.side_effect = lambda number: "id-" + number
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
    debit_line = next(line for line in lines if line["debit_amount"] > 0)
    credit_line = next(line for line in lines if line["credit_amount"] > 0)
    assert debit_line["account_id"] == "id-" + SalesPostingService.ACCOUNT_COGS   # 7000
    assert credit_line["account_id"] == "id-" + SalesPostingService.ACCOUNT_INVENTORY  # 2000
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
    total = next(line for line in lines if line["debit_amount"] > 0)["debit_amount"]
    assert total == pytest.approx(80.0)  # 3*10 + 2*25


def test_warenabgang_uses_fallback_field_names():
    """Accepts 'quantity'/'cost_price' field names as well as 'qty'/'unit_price'."""
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang("dn-1", "LS-003",
                         [{"quantity": 4, "cost_price": 50}],
                         delivery_date="2026-01-10")
    kwargs = fin.create.call_args.kwargs
    total = next(line for line in kwargs["lines"] if line["debit_amount"] > 0)["debit_amount"]
    assert total == pytest.approx(200.0)


def test_warenabgang_falls_back_to_business_day_when_no_date():
    """Fallback ist der Geschaeftstag in Betriebszeitzone, nicht das UTC-Datum.

    Mit UTC landete jede Buchung zwischen 00:00 und 02:00 Ortszeit auf dem
    Vortag — am Monatsersten in der Vorperiode.
    """
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_warenabgang("dn-1", "LS-004", [{"qty": 1, "unit_price": 50}])
    kwargs = fin.create.call_args.kwargs
    assert kwargs["entry_date"] == business_today()
    assert kwargs["period"] == business_today().strftime("%Y-%m")


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
    accounts = {line["account_id"] for line in lines}
    assert "id-" + SalesPostingService.ACCOUNT_RECEIVABLES in accounts  # 1200
    assert "id-" + SalesPostingService.ACCOUNT_REVENUE in accounts      # 8400
    assert "id-" + SalesPostingService.ACCOUNT_TAX in accounts          # 1776


def test_ausgangsrechnung_correct_amounts():
    fin = _make_fin_mock()
    svc = _make_svc(fin)
    svc.book_ausgangsrechnung("RE-003", date(2026, 4, 1), 500, 95, 595)
    kwargs = fin.create.call_args.kwargs
    lines = kwargs["lines"]
    debit = next(line for line in lines if line.get("debit_amount", 0) > 0)
    assert debit["debit_amount"] == pytest.approx(595.0)
    assert kwargs["period"] == "2026-04"


# ── HarvestAcceptanceService._book_self_billing_credit_note ──────────────────

def _make_harvest_svc(*, configured=False):
    from app.services.harvest_acceptance_service import HarvestAcceptanceService
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (1,)
    db.execute.return_value.scalar.return_value = "8" if configured else None
    svc = HarvestAcceptanceService(db, TENANT)
    return svc


def _make_invoice(net=100, vat=19, gross=119, number="SB-2026-001"):
    inv = MagicMock()
    inv.invoice_number = number
    inv.total_net_amount_eur = Decimal(str(net))
    inv.total_vat_amount_eur = Decimal(str(vat))
    inv.total_gross_amount_eur = Decimal(str(gross))
    inv.vat_rate_percent = Decimal("19") if vat else Decimal("0")
    return inv


@pytest.fixture
def self_billing_tax_contract(monkeypatch):
    from app.finance import steuerschluessel as taxes
    from app.services import finance_eingangsrechnung_buchung as accounting
    def groups(db, tenant, positions):
        assert tenant == TENANT and len(positions) == 1
        _, code, rate, net, _ = positions[0]
        assert code == "8"
        return [taxes.Vorsteuergruppe(tax_code=code, satz=rate, netto=net,
                steuer=net * rate / 100, aufwandskonto="4000", vorsteuerkonto="1576")]
    monkeypatch.setattr(taxes, "vorsteuergruppen", groups)
    monkeypatch.setattr(accounting, "kreditorenkonto", lambda *args: "3100")


def _patch_self_billing_path(monkeypatch, *, rate=Decimal("19"), expense="4000", vorsteuer="1576", tax_code="8"):
    resolved = {
        "tax_code": tax_code,
        "rate": rate,
        "expense_account": expense,
        "vorsteuerkonto": vorsteuer,
        "par_24_ustg": False,
        "taxation_type": "regular",
        "supplier_id": "sup",
        "article_tax_class": None,
        "delivery_date": "2026-03-15",
    }
    monkeypatch.setattr(
        "modules.agrar.services.tax_profile_service.get_taxation_type_for_supplier",
        lambda *a, **k: "regular",
    )
    monkeypatch.setattr(
        "modules.agrar.services.tax_profile_service.resolve_self_billing_tax_code",
        lambda *a, **k: resolved,
    )
    monkeypatch.setattr(
        "app.services.self_billing_docflow.lege_self_billing_beleg_an",
        lambda *a, **k: "doc-sb",
    )
    monkeypatch.setattr(
        "app.services.self_billing_docflow.verknuepfe_erweiterung",
        lambda *a, **k: None,
    )
    return resolved


def test_self_billing_requires_supplier_even_for_zero_gross():
    svc = _make_harvest_svc()
    inv = _make_invoice(net=0, vat=0, gross=0)
    with pytest.raises(ValidationFailedError, match="supplier_id"):
        svc._book_self_billing_credit_note(inv, date(2026, 3, 1))


def test_self_billing_creates_posted_ap_via_kern(monkeypatch, self_billing_tax_contract):
    from app.services import self_billing_buchung as core

    _patch_self_billing_path(monkeypatch)
    svc = _make_harvest_svc(configured=True)
    inv = _make_invoice(net=100, vat=19, gross=119)
    inv.id = "sb-inv"
    inv.harvest_acceptance_id = "ha-1"
    booked = MagicMock(return_value=("j-sb", []))
    monkeypatch.setattr(core, "buche_self_billing", booked)
    svc._book_self_billing_credit_note(inv, date(2026, 3, 15), supplier_id="sup", posted_by="u")
    booked.assert_called_once()
    assert booked.call_args.kwargs["supplier_id"] == "sup"
    assert booked.call_args.kwargs["gruppen"][0].aufwandskonto == "4000"


def test_self_billing_liability_matches_gross_in_gruppen(monkeypatch, self_billing_tax_contract):
    from app.services import self_billing_buchung as core
    from app.services.finance_eingangsrechnung_buchung import summen

    _patch_self_billing_path(monkeypatch, rate=Decimal("19"))
    svc = _make_harvest_svc(configured=True)
    inv = _make_invoice(net=500, vat=95, gross=595)
    inv.id = "sb-inv2"
    inv.harvest_acceptance_id = "ha-2"
    captured = {}

    def capture(**kwargs):
        captured["gruppen"] = kwargs["gruppen"]
        return ("j-sb2", kwargs["gruppen"])

    monkeypatch.setattr(core, "buche_self_billing", lambda *a, **k: capture(**k))
    svc._book_self_billing_credit_note(inv, date(2026, 4, 1), supplier_id="sup")
    net, vat, gross = summen(captured["gruppen"])
    assert gross == Decimal("595")
    assert net + vat == gross


def test_self_billing_zero_vat_group(monkeypatch, self_billing_tax_contract):
    from app.services import self_billing_buchung as core

    _patch_self_billing_path(monkeypatch, rate=Decimal("0"), vorsteuer=None)
    svc = _make_harvest_svc(configured=True)
    inv = _make_invoice(net=200, vat=0, gross=200)
    inv.id = "sb-inv3"
    captured = {}
    monkeypatch.setattr(
        core,
        "buche_self_billing",
        lambda *a, **k: captured.update(k) or ("j", k["gruppen"]),
    )
    svc._book_self_billing_credit_note(inv, date(2026, 5, 1), supplier_id="sup")
    assert captured["gruppen"][0].steuer == Decimal("0")
    assert captured["gruppen"][0].vorsteuerkonto is None


def test_self_billing_uses_business_day_when_no_delivery_date(monkeypatch, self_billing_tax_contract):
    from app.services import self_billing_buchung as core

    _patch_self_billing_path(monkeypatch, rate=Decimal("0"), vorsteuer=None)
    svc = _make_harvest_svc(configured=True)
    inv = _make_invoice(net=100, vat=0, gross=100)
    inv.id = "sb-inv4"
    captured = {}
    monkeypatch.setattr(
        core,
        "buche_self_billing",
        lambda *a, **k: captured.update(k) or ("j", k["gruppen"]),
    )
    svc._book_self_billing_credit_note(inv, None, supplier_id="sup")
    assert captured["delivery_date"] == business_today()


def test_self_billing_propagates_error_without_commit(monkeypatch, self_billing_tax_contract):
    from app.services import self_billing_buchung as core

    _patch_self_billing_path(monkeypatch)
    svc = _make_harvest_svc(configured=True)
    inv = _make_invoice()
    inv.id = "sb-inv5"
    monkeypatch.setattr(core, "buche_self_billing", MagicMock(side_effect=RuntimeError("DB down")))
    with pytest.raises(RuntimeError, match="DB down"):
        svc._book_self_billing_credit_note(inv, date(2026, 3, 1), supplier_id="sup")
    svc.db.commit.assert_not_called()


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
    db.query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.first.return_value = original
    original.total_debit = original.total_credit = line.debit
    line.tenant_id = TENANT
    line.debit_amount, line.credit_amount = line.debit, line.credit
    counter = SimpleNamespace(tenant_id=TENANT, account_id="contra", debit=Decimal("0"),
        debit_amount=Decimal("0"), credit=line.debit, credit_amount=line.debit, description="Counter")
    db.query.return_value.filter.return_value.all.return_value = [line,counter]
    db.query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.all.return_value = [line,counter]
    db.execute.return_value.all.return_value = [("1200",),("contra",)]
    db.execute.return_value.fetchone.side_effect = [("read committed",),(5,5,5,0,"a"*64)]

    added = []
    db.add.side_effect = lambda obj: added.append(obj)

    svc = FinanceTransactionService(db, TENANT)
    with patch("app.services.finance_transaction_service.JournalEntry") as MockEntry, \
         patch("app.services.finance_transaction_service.JournalEntryLine"):
        mock_reversal = MagicMock()
        mock_reversal.id = "e-rev"
        mock_reversal.tenant_id = TENANT
        mock_reversal.hash_prev = None
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
    db.query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.first.return_value = entry
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
    db.query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.first.return_value = original
    original.total_debit = original.total_credit = line.debit
    line.tenant_id = TENANT
    line.debit_amount, line.credit_amount = line.debit, line.credit
    counter = SimpleNamespace(tenant_id=TENANT, account_id="contra", debit=Decimal("0"),
        debit_amount=Decimal("0"), credit=line.debit, credit_amount=line.debit, description="Counter")
    db.query.return_value.filter.return_value.all.return_value = [line,counter]
    db.query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.all.return_value = [line,counter]
    db.execute.return_value.all.return_value = [("1200",),("contra",)]
    db.execute.return_value.fetchone.side_effect = [("read committed",),(6,6,6,0,"a"*64)]

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
        mock_rev.tenant_id = TENANT
        mock_rev.hash_prev = None
        mock_rev.sequence_number = None
        mock_rev.hash_current = None
        MockEntry.return_value = mock_rev
        MockLine.side_effect = lambda **kw: (line_kwargs_captured.append(kw), MagicMock())[1]

        svc.reverse("e-swap", reason="test")

    assert len(line_kwargs_captured) == 2
    rev_line = line_kwargs_captured[0]
    # Debit and credit are swapped
    assert rev_line["debit"] == line.credit    # 0
    assert rev_line["credit"] == line.debit    # 595
