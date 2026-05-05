"""Tests fuer Slice 3: Misch- und Fuetterungsprotokoll (TMR-Block).

Fachliche Regeln (User-Review 2026-04-23, §5):
- Nur sinnvoll, wenn ein TMR-Block existiert (TMR / PMR_stall).
- Mischreihenfolge Vertikalmischer:
  Strukturfutter -> Silagen -> Saftfutter/CoP -> Sonstiges -> KF/Mineral.
- Wasserzugabe zur Ziel-TM 38-42 % (Default 40 %).
- Uebermenge Default +5 % (Futterrest / Mischverlust).
"""
from __future__ import annotations

import pytest

from app.api.v1.endpoints.rations_optimization import (
    _build_mixing_protocol,
    _mix_group_order,
)


def _feed(feed_id: str, name: str, dm_frac: float = 0.4) -> dict:
    """Minimales Feed-Dict fuer Tests."""
    return {"id": feed_id, "name": name, "dm_frac": dm_frac}


# ---------------------------------------------------------------------------
# Gruppen-Reihenfolge
# ---------------------------------------------------------------------------

class TestMixGroupOrder:
    def test_stroh_heu_first(self) -> None:
        assert _mix_group_order("Heu, mittlere Qualitaet") == 1
        assert _mix_group_order("Stroh, Weizen") == 1

    def test_silagen_second(self) -> None:
        assert _mix_group_order("Grassilage, 1. Schnitt") == 2
        assert _mix_group_order("Maissilage, hohe OMD") == 2
        assert _mix_group_order("Gras, frisch o. konserviert") == 2

    def test_cop_third(self) -> None:
        assert _mix_group_order("Zuckerruebe, Schnitzel") == 3
        assert _mix_group_order("Biertreber, frisch") == 3
        assert _mix_group_order("Melasse") == 3

    def test_kraftfutter_fifth(self) -> None:
        assert _mix_group_order("Milchleistungsfutter 18/4") == 5
        assert _mix_group_order("Weidemineral Mg/Na") == 5
        assert _mix_group_order("Konzentrat, pelletiert") == 5


# ---------------------------------------------------------------------------
# Protokoll-Aufbau
# ---------------------------------------------------------------------------

class TestMixingProtocolStructure:
    def test_returns_none_without_tmr_block(self) -> None:
        feeds = [_feed("gras", "Weide, Fruehjahr jung", dm_frac=0.18)]
        amounts = [12.0]
        block_labels = ["pasture_block"]
        assert _build_mixing_protocol(
            ration_items=[],
            block_labels=block_labels,
            feeds=feeds,
            amounts=amounts,
            feeding_system_config={"system": "PMR_pasture"},
        ) is None

    def test_returns_none_for_empty_feeds(self) -> None:
        assert _build_mixing_protocol(
            ration_items=[],
            block_labels=[],
            feeds=[],
            amounts=[],
            feeding_system_config={"system": "TMR"},
        ) is None

    def test_basic_tmr_structure(self) -> None:
        feeds = [
            _feed("f_mais", "Maissilage, 35 % TM", dm_frac=0.35),
            _feed("f_gras", "Grassilage, 2. Schnitt", dm_frac=0.35),
            _feed("f_heu", "Heu, mittlere Qualitaet", dm_frac=0.86),
            _feed("f_mlf", "Milchleistungsfutter 18/4", dm_frac=0.88),
            _feed("f_min", "Mineralfutter Ca/P", dm_frac=0.97),
        ]
        amounts = [8.0, 5.0, 1.0, 4.0, 0.2]
        block_labels = ["tmr_block"] * 5
        protocol = _build_mixing_protocol(
            ration_items=[],
            block_labels=block_labels,
            feeds=feeds,
            amounts=amounts,
            feeding_system_config={"system": "TMR", "concentrate_distribution": "included_in_tmr"},
        )
        assert protocol is not None
        assert len(protocol["steps"]) == 5
        # Strukturfutter (Heu) vor Silagen
        first_names = [s["name"] for s in protocol["steps"]]
        assert first_names[0] == "Heu, mittlere Qualitaet"
        # Mineral am Ende
        assert first_names[-1] == "Mineralfutter Ca/P"

    def test_pasture_is_excluded_even_with_wrong_tmr_label(self) -> None:
        feeds = [
            _feed("weide", "Weide, Fruehjahr jung", dm_frac=0.18),
            _feed("f_mais", "Maissilage", dm_frac=0.35),
        ]
        protocol = _build_mixing_protocol(
            ration_items=[],
            block_labels=["tmr_block", "tmr_block"],
            feeds=feeds,
            amounts=[6.0, 8.0],
            feeding_system_config={"system": "PMR_pasture", "concentrate_distribution": "milkparlor"},
        )
        assert protocol is not None
        assert [step["feed_id"] for step in protocol["steps"]] == ["f_mais"]
        assert protocol["excluded_pasture"]["kgdm"] == pytest.approx(6.0)
        assert protocol["excluded_pasture"]["items"][0]["reason"] == "pasture_not_mixed"
        assert any("nicht teil der mischung" in warning.lower() for warning in protocol["warnings"])


class TestMixingProtocolWater:
    def test_water_adds_to_target_dm_frac(self) -> None:
        """Ziel-TM 40 %: Wasser auf diese Soll-TM ermittelt."""
        feeds = [_feed("f_mais", "Maissilage", dm_frac=0.35)]
        amounts = [10.0]  # 10 kg TM, 28.57 kg FM
        protocol = _build_mixing_protocol(
            ration_items=[],
            block_labels=["tmr_block"],
            feeds=feeds,
            amounts=amounts,
            feeding_system_config={"system": "TMR"},
        )
        # Ziel FM = 10 / 0.40 = 25 kg; actual FM = 28.57 => water = 0
        assert protocol is not None
        assert protocol["water_addition_kg_fm"] == 0.0

    def test_water_required_for_dry_mix(self) -> None:
        """Trockenes Mischfutter: Wasser zu Ziel-TM 40 % ergaenzen."""
        feeds = [
            _feed("f_mlf", "Kraftfutter", dm_frac=0.88),
            _feed("f_heu", "Heu", dm_frac=0.86),
        ]
        amounts = [8.0, 3.0]  # 11 kg TM, ~12.6 kg FM
        protocol = _build_mixing_protocol(
            ration_items=[],
            block_labels=["tmr_block"] * 2,
            feeds=feeds,
            amounts=amounts,
            feeding_system_config={"system": "TMR"},
        )
        # Ziel FM = 11 / 0.40 = 27.5 kg; actual ~12.6 => water ~14.9 kg
        assert protocol is not None
        assert protocol["water_addition_kg_fm"] > 10.0
        # Warnung bei sehr trockener Mischung
        assert any("trocken" in w.lower() for w in protocol["warnings"])


class TestMixingProtocolOverfill:
    def test_default_overfill_5pct(self) -> None:
        feeds = [_feed("f_mais", "Maissilage", dm_frac=0.35)]
        amounts = [10.0]
        protocol = _build_mixing_protocol(
            ration_items=[],
            block_labels=["tmr_block"],
            feeds=feeds,
            amounts=amounts,
            feeding_system_config={"system": "TMR"},
        )
        # Uebermenge = 28.57 * 0.05 = ~1.43 kg
        assert protocol is not None
        assert protocol["overfill_kg_fm"] == pytest.approx(10.0 / 0.35 * 0.05, rel=1e-2)
        assert protocol["basis"]["overfill_pct"] == 5.0

    def test_totals_consistency(self) -> None:
        feeds = [
            _feed("f_gras", "Grassilage", dm_frac=0.35),
            _feed("f_mais", "Maissilage", dm_frac=0.35),
        ]
        amounts = [6.0, 4.0]
        protocol = _build_mixing_protocol(
            ration_items=[],
            block_labels=["tmr_block"] * 2,
            feeds=feeds,
            amounts=amounts,
            feeding_system_config={"system": "TMR"},
        )
        totals = protocol["totals"]
        base_fm = totals["tmr_kgfm_without_water"]
        with_water = totals["tmr_kgfm_with_water"]
        with_water_and_over = totals["tmr_kgfm_with_water_and_overfill"]
        water = protocol["water_addition_kg_fm"]
        overfill = protocol["overfill_kg_fm"]
        assert with_water == pytest.approx(base_fm + water, abs=0.02)
        assert with_water_and_over == pytest.approx(base_fm + water + overfill, abs=0.02)
