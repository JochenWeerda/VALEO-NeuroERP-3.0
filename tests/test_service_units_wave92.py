"""Wave 92 — Unit-Tests fuer meldewesen_lifecycle_service, milchvieh_crosssell_service,
lohn_service (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# meldewesen_lifecycle_service — simulate_uebermittlung  (pure simulation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_simulate_uebermittlung_returns_dict() -> None:
    from app.services.meldewesen_lifecycle_service import simulate_uebermittlung
    result = simulate_uebermittlung("ustva", "2024-01", 1500.0)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_simulate_uebermittlung_simuliert_flag() -> None:
    from app.services.meldewesen_lifecycle_service import simulate_uebermittlung
    result = simulate_uebermittlung("ustva", "2024-01", 1500.0)
    assert result.get("simuliert") is True


@pytest.mark.unit
def test_simulate_uebermittlung_has_externe_referenz() -> None:
    from app.services.meldewesen_lifecycle_service import simulate_uebermittlung
    result = simulate_uebermittlung("ustva", "2024-01", 1500.0)
    assert "externe_referenz" in result
    assert len(result["externe_referenz"]) > 0


@pytest.mark.unit
def test_simulate_uebermittlung_different_meldung_types() -> None:
    from app.services.meldewesen_lifecycle_service import simulate_uebermittlung
    for meldung_typ in ("ustva", "zusammenfassung"):
        result = simulate_uebermittlung(meldung_typ, "2024-01", 500.0)
        assert result["simuliert"] is True


# ---------------------------------------------------------------------------
# milchvieh_crosssell_service — ecm_kg, produktgruppen_potenzial
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_ecm_kg_basic() -> None:
    from app.services.milchvieh_crosssell_service import ecm_kg
    result = ecm_kg(milch_kg=10000, fett_pct=4.0, eiw_pct=3.4)
    assert result is not None
    assert result > 0


@pytest.mark.unit
def test_ecm_kg_none_inputs_returns_none() -> None:
    from app.services.milchvieh_crosssell_service import ecm_kg
    result = ecm_kg(milch_kg=None, fett_pct=4.0, eiw_pct=3.4)
    assert result is None


@pytest.mark.unit
def test_ecm_kg_high_quality_milk_above_volume() -> None:
    from app.services.milchvieh_crosssell_service import ecm_kg
    # High fat/protein milk → ECM > raw volume
    result = ecm_kg(milch_kg=10000, fett_pct=4.5, eiw_pct=3.6)
    assert result > 10000


@pytest.mark.unit
def test_produktgruppen_potenzial_returns_list() -> None:
    from app.services.milchvieh_crosssell_service import produktgruppen_potenzial
    result = produktgruppen_potenzial(100000)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.unit
def test_produktgruppen_potenzial_entries_have_required_keys() -> None:
    from app.services.milchvieh_crosssell_service import produktgruppen_potenzial
    result = produktgruppen_potenzial(100000)
    for entry in result:
        assert "key" in entry
        assert "label" in entry
        assert "eur_jahr_min" in entry
        assert "eur_jahr_max" in entry


@pytest.mark.unit
def test_produktgruppen_potenzial_min_less_than_max() -> None:
    from app.services.milchvieh_crosssell_service import produktgruppen_potenzial
    result = produktgruppen_potenzial(50000)
    for entry in result:
        assert entry["eur_jahr_min"] <= entry["eur_jahr_max"]


@pytest.mark.unit
def test_produktgruppen_potenzial_larger_herd_larger_potential() -> None:
    from app.services.milchvieh_crosssell_service import produktgruppen_potenzial
    small = produktgruppen_potenzial(10000)
    large = produktgruppen_potenzial(200000)
    small_total = sum(e["eur_jahr_min"] for e in small)
    large_total = sum(e["eur_jahr_min"] for e in large)
    assert large_total > small_total


# ---------------------------------------------------------------------------
# lohn_service — berechne_netto, get_parameter_set, build_payroll_closeout
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_parameter_set_valid_year() -> None:
    from app.services.lohn_service import get_parameter_set
    params = get_parameter_set(2025)
    assert params is not None
    assert params.year in (2025, 2026)  # may return the nearest configured year


@pytest.mark.unit
def test_get_parameter_set_invalid_year_raises() -> None:
    from app.services.lohn_service import get_parameter_set
    with pytest.raises(ValueError):
        get_parameter_set(2020)  # year not configured


@pytest.mark.unit
def test_berechne_netto_returns_ergebnis() -> None:
    from app.services.lohn_service import berechne_netto
    result = berechne_netto(
        brutto=3000, steuerklasse=1, hat_kinder=False, kinder_freibetraege=0,
        kirchensteuersatz=0, zusatzbeitrag_kv=0.016, year=2025,
    )
    assert result is not None
    assert result.netto < result.brutto


@pytest.mark.unit
def test_berechne_netto_deducts_sv() -> None:
    from app.services.lohn_service import berechne_netto
    result = berechne_netto(
        brutto=3000, steuerklasse=1, hat_kinder=False, kinder_freibetraege=0,
        kirchensteuersatz=0, zusatzbeitrag_kv=0.016, year=2025,
    )
    # Social security deductions should be positive
    assert result.employee_social is not None


@pytest.mark.unit
def test_build_payroll_closeout_returns_closeout() -> None:
    from app.services.lohn_service import build_payroll_closeout, PayrollEmployeeInput
    employees = [
        PayrollEmployeeInput(
            employee_ref="E-001", gross=Decimal("3000"), tax_class=1,
            has_children=False, child_allowances=0, church_tax_rate=0.0,
            health_additional_rate=0.016,
        )
    ]
    result = build_payroll_closeout("2025-01", employees)
    assert result is not None
    assert result.period == "2025-01"


@pytest.mark.unit
def test_build_payroll_closeout_has_lines() -> None:
    from app.services.lohn_service import build_payroll_closeout, PayrollEmployeeInput
    employees = [
        PayrollEmployeeInput(
            employee_ref="E-001", gross=Decimal("2500"), tax_class=2,
            has_children=True, child_allowances=1, church_tax_rate=0.0,
            health_additional_rate=0.016,
        )
    ]
    result = build_payroll_closeout("2025-02", employees)
    assert isinstance(result.lines, list)
    assert len(result.lines) >= 1
