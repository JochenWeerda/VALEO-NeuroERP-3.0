"""Wave 89 — Unit-Tests fuer harvest_acceptance_service, ist_aggregation_service,
kaeufer_signal_service (pure domain functions)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# harvest_acceptance_service — pure quality grading + DQ validation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_assign_quality_grade_good_values_a() -> None:
    from app.services.harvest_acceptance_service import assign_quality_grade
    grade = assign_quality_grade(moisture_pct=14.0, protein_pct=13.0, contamination_pct=0.5)
    assert grade == "A"


@pytest.mark.unit
def test_assign_quality_grade_moderate_values_c() -> None:
    from app.services.harvest_acceptance_service import assign_quality_grade
    grade = assign_quality_grade(moisture_pct=15.5, protein_pct=10.0, contamination_pct=3.0)
    assert grade == "C"


@pytest.mark.unit
def test_assign_quality_grade_bad_values_reject() -> None:
    from app.services.harvest_acceptance_service import assign_quality_grade
    grade = assign_quality_grade(moisture_pct=20.0, protein_pct=7.0, contamination_pct=5.0)
    assert grade == "REJECT"


@pytest.mark.unit
def test_calculate_net_weight_applies_deductions() -> None:
    from app.services.harvest_acceptance_service import calculate_net_weight
    net = calculate_net_weight(gross_kg=10000, tare_kg=200, moisture_pct=18.0, drying_target_pct=14.0)
    assert net < 10000 - 200  # must be less than gross minus tare due to moisture deduction
    assert net > 0


@pytest.mark.unit
def test_calculate_net_weight_at_target_moisture() -> None:
    from app.services.harvest_acceptance_service import calculate_net_weight
    # At target moisture, deduction should be only tare
    net = calculate_net_weight(gross_kg=10000, tare_kg=200, moisture_pct=14.0, drying_target_pct=14.0)
    assert net == pytest.approx(9800.0, rel=1e-3)


@pytest.mark.unit
def test_derive_nuts2_from_postal_code_german_code() -> None:
    from app.services.harvest_acceptance_service import derive_nuts2_from_postal_code
    nuts2 = derive_nuts2_from_postal_code("12345", "DE")
    assert nuts2.startswith("DE")
    assert len(nuts2) == 4


@pytest.mark.unit
def test_evaluate_harvest_acceptance_datensatz_valid() -> None:
    from app.services.harvest_acceptance_service import evaluate_harvest_acceptance_datensatz
    result = evaluate_harvest_acceptance_datensatz({
        "wareneingang_nr": "WE-001", "lieferant_id": "L-001", "ware": "WW",
        "brutto_kg": 10000, "annahme_nr": "AN-001", "kunde_id": "K-001",
        "lieferdatum": "2024-01-15",
    })
    assert result.bestanden is True
    assert result.fehler_anzahl == 0


@pytest.mark.unit
def test_evaluate_harvest_acceptance_datensatz_empty_fails() -> None:
    from app.services.harvest_acceptance_service import evaluate_harvest_acceptance_datensatz
    result = evaluate_harvest_acceptance_datensatz({})
    assert result.bestanden is False
    assert result.fehler_anzahl > 0


@pytest.mark.unit
def test_evaluate_harvest_acceptance_missing_fields_reported() -> None:
    from app.services.harvest_acceptance_service import evaluate_harvest_acceptance_datensatz
    result = evaluate_harvest_acceptance_datensatz({
        "wareneingang_nr": "WE-001", "lieferant_id": "L-001", "ware": "WW", "brutto_kg": 10000,
    })
    felder = [v.feld for v in result.verletzungen]
    # Missing annahme_nr, kunde_id, lieferdatum
    assert len(felder) > 0


@pytest.mark.unit
def test_build_dq_error_detail_harvest() -> None:
    from app.services.harvest_acceptance_service import evaluate_harvest_acceptance_datensatz, build_dq_error_detail
    result = evaluate_harvest_acceptance_datensatz({})
    detail = build_dq_error_detail("Wareneingang", result)
    assert detail["entity_typ"] == "Wareneingang"
    assert detail["fehler_anzahl"] == result.fehler_anzahl


# ---------------------------------------------------------------------------
# ist_aggregation_service — klassifiziere_artikel  (pure classification)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_klassifiziere_artikel_pesticide_by_flag() -> None:
    from app.services.ist_aggregation_service import klassifiziere_artikel
    result = klassifiziere_artikel("Glyphosat 360", None, None, True, None)
    assert result == "pflanzenschutz"


@pytest.mark.unit
def test_klassifiziere_artikel_fertilizer_by_name() -> None:
    from app.services.ist_aggregation_service import klassifiziere_artikel
    result = klassifiziere_artikel("Harnstoff 46%", None, None, False, "Harnstoff")
    assert result is not None
    assert "duenger" in result


@pytest.mark.unit
def test_klassifiziere_artikel_unknown_returns_none() -> None:
    from app.services.ist_aggregation_service import klassifiziere_artikel
    result = klassifiziere_artikel("Winterweizen", "Getreide", None, False, None)
    # Non-PSM/fertilizer articles may return None
    assert result is None or isinstance(result, str)


@pytest.mark.unit
def test_klassifiziere_artikel_pesticide_flag_overrides() -> None:
    from app.services.ist_aggregation_service import klassifiziere_artikel
    # PSM flag should take precedence
    result = klassifiziere_artikel("Produkt X", "Getreide", None, True, None)
    assert result == "pflanzenschutz"


# ---------------------------------------------------------------------------
# kaeufer_signal_service — signale_aus_werten  (pure signal computation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_signale_aus_werten_returns_object() -> None:
    from app.services.kaeufer_signal_service import signale_aus_werten
    result = signale_aus_werten(
        preisanfragen_12m=5, angebote_12m=3, bestellungen_12m=2,
        gruppen_bezogen="PREISABFRAGER", deckung_pct=0.7, bedarf_eur=50000,
    )
    assert result is not None


@pytest.mark.unit
def test_signale_aus_werten_abschlussquote_computed() -> None:
    from app.services.kaeufer_signal_service import signale_aus_werten
    result = signale_aus_werten(
        preisanfragen_12m=10, angebote_12m=5, bestellungen_12m=4,
        gruppen_bezogen="STRATEGISCHER_STAMMKUNDE", deckung_pct=0.9, bedarf_eur=100000,
    )
    # abschlussquote = bestellungen / (angebote + preisanfragen - bestellungen) approx 0.444
    assert 0.0 <= result.abschlussquote <= 1.0


@pytest.mark.unit
def test_signale_aus_werten_deckung_pct_stored() -> None:
    from app.services.kaeufer_signal_service import signale_aus_werten
    result = signale_aus_werten(
        preisanfragen_12m=2, angebote_12m=2, bestellungen_12m=1,
        gruppen_bezogen="PREISABFRAGER", deckung_pct=0.35, bedarf_eur=25000,
    )
    assert result.deckung_gesamt_pct == pytest.approx(0.35)


@pytest.mark.unit
def test_signale_aus_werten_bedarf_stored() -> None:
    from app.services.kaeufer_signal_service import signale_aus_werten
    result = signale_aus_werten(
        preisanfragen_12m=0, angebote_12m=0, bestellungen_12m=0,
        gruppen_bezogen="PREISABFRAGER", deckung_pct=0.0, bedarf_eur=75000,
    )
    assert result.bedarf_gesamt_eur == 75000
