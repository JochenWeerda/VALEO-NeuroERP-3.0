"""Unit-Tests für HarvestAcceptanceService Pure-Functions.

Testet calculate_net_weight und assign_quality_grade ohne Datenbankverbindung.
"""
import pytest

from app.services.harvest_acceptance_service import (
    assign_quality_grade,
    calculate_net_weight,
)


# ── calculate_net_weight ─────────────────────────────────────────────────────

class TestCalculateNetWeight:
    def test_standard_case_no_moisture_correction(self):
        """Feuchte gleich Zielwert → kein Trocknungsabzug."""
        result = calculate_net_weight(
            gross_kg=20_000.0,
            tare_kg=5_000.0,
            moisture_pct=14.0,
            drying_target_pct=14.0,
        )
        assert result == 15_000.0

    def test_moisture_above_target_reduces_weight(self):
        """Feuchte > Zielwert → Trocknungsabzug wird angewandt."""
        # netto_feucht = 20000 - 5000 = 15000
        # abzug = 15000 * (16 - 14) / 100 = 300
        # netto_trocken = 15000 - 300 = 14700
        result = calculate_net_weight(
            gross_kg=20_000.0,
            tare_kg=5_000.0,
            moisture_pct=16.0,
            drying_target_pct=14.0,
        )
        assert result == pytest.approx(14_700.0, rel=1e-6)

    def test_moisture_below_target_no_reduction(self):
        """Feuchte < Zielwert → kein negativer Abzug (Bonus wird nicht gegeben)."""
        result = calculate_net_weight(
            gross_kg=10_000.0,
            tare_kg=2_000.0,
            moisture_pct=12.0,
            drying_target_pct=14.0,
        )
        assert result == 8_000.0

    def test_negative_gross_raises_value_error(self):
        with pytest.raises(ValueError, match="negativ"):
            calculate_net_weight(-100.0, 0.0, 14.0, 14.0)

    def test_tare_exceeds_gross_raises_value_error(self):
        with pytest.raises(ValueError, match="Tara"):
            calculate_net_weight(1_000.0, 2_000.0, 14.0, 14.0)

    def test_result_rounded_to_three_decimal_places(self):
        """Ergebnis auf 3 Dezimalstellen gerundet."""
        # 9999 - 1000 = 8999, abzug = 8999 * 1 / 100 = 89.99
        # netto = 8999 - 89.99 = 8909.01
        result = calculate_net_weight(
            gross_kg=9_999.0,
            tare_kg=1_000.0,
            moisture_pct=15.0,
            drying_target_pct=14.0,
        )
        assert result == round(result, 3)


# ── assign_quality_grade ─────────────────────────────────────────────────────

class TestAssignQualityGrade:
    def test_grade_a_premium_quality(self):
        assert assign_quality_grade(moisture_pct=13.5, protein_pct=13.0, contamination_pct=0.5) == "A"

    def test_grade_b_good_quality(self):
        assert assign_quality_grade(moisture_pct=14.5, protein_pct=11.0, contamination_pct=1.5) == "B"

    def test_grade_c_acceptable_quality(self):
        assert assign_quality_grade(moisture_pct=15.5, protein_pct=9.0, contamination_pct=2.5) == "C"

    def test_reject_too_wet(self):
        """Feuchte > 16 % → REJECT."""
        assert assign_quality_grade(moisture_pct=17.0, protein_pct=13.0, contamination_pct=0.0) == "REJECT"

    def test_reject_too_much_contamination(self):
        """Verunreinigung > 3 % → REJECT, auch wenn andere Parameter gut."""
        assert assign_quality_grade(moisture_pct=13.0, protein_pct=13.0, contamination_pct=4.0) == "REJECT"

    def test_reject_low_protein(self):
        """Protein < 8 % → REJECT."""
        assert assign_quality_grade(moisture_pct=13.0, protein_pct=5.0, contamination_pct=0.5) == "REJECT"

    def test_invalid_moisture_raises_value_error(self):
        with pytest.raises(ValueError, match="Feuchte"):
            assign_quality_grade(moisture_pct=150.0, protein_pct=12.0, contamination_pct=0.5)

    def test_boundary_a_exactly_at_threshold(self):
        """Exakt an der A-Grenze → A."""
        assert assign_quality_grade(moisture_pct=14.0, protein_pct=12.0, contamination_pct=1.0) == "A"
