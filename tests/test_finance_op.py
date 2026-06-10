"""Reine Logik-Tests des OP-Aging (DOM-FIN-004) — ohne DB."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.services.finance_op_service import aging_bucket

pytestmark = pytest.mark.unit

TODAY = date(2026, 6, 10)


def test_nicht_faellig_ohne_datum():
    assert aging_bucket(None, TODAY) == ("nicht_faellig", 0)


def test_nicht_faellig_zukunft():
    assert aging_bucket(TODAY + timedelta(days=5), TODAY) == ("nicht_faellig", 0)


def test_bucket_1_30():
    assert aging_bucket(TODAY - timedelta(days=14), TODAY) == ("1-30", 14)


def test_bucket_31_60():
    assert aging_bucket(TODAY - timedelta(days=45), TODAY) == ("31-60", 45)


def test_bucket_60_plus():
    assert aging_bucket(TODAY - timedelta(days=75), TODAY) == ("60+", 75)


def test_faellig_heute_ist_nicht_ueberfaellig():
    assert aging_bucket(TODAY, TODAY) == ("nicht_faellig", 0)
