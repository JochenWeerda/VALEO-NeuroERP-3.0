"""ASK-PPP-002: Sachkundenachweis als Freigabevoraussetzung für PSM (TDD)."""
from __future__ import annotations

import os
import sys
from datetime import date

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def test_sachkunde_valid_allows_psm():
    from app.agrar.feldbuch.sachkunde import pruefe_sachkunde

    r = pruefe_sachkunde(
        anwender="Max Mustermann",
        sachkunde_nummer="SK-NI-12345",
        gueltig_bis=date(2027, 12, 31),
        anwendungsdatum=date(2026, 5, 10),
    )
    assert r["erlaubt"] is True
    assert r["fehlende"] == []


def test_sachkunde_missing_number_blocks():
    from app.agrar.feldbuch.sachkunde import pruefe_sachkunde

    r = pruefe_sachkunde(
        anwender="Max Mustermann",
        sachkunde_nummer=None,
        gueltig_bis=date(2027, 12, 31),
        anwendungsdatum=date(2026, 5, 10),
    )
    assert r["erlaubt"] is False
    assert "Sachkundenachweis" in r["fehlende"]


def test_sachkunde_expired_blocks():
    from app.agrar.feldbuch.sachkunde import pruefe_sachkunde

    r = pruefe_sachkunde(
        anwender="Max Mustermann",
        sachkunde_nummer="SK-NI-12345",
        gueltig_bis=date(2025, 1, 1),
        anwendungsdatum=date(2026, 5, 10),
    )
    assert r["erlaubt"] is False
    assert "gueltig" in ";".join(r["fehlende"]).lower() or "abgelaufen" in ";".join(r["fehlende"]).lower()


def test_psm_compliance_includes_sachkunde():
    from app.agrar.feldbuch.pflanzenschutz import PsmMassnahme, psm_compliance

    m = PsmMassnahme(
        date(2026, 5, 10), "Atlantis", 1.5, 8.0, "Max Mustermann",
        wirkungsbereich="Herbizid", begruendung="Ungras",
        sachkunde_nummer=None, sachkunde_gueltig_bis=None,
    )
    r = psm_compliance(m)
    assert r["compliant"] is False
    assert any("Sachkunde" in x for x in r["fehlende_pflichtangaben"])
