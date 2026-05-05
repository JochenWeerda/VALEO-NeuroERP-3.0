"""Tests fuer Slice 2: Konzentrat-Futterabruf-Staffel.

Fachliche Regeln (User-Review 2026-04-23, §4):
- Staffel linear/stueckweise OBERHALB Basisleistung (Milch aus Grobfutter).
- Umrechnungsfaktor 0,45-0,50 kg Konzentrat (FM) je kg Zusatzmilch.
- Einzelgaben-Limit je Verteilungssystem strikt geprueft.
- Tagesmaximum weich; physiologische Obergrenze = 1,5x Tagesmax.
- Keine KI-Bildwerte, rein aus _milk_from_supply + FeedingSystemConfig.
"""
from __future__ import annotations

import pytest

from app.api.v1.endpoints.rations_optimization import (
    _build_concentrate_call_up_table,
    _CONC_PER_ADDITIONAL_MILK_LOW,
    _CONC_PER_ADDITIONAL_MILK_HIGH,
    _CONC_HARD_SAFETY_FACTOR,
)


# ---------------------------------------------------------------------------
# Basisverhalten: Staffel nur fuer gestaffelte Systeme
# ---------------------------------------------------------------------------

class TestCallUpAvailability:
    def test_tmr_included_returns_none(self) -> None:
        """Bei reinem TMR (included_in_tmr) gibt es keine Staffel."""
        fs = {
            "system": "TMR",
            "concentrate_distribution": "included_in_tmr",
            "concentrate_max_per_serving_kg": 0.0,
            "concentrate_servings_per_day": 0.0,
            "concentrate_max_per_day_kg": 0.0,
        }
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 30.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=20.0,
        )
        assert table is None

    def test_empty_config_returns_none(self) -> None:
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 30.0},
            feeding_system_config={},
            base_milk_from_forage_kg=20.0,
        )
        assert table is None

    def test_milkparlor_returns_table(self) -> None:
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "milkparlor",
            "concentrate_max_per_serving_kg": 4.5,
            "concentrate_servings_per_day": 2.0,
            "concentrate_max_per_day_kg": 9.0,
        }
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 35.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=22.0,
        )
        assert table is not None
        assert "basis" in table and "rows" in table and "warnings" in table
        assert table["basis"]["concentrate_distribution"] == "milkparlor"


# ---------------------------------------------------------------------------
# Linearitaet: 0,45-0,50 kg Konzentrat je kg Zusatzmilch
# ---------------------------------------------------------------------------

class TestCallUpLinearity:
    def _table(self, basis: float = 20.0, target: float = 35.0):
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "milkparlor",
            "concentrate_max_per_serving_kg": 4.5,
            "concentrate_servings_per_day": 2.0,
            "concentrate_max_per_day_kg": 9.0,
        }
        return _build_concentrate_call_up_table(
            profile={"milk_kg_day": target},
            feeding_system_config=fs,
            base_milk_from_forage_kg=basis,
        )

    def test_below_basis_zero_concentrate(self) -> None:
        table = self._table(basis=25.0, target=25.0)
        # Stufe 25 kg = Basis -> 0 Zusatzmilch -> 0 Konzentrat
        row_25 = next(r for r in table["rows"] if abs(r["milk_kg_day"] - 25.0) < 1e-6)
        assert row_25["additional_milk_kg"] == 0.0
        assert row_25["concentrate_kg_fm_day_low"] == 0.0
        assert row_25["concentrate_kg_fm_day_high"] == 0.0

    def test_linear_band_at_30kg(self) -> None:
        table = self._table(basis=22.0, target=35.0)
        row_30 = next(r for r in table["rows"] if abs(r["milk_kg_day"] - 30.0) < 1e-6)
        # 30 - 22 = 8 kg Zusatzmilch
        assert row_30["additional_milk_kg"] == pytest.approx(8.0)
        expected_low = 8.0 * _CONC_PER_ADDITIONAL_MILK_LOW
        expected_high = 8.0 * _CONC_PER_ADDITIONAL_MILK_HIGH
        assert row_30["concentrate_kg_fm_day_low"] == pytest.approx(expected_low, rel=1e-3)
        assert row_30["concentrate_kg_fm_day_high"] == pytest.approx(expected_high, rel=1e-3)

    def test_piecewise_linear_no_negative_concentrate(self) -> None:
        """Niemals negative Konzentratmengen, auch wenn Basis > gewaehlte Stufe."""
        table = self._table(basis=40.0, target=25.0)
        for row in table["rows"]:
            if row["milk_kg_day"] <= 40.0:
                assert row["concentrate_kg_fm_day_low"] == 0.0
                assert row["concentrate_kg_fm_day_high"] == 0.0


# ---------------------------------------------------------------------------
# Limit-Checks: Einzelgabe + Tagesmax + physiologische Obergrenze
# ---------------------------------------------------------------------------

class TestCallUpLimits:
    def test_high_performance_exceeds_hard_cap(self) -> None:
        """Bei sehr hoher Zusatzmilch wird die 1,5x-Hartgrenze ueberschritten."""
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "milkparlor",
            "concentrate_max_per_serving_kg": 4.5,
            "concentrate_servings_per_day": 2.0,
            "concentrate_max_per_day_kg": 9.0,
        }
        # Basis klein, Zielleistung sehr hoch => 30 kg Zusatzmilch noetig
        # => 0.475 * 30 = 14.25 kg FM > 13.5 kg (1.5x von 9)
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 50.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=20.0,
        )
        row_50 = next(r for r in table["rows"] if abs(r["milk_kg_day"] - 50.0) < 1e-6)
        assert row_50["exceeds_hard_safety_limit"] is True
        assert row_50["exceeds_recommended_daily_limit"] is True
        # Warnung erzeugt
        assert any("50" in w and "physiolog" in w.lower() for w in table["warnings"])

    def test_moderate_performance_flags_soft_daily(self) -> None:
        """Moderate Ueberschreitung: Tagesmax weich, aber noch unter 1,5x."""
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "milkparlor",
            "concentrate_max_per_serving_kg": 4.5,
            "concentrate_servings_per_day": 2.0,
            "concentrate_max_per_day_kg": 9.0,
        }
        # 20 kg Zusatzmilch -> ~9.5 kg FM -> > 9 (daily), < 13.5 (hard)
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 40.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=20.0,
        )
        row_40 = next(r for r in table["rows"] if abs(r["milk_kg_day"] - 40.0) < 1e-6)
        assert row_40["exceeds_recommended_daily_limit"] is True
        assert row_40["exceeds_hard_safety_limit"] is False

    def test_per_serving_limit_detection(self) -> None:
        """Einzelgabe-Ueberschreitung wird erkannt und gewarnt."""
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "transponder",
            "concentrate_max_per_serving_kg": 2.5,
            "concentrate_servings_per_day": 4.0,
            "concentrate_max_per_day_kg": 8.0,
        }
        # Transponder: mid = conc_fm / 4. 15 kg Zusatzmilch * 0.475 = 7.125 kg
        # per_serving = 1.78 -> unter 2.5 -> OK
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 35.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=20.0,
        )
        row_35 = next(r for r in table["rows"] if abs(r["milk_kg_day"] - 35.0) < 1e-6)
        assert row_35["per_serving_kg_fm"] < 2.5

    def test_amsserving_limit_with_high_milk(self) -> None:
        """AMS-Grenzen enger: 2.0 kg/Melkung, 6 kg/d."""
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "ams",
            "concentrate_max_per_serving_kg": 2.0,
            "concentrate_servings_per_day": 3.0,
            "concentrate_max_per_day_kg": 6.0,
        }
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 40.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=22.0,
        )
        # bei 40 kg: 18 kg Zusatzmilch -> ~8.55 kg FM/Tag, per_serving ~2.85 -> > 2.0
        row_40 = next(r for r in table["rows"] if abs(r["milk_kg_day"] - 40.0) < 1e-6)
        assert row_40["exceeds_per_serving_limit"] is True
        assert row_40["exceeds_recommended_daily_limit"] is True


# ---------------------------------------------------------------------------
# Integration: Zielleistung wird in Staffel aufgenommen
# ---------------------------------------------------------------------------

class TestCallUpTargetMilk:
    def test_non_standard_target_is_included(self) -> None:
        fs = {
            "system": "PMR_stall",
            "concentrate_distribution": "milkparlor",
            "concentrate_max_per_serving_kg": 4.5,
            "concentrate_servings_per_day": 2.0,
            "concentrate_max_per_day_kg": 9.0,
        }
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 37.5},
            feeding_system_config=fs,
            base_milk_from_forage_kg=22.0,
        )
        steps = [r["milk_kg_day"] for r in table["rows"]]
        assert 37.5 in steps

    def test_basis_field_contains_metadata(self) -> None:
        fs = {
            "system": "PMR_pasture",
            "concentrate_distribution": "milkparlor",
            "concentrate_max_per_serving_kg": 4.5,
            "concentrate_servings_per_day": 2.0,
            "concentrate_max_per_day_kg": 9.0,
        }
        table = _build_concentrate_call_up_table(
            profile={"milk_kg_day": 30.0},
            feeding_system_config=fs,
            base_milk_from_forage_kg=25.0,
        )
        basis = table["basis"]
        assert basis["milk_from_forage_kg"] == pytest.approx(25.0)
        assert basis["target_milk_kg"] == pytest.approx(30.0)
        assert basis["feeding_system"] == "PMR_PASTURE"
        assert basis["concentrate_max_per_serving_kg_fm"] == pytest.approx(4.5)
        assert basis["concentrate_max_per_day_kg_fm"] == pytest.approx(9.0)
        assert basis["hard_safety_daily_cap_kg_fm"] == pytest.approx(
            9.0 * _CONC_HARD_SAFETY_FACTOR
        )
        assert basis["kg_conc_per_additional_milk_low"] == _CONC_PER_ADDITIONAL_MILK_LOW
        assert basis["kg_conc_per_additional_milk_high"] == _CONC_PER_ADDITIONAL_MILK_HIGH
