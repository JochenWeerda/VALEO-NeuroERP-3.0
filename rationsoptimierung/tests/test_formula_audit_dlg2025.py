"""
Formel-Audit-Regression gegen DLG Information 01|2025 / GfE 2023.

Verankert die zentralen Kernformeln des Rations-Bedarfsmodells gegen die
Definitionen aus dem DLG-Merkblatt 01|2025, um kuenftige Formel-Drift zu
verhindern. Referenz: DLG Information 01|2025 „Rationsoptimierung und
Fuetterungskontrolle bei Milchkuehen", Kap. 10 und Abkuerzungsverzeichnis.
"""
import pytest

from app.nutrition import gfe2023


def _dlg_ecm_kg(milk_kg, fat_pct, protein_pct, lactose_pct):
    """DLG-01|2025-ECM-Definition, unabhaengig vom Produktivcode nachgerechnet."""
    return milk_kg * (38.5 * fat_pct + 24.2 * protein_pct + 16.5 * lactose_pct) / 3.15 / 100.0


class TestEcmDlg2025:
    def test_reference_composition_ecm_equals_milk(self):
        # Referenzzusammensetzung 4,0/3,4/4,8 -> ECM ~ Milch (Faktor ~1,0015)
        ecm = gfe2023.energy_corrected_milk_kg(30.0, 4.0, 3.4, 4.8)
        assert ecm == pytest.approx(_dlg_ecm_kg(30.0, 4.0, 3.4, 4.8), rel=1e-9)
        assert ecm == pytest.approx(30.0, rel=2e-3)

    def test_lactose_default_is_dlg_reference(self):
        assert gfe2023.ECM_REFERENCE_LACTOSE_PCT == pytest.approx(4.8)
        # Ohne Laktose-Angabe wird der DLG-Referenzwert 4,8 % verwendet
        with_default = gfe2023.energy_corrected_milk_kg(40.0, 3.8, 3.2)
        explicit = gfe2023.energy_corrected_milk_kg(40.0, 3.8, 3.2, 4.8)
        assert with_default == pytest.approx(explicit, rel=1e-12)

    def test_lactose_sensitivity(self):
        # Hoehere Laktose -> hoehere ECM (Formel beruecksichtigt Laktose)
        low = gfe2023.energy_corrected_milk_kg(40.0, 3.8, 3.2, 4.5)
        high = gfe2023.energy_corrected_milk_kg(40.0, 3.8, 3.2, 5.0)
        assert high > low

    def test_matches_independent_dlg_formula(self):
        for milk, f, p, la in [(25, 4.2, 3.5, 4.7), (45, 3.6, 3.1, 4.9), (10, 5.0, 3.8, 4.6)]:
            assert gfe2023.energy_corrected_milk_kg(milk, f, p, la) == pytest.approx(
                _dlg_ecm_kg(milk, f, p, la), rel=1e-9
            )


class TestEnergyMaintenanceGfe2023:
    def test_maintenance_064_metabolic_bw(self):
        # GfE 2023: ME_Erhalt = 0,64 * LM^0,75
        for km in (600, 650, 700, 790):
            assert gfe2023.energy_maintenance_me_mj(km) == pytest.approx(
                0.64 * km**0.75, rel=1e-9
            )


class TestMePerKgEcm:
    def test_me_per_kg_ecm_constant(self):
        # ME_Milch = ECM * (3,15 / 0,66)
        assert gfe2023.ME_PER_KG_ECM == pytest.approx(3.15 / 0.66, rel=1e-9)


class TestDcabDefinition:
    """DCAB = (Na+ + K+) - (Cl- + S2-) [meq/kg TM] (DLG 01|2025, Kap. 9.2.2)."""

    @staticmethod
    def _dcab_meq(na_g, k_g, cl_g, s_g):
        # Aequivalentgewichte: Na 22,99, K 39,10, Cl 35,45, S 16,03 (2-wertig)
        return (na_g / 22.99 + k_g / 39.10) * 1000 - (cl_g / 35.45 + s_g / 16.03) * 1000

    def test_dcab_sign_and_monotonicity(self):
        # Mehr K/Na -> hoehere DCAB; mehr Cl/S -> niedrigere DCAB
        base = self._dcab_meq(1.5, 12.0, 3.0, 2.0)
        more_k = self._dcab_meq(1.5, 20.0, 3.0, 2.0)
        more_cl = self._dcab_meq(1.5, 12.0, 8.0, 2.0)
        assert more_k > base
        assert more_cl < base
