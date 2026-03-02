"""
Tests für FIBU Connector Framework: Parser, Validierung, Idempotency.
"""

from decimal import Decimal

import pytest

from app.core.connectors.base import NormalizedItem, NormalizedLine, validate_item_balance
from app.core.connectors.payroll_parser import PayrollParser
from app.core.connectors.asset_ledger_parser import AssetLedgerParser


class TestValidateItemBalance:
    """Validierung: Soll = Haben."""

    def test_balanced(self):
        item = NormalizedItem(
            booking_date="2026-01-15",
            document_no="B1",
            text="Test",
            lines=[
                NormalizedLine(account="1000", dc="D", amount=Decimal("100.00")),
                NormalizedLine(account="2000", dc="C", amount=Decimal("100.00")),
            ],
        )
        assert validate_item_balance(item) is None

    def test_unbalanced(self):
        item = NormalizedItem(
            booking_date="2026-01-15",
            document_no="B1",
            text="Test",
            lines=[
                NormalizedLine(account="1000", dc="D", amount=Decimal("100.00")),
                NormalizedLine(account="2000", dc="C", amount=Decimal("99.00")),
            ],
        )
        err = validate_item_balance(item)
        assert err is not None
        assert "Soll" in err and "Haben" in err


class TestPayrollParser:
    """Payroll-Parser: CSV mit Lohnbuchungen."""

    @pytest.fixture
    def parser(self):
        return PayrollParser()

    def test_detect_valid_csv(self, parser):
        raw = b"buchungsdatum;konto;betrag;soll_haben;buchungstext\n2026-01-15;6000;100;S;Lohn"
        assert parser.detect(raw, {"delimiter": ";"}) is True

    def test_parse_minimal_csv(self, parser):
        raw = (
            b"buchungsdatum;konto;betrag;soll_haben;buchungstext\n"
            b"2026-01-15;6000;100,50;S;Lohn\n"
            b"2026-01-15;1200;100,50;H;Verrechnung"
        )
        settings = {"delimiter": ";", "encoding": "utf-8"}
        mapping = {}
        items = parser.parse(raw, settings, mapping)
        assert len(items) == 1
        assert items[0].booking_date == "2026-01-15"
        assert len(items[0].lines) == 2
        assert validate_item_balance(items[0]) is None


class TestAssetLedgerParser:
    """Asset-Ledger-Parser: CSV mit Anlagenbuchungen."""

    @pytest.fixture
    def parser(self):
        return AssetLedgerParser()

    def test_detect_valid_csv(self, parser):
        raw = b"buchungsdatum;konto;betrag;gegenkonto;buchungstext\n2026-01-15;0840;500;4800;AfA"
        assert parser.detect(raw, {"delimiter": ";"}) is True

    def test_parse_two_lines_balanced(self, parser):
        raw = (
            b"buchungsdatum;konto;betrag;soll_haben;gegenkonto;buchungstext\n"
            b"2026-01-15;0840;500;S;4800;Abschreibung\n"
        )
        settings = {"delimiter": ";", "encoding": "utf-8"}
        mapping = {}
        items = parser.parse(raw, settings, mapping)
        assert len(items) == 1
        assert len(items[0].lines) == 2
        assert items[0].booking_date == "2026-01-15"
        err = validate_item_balance(items[0])
        assert err is None, err
