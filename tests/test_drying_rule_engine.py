from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from modules.agrar.services.drying_rule_engine import (
    DryingFactorRange,
    DryingLookupRow,
    DryingRuleSet,
    compute_settlement,
    round_moisture_to_0_1,
)


class InMemoryRepo:
    def __init__(self, rule_set: DryingRuleSet, *, lookup: list[DryingLookupRow] | None = None, ranges: list[DryingFactorRange] | None = None):
        self._rs = rule_set
        self._lookup = lookup or []
        self._ranges = ranges or []

    def find_rule_set(
        self,
        *,
        crop_code: str,
        site_id: str | None,
        calc_date: date,
        contract_id: str | None = None,
        customer_id: str | None = None,
    ) -> DryingRuleSet:
        assert crop_code == self._rs.crop_code
        return self._rs

    def list_lookup_rows(self, *, rule_set_id: str) -> list[DryingLookupRow]:
        assert rule_set_id == self._rs.id
        return self._lookup

    def list_factor_ranges(self, *, rule_set_id: str) -> list[DryingFactorRange]:
        assert rule_set_id == self._rs.id
        return self._ranges


def test_rounding_modes_to_point_one():
    v = Decimal("20.27")
    assert round_moisture_to_0_1(v, "ROUND_NEAREST") == Decimal("20.3")
    assert round_moisture_to_0_1(v, "ROUND_UP") == Decimal("20.3")
    assert round_moisture_to_0_1(v, "ROUND_DOWN") == Decimal("20.2")


def test_maize_lookup_table_example():
    rs = DryingRuleSet(
        id="rs-maize",
        version=1,
        crop_code="MAIZE",
        site_id=None,
        valid_from=None,
        valid_to=None,
        method="LOOKUP_TABLE",
        base_moisture_pct=Decimal("15.0"),
        rounding_mode="ROUND_NEAREST",
        clamp_mode="HARD_ERROR",
    )
    repo = InMemoryRepo(
        rs,
        lookup=[
            DryingLookupRow(
                moisture_pct=Decimal("20.0"),
                entzug_pct_points=Decimal("5.0"),
                loss_pct=Decimal("6.75"),
            )
        ],
    )
    result = compute_settlement(
        repo,
        {
            "cropCode": "MAIZE",
            "netWeightKg": 1000,
            "moisturePct": 20.0,
            "calcDate": "2026-02-17",
        },
    )
    assert result.entzug_pct_points == Decimal("5.0")
    assert float(result.loss_pct) == pytest.approx(6.75, abs=1e-9)
    assert float(result.invoice_weight_kg) == pytest.approx(932.5, abs=1e-6)


def test_rapeseed_dry_matter_normalization_example():
    rs = DryingRuleSet(
        id="rs-raps",
        version=1,
        crop_code="RAPESEED",
        site_id=None,
        valid_from=None,
        valid_to=None,
        method="DRY_MATTER_NORMALIZATION",
        base_moisture_pct=Decimal("9.0"),
        rounding_mode="ROUND_NEAREST",
        clamp_mode="HARD_ERROR",
    )
    repo = InMemoryRepo(rs)
    result = compute_settlement(
        repo,
        {
            "cropCode": "RAPESEED",
            "netWeightKg": 1000,
            "moisturePct": 12.0,
            "calcDate": "2026-02-17",
        },
    )
    # 1000 * 88 / 91 = 967.032967...
    assert float(result.invoice_weight_kg) == pytest.approx(967.03297, abs=1e-5)
    assert float(result.loss_kg) == pytest.approx(32.96703, abs=1e-5)
    assert result.entzug_pct_points == Decimal("3.0")


def test_wheat_factor_from_base_example():
    rs = DryingRuleSet(
        id="rs-wheat",
        version=1,
        crop_code="WHEAT",
        site_id=None,
        valid_from=None,
        valid_to=None,
        method="FACTOR_FROM_BASE",
        base_moisture_pct=Decimal("14.5"),
        start_threshold_moisture_pct=Decimal("15.1"),
        rounding_mode="ROUND_NEAREST",
        clamp_mode="HARD_ERROR",
    )
    repo = InMemoryRepo(
        rs,
        ranges=[
            DryingFactorRange(from_moisture_incl=Decimal("15.1"), to_moisture_incl=Decimal("19.4"), factor=Decimal("1.3")),
            DryingFactorRange(from_moisture_incl=Decimal("19.5"), to_moisture_incl=Decimal("29.9"), factor=Decimal("1.4")),
            DryingFactorRange(from_moisture_incl=Decimal("30.0"), to_moisture_incl=Decimal("99.9"), factor=Decimal("1.5")),
        ],
    )
    result = compute_settlement(
        repo,
        {
            "cropCode": "WHEAT",
            "netWeightKg": 1000,
            "moisturePct": 18.0,
            "calcDate": "2026-02-17",
        },
    )
    assert result.entzug_pct_points == Decimal("3.5")
    assert float(result.loss_pct) == pytest.approx(4.55, abs=1e-6)
    assert float(result.invoice_weight_kg) == pytest.approx(954.5, abs=1e-6)



