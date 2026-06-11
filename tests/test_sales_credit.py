"""Reine Logik-Tests der Kreditlimit-Prüfung (DOM-SALES-004.3)."""

from __future__ import annotations

import pytest

from app.services.sales_credit_service import credit_check

pytestmark = pytest.mark.unit


def test_kein_limit_keine_sperre():
    r = credit_check(0, 5000, betrag=1000)
    assert r["ampel"] == "kein_limit" and r["verfuegbar"] is None


def test_ok_unter_warnschwelle():
    r = credit_check(20000, 4800, betrag=5000)
    assert r["ampel"] == "ok" and r["verfuegbar"] == 15200.0 and r["auslastung_neu_pct"] == 49.0


def test_warnung_ab_80_prozent():
    r = credit_check(20000, 4800, betrag=12500)
    assert r["ampel"] == "warnung" and r["auslastung_neu_pct"] == 86.5


def test_blockiert_ab_100_prozent():
    r = credit_check(10000, 8000, betrag=3000)
    assert r["ampel"] == "blockiert" and r["auslastung_neu_pct"] == 110.0


def test_verfuegbarer_rahmen():
    r = credit_check(10000, 6000)
    assert r["verfuegbar"] == 4000.0 and r["ampel"] == "ok"
