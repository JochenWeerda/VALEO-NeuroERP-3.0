"""FEED-OPT-042 (TDD-Red-Welle 1): GfE-2023-Bedarfslogik als eigenes Modul.

Golden-Test: Die Literalwerte wurden VOR der Extraktion aus der bestehenden
Monolith-Implementierung (`rations_optimization._gfe_requirements`) erfasst
(Stand 2026-07-17) und beweisen die Drift-Freiheit der Modularisierung.
"""
from __future__ import annotations

import pytest

# Golden-Werte: erfasst aus der Monolith-Implementierung vor der Extraktion.
GOLDEN: dict[str, tuple[dict, float | None, dict[str, float]]] = {
    "default_hf_30l": (
        {"body_weight_kg": 650, "milk_kg_day": 30,
         "milk_fat_pct": 4.0, "milk_protein_pct": 3.4},
        None,
        {"me_mj": 213.514136, "sidp_g": 1906.363573, "nel_mj": 135.169319,
         "nxp_g": 2006.698498, "dmi_min_kg": 18.675, "dmi_max_kg": 22.825,
         "dmi_target_kg": 20.75, "ndf_min_g": 6225.0, "ca_min_g": 40.590678,
         "p_min_g": 28.802242, "na_min_g": 31.125, "mg_min_g": 34.2,
         "k_max_g": 581.0},
    ),
    "high_yield_weide": (
        {"body_weight_kg": 700, "milk_kg_day": 42, "milk_fat_pct": 4.2,
         "milk_protein_pct": 3.5, "feeding_type": "PMR+Weide"},
        None,
        {"me_mj": 295.701206, "sidp_g": 2523.417912, "nel_mj": 186.00478,
         "nxp_g": 2656.229381, "dmi_min_kg": 21.42, "dmi_max_kg": 26.18,
         "dmi_target_kg": 23.8, "ndf_min_g": 7140.0, "ca_min_g": 55.458764,
         "p_min_g": 39.705248, "na_min_g": 35.7, "mg_min_g": 37.8,
         "k_max_g": 666.4},
    ),
    "dry_cow": (
        {"body_weight_kg": 680, "milk_kg_day": 0},
        None,
        {"me_mj": 56.183597, "sidp_g": 438.969923, "nel_mj": 41.014026,
         "nxp_g": 462.073603, "dmi_min_kg": 15.3, "dmi_max_kg": 18.7,
         "dmi_target_kg": 17.0, "ndf_min_g": 5100.0, "ca_min_g": 4.128035,
         "p_min_g": 1.864274, "na_min_g": 25.5, "mg_min_g": 32.64,
         "k_max_g": 476.0},
    ),
    "fani_corrected": (
        {"body_weight_kg": 650, "milk_kg_day": 35, "milk_fat_pct": 3.9,
         "milk_protein_pct": 3.3, "target_dmi_kg": 23.0},
        3.8,
        {"me_mj": 234.207228, "sidp_g": 2153.363573, "nel_mj": 149.024319,
         "nxp_g": 2266.698498, "dmi_min_kg": 20.7, "dmi_max_kg": 25.3,
         "dmi_target_kg": 23.0, "ndf_min_g": 6900.0, "ca_min_g": 46.690678,
         "p_min_g": 33.302242, "na_min_g": 34.5, "mg_min_g": 34.7,
         "k_max_g": 644.0},
    ),
}


@pytest.mark.parametrize("case", sorted(GOLDEN))
def test_module_matches_monolith_golden_values(case: str) -> None:
    from app.agrar.rations.requirements import gfe_requirements

    profile, fani, expected = GOLDEN[case]
    result = gfe_requirements(profile, fani=fani).model_dump()
    assert set(result) == set(expected), "Feldmenge unveraendert"
    for key, value in expected.items():
        assert result[key] == pytest.approx(value, abs=1e-5), (case, key)


def test_monolith_aliases_delegate_to_module() -> None:
    """Bestehende Aufrufer im Monolithen nutzen exakt die Modul-Funktion."""
    from app.agrar.rations import requirements as module
    from app.api.v1.endpoints import rations_optimization as monolith

    assert monolith._gfe_requirements is module.gfe_requirements
    assert monolith._CowReq is module.CowRequirements
    assert monolith._normalize_feeding_type is module.normalize_feeding_type


def test_normalize_feeding_type_contract() -> None:
    from app.agrar.rations.requirements import normalize_feeding_type

    assert normalize_feeding_type(None) == "TMR"
    assert normalize_feeding_type("pmr") == "PMR"
    assert normalize_feeding_type("PMR Weide") == "PMR+Weide"
    assert normalize_feeding_type("weide") == "PMR+Weide"
    assert normalize_feeding_type("unbekannt") == "TMR"
