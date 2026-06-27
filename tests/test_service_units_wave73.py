"""Wave 73 — Unit-Tests fuer agrar_settlement_service (MoistureEngine) und atlas_customs_service."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# agrar_settlement_service — calculate_billing_weight  (pure Decimal math)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_calculate_billing_weight_basic() -> None:
    from app.services.agrar_settlement_service import calculate_billing_weight, MoistureEngineInput
    inp = MoistureEngineInput(net_weight_kg=Decimal("10000"), moisture_pct=Decimal("18.5"))
    result = calculate_billing_weight(inp)
    assert result.billing_weight_kg < Decimal("10000")  # moisture deduction reduces weight
    assert result.billing_weight_kg > 0


@pytest.mark.unit
def test_calculate_billing_weight_at_target_moisture_no_deduction() -> None:
    from app.services.agrar_settlement_service import calculate_billing_weight, MoistureEngineInput
    # At target moisture (14%) there should be no moisture deduction
    inp = MoistureEngineInput(
        net_weight_kg=Decimal("10000"),
        moisture_pct=Decimal("14.0"),
        target_moisture_pct=Decimal("14.0"),
    )
    result = calculate_billing_weight(inp)
    assert result.moisture_factor == pytest.approx(1.0, rel=1e-3)


@pytest.mark.unit
def test_calculate_billing_weight_high_moisture_bigger_deduction() -> None:
    from app.services.agrar_settlement_service import calculate_billing_weight, MoistureEngineInput
    inp_low = MoistureEngineInput(net_weight_kg=Decimal("10000"), moisture_pct=Decimal("16"))
    inp_high = MoistureEngineInput(net_weight_kg=Decimal("10000"), moisture_pct=Decimal("20"))
    r_low = calculate_billing_weight(inp_low)
    r_high = calculate_billing_weight(inp_high)
    assert r_high.billing_weight_kg < r_low.billing_weight_kg


@pytest.mark.unit
def test_calculate_billing_weight_result_fields() -> None:
    from app.services.agrar_settlement_service import calculate_billing_weight, MoistureEngineInput
    import dataclasses
    inp = MoistureEngineInput(net_weight_kg=Decimal("5000"), moisture_pct=Decimal("15"))
    result = calculate_billing_weight(inp)
    fields = dataclasses.asdict(result)
    for key in ("net_weight_kg", "billing_weight_kg", "moisture_factor", "impurities_factor", "deduction_kg"):
        assert key in fields


@pytest.mark.unit
def test_calculate_billing_weight_deduction_formula() -> None:
    from app.services.agrar_settlement_service import calculate_billing_weight, MoistureEngineInput
    inp = MoistureEngineInput(net_weight_kg=Decimal("10000"), moisture_pct=Decimal("18.5"))
    result = calculate_billing_weight(inp)
    # deduction_kg = net_weight - billing_weight
    expected = float(result.net_weight_kg - result.billing_weight_kg)
    assert float(result.deduction_kg) == pytest.approx(expected, rel=1e-3)


@pytest.mark.unit
def test_calculate_billing_weight_with_impurities() -> None:
    from app.services.agrar_settlement_service import calculate_billing_weight, MoistureEngineInput
    inp_clean = MoistureEngineInput(net_weight_kg=Decimal("10000"), moisture_pct=Decimal("14"), impurities_pct=Decimal("0"))
    inp_dirty = MoistureEngineInput(net_weight_kg=Decimal("10000"), moisture_pct=Decimal("14"), impurities_pct=Decimal("5"))
    r_clean = calculate_billing_weight(inp_clean)
    r_dirty = calculate_billing_weight(inp_dirty)
    # Higher impurities should reduce billing weight
    assert r_dirty.billing_weight_kg <= r_clean.billing_weight_kg


# ---------------------------------------------------------------------------
# atlas_customs_service — generate_mrn, simulate_taric_check  (pure)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_generate_mrn_returns_string() -> None:
    from app.services.atlas_customs_service import generate_mrn
    mrn = generate_mrn("DE")
    assert isinstance(mrn, str)
    assert len(mrn) > 5


@pytest.mark.unit
def test_generate_mrn_starts_with_country_code() -> None:
    from app.services.atlas_customs_service import generate_mrn
    mrn = generate_mrn("DE")
    assert mrn.startswith("DE")


@pytest.mark.unit
def test_generate_mrn_different_each_call() -> None:
    from app.services.atlas_customs_service import generate_mrn
    mrn1 = generate_mrn("DE")
    mrn2 = generate_mrn("DE")
    assert mrn1 != mrn2


@pytest.mark.unit
def test_generate_mrn_different_country() -> None:
    from app.services.atlas_customs_service import generate_mrn
    mrn_de = generate_mrn("DE")
    mrn_nl = generate_mrn("NL")
    assert mrn_nl.startswith("NL")


@pytest.mark.unit
def test_simulate_taric_check_valid_position() -> None:
    from app.services.atlas_customs_service import simulate_taric_check
    positionen = [{"waren_nr": "10019900", "bezeichnung": "Weichweizen"}]
    result = simulate_taric_check(positionen)
    assert "positionen" in result
    assert "hat_fehler" in result
    assert len(result["positionen"]) == 1


@pytest.mark.unit
def test_simulate_taric_check_missing_waren_nr() -> None:
    from app.services.atlas_customs_service import simulate_taric_check
    positionen = [{"bezeichnung": "Unbekannte Ware"}]
    result = simulate_taric_check(positionen)
    assert result["hat_fehler"] is True
    # Should report error about missing Warennummer
    pos = result["positionen"][0]
    assert len(pos.get("fehler", [])) > 0


@pytest.mark.unit
def test_simulate_taric_check_multiple_positions() -> None:
    from app.services.atlas_customs_service import simulate_taric_check
    positionen = [
        {"waren_nr": "10019900", "bezeichnung": "Weizen"},
        {"waren_nr": "12019900", "bezeichnung": "Sojabohnen"},
    ]
    result = simulate_taric_check(positionen)
    assert len(result["positionen"]) == 2


@pytest.mark.unit
def test_simulate_taric_check_empty_positions() -> None:
    from app.services.atlas_customs_service import simulate_taric_check
    result = simulate_taric_check([])
    assert "positionen" in result
    assert result["positionen"] == []
