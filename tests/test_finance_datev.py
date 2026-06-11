"""Reine Logik-Tests des DATEV-Exports (DOM-FIN-004.5)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.services.finance_datev_service import DATEV_HEADER, datev_csv, datev_row

pytestmark = pytest.mark.unit


def test_datev_row_debitor():
    r = datev_row(Decimal("800"), "debitoren", date(2026, 3, 7), "DEMO-RE-103", "Müller KG")
    assert r[0] == "800,00" and r[1] == "S" and r[2] == "1400" and r[3] == "8400"
    assert r[4] == "07032026" and r[5] == "DEMO-RE-103"


def test_datev_row_kreditor():
    r = datev_row(Decimal("3400"), "kreditoren", date(2026, 6, 5), "DEMO-RE-102", "Lieferant GmbH")
    assert r[1] == "H" and r[2] == "1600" and r[3] == "3400"


def test_datev_row_dezimalkomma():
    r = datev_row(Decimal("1234.5"), "debitoren", date(2026, 1, 1), "X", "Y")
    assert r[0] == "1234,50"


def test_datev_csv_header_und_zeilen():
    rows = [datev_row(Decimal("100"), "debitoren", date(2026, 1, 2), "R1", "Kunde")]
    out = datev_csv(rows)
    lines = out.strip().split("\n")
    assert lines[0] == ";".join(DATEV_HEADER)
    assert lines[1].startswith("100,00;S;1400;8400;02012026;R1;")
