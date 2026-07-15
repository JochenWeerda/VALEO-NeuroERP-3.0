from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]


def test_fm_tm_quantity_and_concentration_are_inverse_properties() -> None:
    from app.agrar.rations.reference_data import BasisValueKind, MatterBasis, convert_basis

    dry_matter_values = (Decimal("0.1"), Decimal("12.5"), Decimal("35"), Decimal("88.4"), Decimal("100"))
    source_values = (Decimal("0"), Decimal("0.001"), Decimal("7.25"), Decimal("999999.999"))
    for dry_matter_pct in dry_matter_values:
        for source in source_values:
            for kind in BasisValueKind:
                converted = convert_basis(
                    source,
                    from_basis=MatterBasis.FRESH_MATTER,
                    to_basis=MatterBasis.DRY_MATTER,
                    dry_matter_pct=dry_matter_pct,
                    kind=kind,
                )
                restored = convert_basis(
                    converted,
                    from_basis=MatterBasis.DRY_MATTER,
                    to_basis=MatterBasis.FRESH_MATTER,
                    dry_matter_pct=dry_matter_pct,
                    kind=kind,
                )
                # Repeating decimal fractions (for example 88.4 %) cannot be
                # represented exactly; the domain contract permits only a
                # sub-yocto residual before the explicit display rounding.
                assert abs(restored - source) <= Decimal("1e-24")


def test_basis_validation_dimension_guard_and_rounding_are_explicit() -> None:
    from app.agrar.rations.reference_data import (
        MatterBasis,
        RoundingMode,
        UnitDefinition,
        convert_basis,
        convert_unit,
        round_decimal,
    )

    with pytest.raises(ValueError, match="Trockenmasse"):
        convert_basis(Decimal("10"), MatterBasis.FRESH_MATTER, MatterBasis.DRY_MATTER, Decimal("0"))
    with pytest.raises(ValueError, match="Trockenmasse"):
        convert_basis(Decimal("10"), MatterBasis.FRESH_MATTER, MatterBasis.DRY_MATTER, Decimal("100.1"))

    kg = UnitDefinition("kg", "Kilogramm", "mass", Decimal("1"), 3)
    gram = UnitDefinition("g", "Gramm", "mass", Decimal("0.001"), 1)
    megajoule = UnitDefinition("MJ", "Megajoule", "energy", Decimal("1"), 2)
    assert convert_unit(Decimal("1.250"), kg, gram) == Decimal("1250.0")
    with pytest.raises(ValueError, match="Dimension"):
        convert_unit(Decimal("1"), kg, megajoule)

    assert round_decimal(Decimal("1.005"), 2, RoundingMode.HALF_UP) == Decimal("1.01")
    assert round_decimal(Decimal("1.005"), 2, RoundingMode.HALF_EVEN) == Decimal("1.00")


def test_reference_data_migration_is_versioned_seeded_and_append_only() -> None:
    migration = ROOT / "alembic" / "versions" / "feed_core_reference_data_20260715.py"
    source = migration.read_text(encoding="utf-8")
    assert 'down_revision = "feed_core_groups_20260715"' in source
    for table in ("feeding_unit_definitions", "feeding_nutrient_definitions", "feeding_reference_revisions"):
        assert table in source
    for seed in ("dry_matter", "crude_protein", "net_energy_lactation", "mycotoxin"):
        assert seed in source
    assert "ON CONFLICT" in source
    assert "guard_immutable_feeding_reference_revision" in source


def test_reference_screen_is_native_meridian_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("agrar/feeding-reference-data")
    assert definition is not None
    assert definition["adapter"] == {
        "type": "native", "sourceId": "agrar/feeding-reference-data", "temporary": False
    }
    assert definition["layout"]["floorplan"] == "listReport"
    assert {table["key"] for table in definition["tables"]} == {"nutrients", "units"}
    assert _check_readiness(definition)["generatorReady"] is True


def test_reference_api_has_typed_read_and_conversion_contracts() -> None:
    from app.api.v1.endpoints.rations_reference_data import (
        BasisConversionOut,
        NutrientDefinitionOut,
        UnitDefinitionOut,
        router,
    )

    response_models = {
        (route.path, next(iter(route.methods or []))): route.response_model
        for route in router.routes
        if hasattr(route, "response_model")
    }
    assert response_models[("/reference-data/nutrients", "GET")] == list[NutrientDefinitionOut]
    assert response_models[("/reference-data/units", "GET")] == list[UnitDefinitionOut]
    assert response_models[("/reference-data/convert-basis", "POST")] is BasisConversionOut
