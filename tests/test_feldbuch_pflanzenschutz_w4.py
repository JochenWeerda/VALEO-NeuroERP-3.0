"""
AS-W4-Regression: PSM-Dokumentation (PflSchG/CC) — Compliance, Kostensplit,
Wartezeit-Hinweis.
"""
from __future__ import annotations

import os
import sys
from datetime import date

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.agrar.feldbuch.pflanzenschutz import (  # noqa: E402
    PsmMassnahme,
    kostensplit_nach_wirkungsbereich,
    psm_compliance,
    wartezeit_hinweis,
)


class TestCompliance:
    def test_complete_is_compliant(self):
        m = PsmMassnahme(date(2026, 5, 10), "Beispiel-Herbizid", 1.5, 8.0, "Max Mustermann",
                         wirkungsbereich="Herbizid", begruendung="Ungrasbekaempfung",
                         sachkunde_nummer="SK-NI-1", sachkunde_gueltig_bis=date(2027, 12, 31))
        r = psm_compliance(m)
        assert r["compliant"] is True
        assert r["fehlende_pflichtangaben"] == []

    def test_missing_operator_and_reason(self):
        m = PsmMassnahme(date(2026, 5, 10), "Mittel", 1.0, 5.0, anwender=None)
        r = psm_compliance(m)
        assert r["compliant"] is False
        assert "Anwender" in r["fehlende_pflichtangaben"]
        assert "Begruendung" in r["fehlende_pflichtangaben"]


class TestWartezeit:
    def test_eingehalten(self):
        r = wartezeit_hinweis(date(2026, 6, 1), 42, date(2026, 8, 1))
        assert r["wartezeit_eingehalten"] is True
        assert r["fruehester_erntetermin"] == "2026-07-13"

    def test_verletzt(self):
        r = wartezeit_hinweis(date(2026, 7, 20), 42, date(2026, 8, 1))
        assert r["wartezeit_eingehalten"] is False

    def test_none_without_inputs(self):
        assert wartezeit_hinweis(None, 42, date(2026, 8, 1)) is None


class TestKostensplit:
    def test_split_by_bereich(self):
        ms = [
            PsmMassnahme(date(2026, 5, 1), "H", 1, 5, "A", wirkungsbereich="Herbizid", kosten_eur=100.0),
            PsmMassnahme(date(2026, 6, 1), "F", 1, 5, "A", wirkungsbereich="Fungizid", kosten_eur=60.0),
            PsmMassnahme(date(2026, 6, 2), "X", 1, 5, "A", wirkungsbereich=None, kosten_eur=20.0),
        ]
        s = kostensplit_nach_wirkungsbereich(ms)
        assert s["Herbizid"] == 100.0
        assert s["Fungizid"] == 60.0
        assert s["Sonstiges"] == 20.0
