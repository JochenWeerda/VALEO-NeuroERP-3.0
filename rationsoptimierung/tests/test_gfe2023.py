"""Unit-Tests GfE-2023-Näherungsmodul."""
import pytest

from app.nutrition import gfe2023


def test_metabolic_body_weight():
    assert abs(gfe2023.metabolic_body_weight_kg(100) - 31.62) < 0.1
    with pytest.raises(ValueError):
        gfe2023.metabolic_body_weight_kg(0)


def test_energy_maintenance_650kg():
    # 0,64 * 650^0,75 ≈ 82,4 MJ/Tag
    me = gfe2023.energy_maintenance_me_mj(650)
    assert me == pytest.approx(0.64 * (650**0.75), rel=1e-5)
    assert 80 < me < 86


def test_ecm_and_total_me():
    # 35 kg Milch, 3,8 % Fett, 3,2 % Eiweiß
    ecm = gfe2023.energy_corrected_milk_kg(35, 3.8, 3.2)
    factor = 0.337 + 0.116 * 3.8 + 0.06 * 3.2
    assert abs(ecm - 35 * factor) < 1e-6
    total, maint, lact = gfe2023.total_me_requirement_mj(650, 35, 3.8, 3.2)
    assert total == pytest.approx(maint + lact)
    assert maint == pytest.approx(gfe2023.energy_maintenance_me_mj(650))
    assert lact == pytest.approx(gfe2023.ME_PER_KG_ECM * ecm)


def test_sidp_positive():
    t, m, l = gfe2023.sidp_requirement_g(650, 35, 3.2)
    assert t == m + l
    assert m > 0 and l > 0


def test_estimate_dmi_high_yield_ballpark():
    """Geschätzte TM für 650 kg / 35 kg Milch / ~Spitzenlaktation sollte > 22 kg liegen (LP mit GfE-ME)."""
    dmi = gfe2023.estimate_dmi_lactating_kg(650, 35, 150)
    assert 22.0 <= dmi <= 32.0


def test_minerals_scale_with_milk():
    ca0, p0, na0 = gfe2023.minerals_ca_p_na_g(650, 0)
    ca1, p1, na1 = gfe2023.minerals_ca_p_na_g(650, 35)
    assert ca1 > ca0 and p1 > p0 and na1 > na0
