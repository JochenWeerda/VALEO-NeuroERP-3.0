"""Reine Logik-Tests des Kontrakt-Erfüllungsstands (DOM-CON-004) — ohne DB."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.contract_fulfillment_service import fulfillment_status

pytestmark = pytest.mark.unit


def test_offen():
    r = fulfillment_status(Decimal("100"), Decimal("0"))
    assert r["status"] == "offen" and r["offen"] == 100.0


def test_teilerfuellt():
    r = fulfillment_status(Decimal("200"), Decimal("120"))
    assert r["status"] == "teilerfuellt" and r["erfuellung_pct"] == 60.0 and r["offen"] == 80.0


def test_erfuellt_innerhalb_toleranz():
    assert fulfillment_status(Decimal("100"), Decimal("100"))["status"] == "erfuellt"


def test_uebererfuellt_ohne_erlaubnis_ist_abweichung():
    r = fulfillment_status(Decimal("100"), Decimal("110"), allow_over=False)
    assert r["status"] == "uebererfuellt" and r["abweichung"] is True


def test_uebererfuellt_mit_erlaubnis_keine_abweichung():
    r = fulfillment_status(Decimal("100"), Decimal("110"), allow_over=True)
    assert r["status"] == "uebererfuellt" and r["abweichung"] is False


def test_ohne_menge():
    assert fulfillment_status(Decimal("0"), Decimal("0"))["status"] == "ohne_menge"
