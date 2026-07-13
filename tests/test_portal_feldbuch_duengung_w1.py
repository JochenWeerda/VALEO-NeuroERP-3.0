"""
AS-W1-Regression (Portal): Reinnaehrstoff-Berechnung beim Speichern einer
Duengungsmassnahme im Portal-Feldbuch.
"""
from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.api.v1.endpoints.portal_feldbuch import _apply_duengung_nutrients  # noqa: E402


def test_kas_nutrients_and_cost():
    payload = {
        "typ": "duengung", "menge": 350.0, "flaeche": 10.0,
        "n_gehalt": 27.0, "duenger_form": "M", "preis_je_einheit": 0.35,
    }
    out = _apply_duengung_nutrients(dict(payload))
    assert out["n_kg"] == pytest.approx(945.0)
    assert out["kosten_eur"] == pytest.approx(0.35 * 350 * 10, abs=0.01)
    # Nicht-Spalten-Eingaben werden entfernt
    for key in ("n_gehalt", "p2o5_gehalt", "k2o_gehalt", "mgo_gehalt", "s_gehalt", "preis_je_einheit"):
        assert key not in out


def test_npk_all_nutrients():
    payload = {"typ": "duengung", "menge": 300.0, "flaeche": 5.0,
               "n_gehalt": 15.0, "p2o5_gehalt": 15.0, "k2o_gehalt": 15.0}
    out = _apply_duengung_nutrients(dict(payload))
    assert out["n_kg"] == pytest.approx(225.0)
    assert out["p2o5_kg"] == pytest.approx(225.0)
    assert out["k2o_kg"] == pytest.approx(225.0)


def test_no_gehalt_no_nutrient_columns():
    payload = {"typ": "psm", "menge": 2.0, "flaeche": 5.0, "wirkungsbereich": "Herbizid"}
    out = _apply_duengung_nutrients(dict(payload))
    assert "n_kg" not in out
    assert out.get("wirkungsbereich") == "Herbizid"


def test_organic_form_flag_preserved():
    payload = {"typ": "duengung", "menge": 25000.0, "flaeche": 1.0,
               "n_gehalt": 0.4, "duenger_form": "O"}
    out = _apply_duengung_nutrients(dict(payload))
    assert out["duenger_form"] == "O"
    assert out["n_kg"] == pytest.approx(100.0)
