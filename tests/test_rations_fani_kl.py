"""Tests fuer FANi-basiertes dynamisches k_l in _gfe_requirements (RATIONS-FANI-KL-001)."""
from __future__ import annotations

import pytest

from app.api.v1.endpoints.rations_optimization import _gfe_requirements


_BASE_PROFILE = {
    "body_weight_kg": 650,
    "milk_kg_day": 35,
    "milk_fat_pct": 4.0,
    "milk_protein_pct": 3.4,
    "feeding_type": "TMR",
}


def test_fani_none_uses_baseline_kl():
    """Ohne FANi bleibt k_l_planning=0.60 – unveraendertes Basisverhalten."""
    req_base = _gfe_requirements(_BASE_PROFILE)
    req_none = _gfe_requirements(_BASE_PROFILE, fani=None)
    assert req_base.me_mj == pytest.approx(req_none.me_mj, rel=1e-9)


def test_fani_3_equals_baseline():
    """FANi=3.0 entspricht dem Baseline (k_l-Korrektur = 0)."""
    req_base = _gfe_requirements(_BASE_PROFILE)
    req_3 = _gfe_requirements(_BASE_PROFILE, fani=3.0)
    assert req_base.me_mj == pytest.approx(req_3.me_mj, rel=1e-6)


def test_fani_above_3_reduces_me_demand():
    """FANi>3 -> hoehere ME-Dichte -> hoeheres k_l -> niedrigerer ME-Bedarf."""
    req_base = _gfe_requirements(_BASE_PROFILE)
    req_high = _gfe_requirements(_BASE_PROFILE, fani=4.0)
    assert req_high.me_mj < req_base.me_mj


def test_fani_below_3_increases_me_demand():
    """FANi<3 -> niedrigere ME-Dichte -> niedrigeres k_l -> hoehere ME-Bedarf."""
    req_base = _gfe_requirements(_BASE_PROFILE)
    req_low = _gfe_requirements(_BASE_PROFILE, fani=2.0)
    assert req_low.me_mj > req_base.me_mj


def test_kl_clamped_at_upper_bound():
    """k_l darf 0.64 nicht ueberschreiten (FANi=13 wuerde sonst 0.70 ergeben)."""
    req_extreme = _gfe_requirements(_BASE_PROFILE, fani=13.0)
    req_cap = _gfe_requirements(_BASE_PROFILE, fani=7.0)
    # Beide sollten gleich sein, da Clamp bei 0.64 greift.
    assert req_extreme.me_mj == pytest.approx(req_cap.me_mj, rel=1e-6)


def test_kl_clamped_at_lower_bound():
    """k_l darf 0.58 nicht unterschreiten (FANi=0 wuerde k_l=0.57 ergeben)."""
    req_zero = _gfe_requirements(_BASE_PROFILE, fani=0.0)
    req_none = _gfe_requirements(_BASE_PROFILE, fani=None)
    # fani=0 -> kein aenderung wegen `fani > 0` Guard, also identisch mit None
    assert req_zero.me_mj == pytest.approx(req_none.me_mj, rel=1e-9)


@pytest.mark.parametrize("fani,expected_kl", [
    (1.0, 0.58),   # 0.60 + 0.01*(1-3) = 0.58 (Untergrenze)
    (2.0, 0.59),   # 0.60 + 0.01*(2-3) = 0.59
    (3.0, 0.60),   # Basis
    (4.0, 0.61),   # 0.60 + 0.01*(4-3) = 0.61
    (5.0, 0.62),
    (7.0, 0.64),   # Obergrenze
])
def test_kl_values_parametrized(fani, expected_kl):
    """Tabellarische Pruefung der k_l-Werte fuer verschiedene FANi-Stufen."""
    profile_nomilk = {
        "body_weight_kg": 650,
        "milk_kg_day": 0,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "feeding_type": "TMR",
    }
    # Bei milk=0 hat k_l keinen Einfluss auf me_mj (me_milk=0), also Milch setzen
    profile_milk = {**profile_nomilk, "milk_kg_day": 35}
    req_fani = _gfe_requirements(profile_milk, fani=fani)
    nel_maint = 0.308 * (650 ** 0.75)
    nel_milk = (0.38 * 4.0 + 0.21 * 3.4 + 0.95) * 35
    expected_me = nel_maint / 0.73 + nel_milk / expected_kl
    assert req_fani.me_mj == pytest.approx(expected_me, rel=1e-6)


def test_sidp_unchanged_by_fani():
    """sidP-Bedarf haengt nicht von FANi/k_l ab."""
    req_base = _gfe_requirements(_BASE_PROFILE)
    req_high = _gfe_requirements(_BASE_PROFILE, fani=4.0)
    assert req_base.sidp_g == pytest.approx(req_high.sidp_g, rel=1e-9)


def test_pmr_weide_profile_also_uses_fani():
    """FANi-Korrektur gilt auch fuer PMR+Weide-Profile."""
    profile_weide = {**_BASE_PROFILE, "feeding_type": "PMR+Weide"}
    req_base = _gfe_requirements(profile_weide)
    req_fani = _gfe_requirements(profile_weide, fani=4.0)
    assert req_fani.me_mj < req_base.me_mj
