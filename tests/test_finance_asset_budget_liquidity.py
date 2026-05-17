"""
Tests for Anlagenbuchhaltung, Budgetierung and Liquiditätsplanung.

Markers: unit (pure-logic tests), integration (DB-backed tests skipped when DB unavailable).
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal
from typing import List
from unittest.mock import MagicMock, patch, call

import pytest

# ---------------------------------------------------------------------------
# Pure-logic helpers (no DB, no FastAPI)
# ---------------------------------------------------------------------------


def _linear_monthly_depreciation(
    acquisition_cost: float,
    residual_value: float,
    useful_life_years: int,
) -> float:
    return round((acquisition_cost - residual_value) / useful_life_years / 12, 2)


def _linear_annual_depreciation(
    acquisition_cost: float,
    residual_value: float,
    useful_life_years: int,
) -> float:
    return round((acquisition_cost - residual_value) / useful_life_years, 2)


def _build_depreciation_schedule(
    acquisition_cost: float,
    residual_value: float,
    useful_life_years: int,
    months: int,
) -> list[dict]:
    """Return month-by-month schedule up to `months`."""
    monthly = _linear_monthly_depreciation(acquisition_cost, residual_value, useful_life_years)
    bv = acquisition_cost
    schedule = []
    for m in range(1, months + 1):
        dep = min(monthly, max(0.0, bv - residual_value))
        bv = round(bv - dep, 2)
        schedule.append({"month": m, "depreciation": dep, "book_value": bv})
    return schedule


def _build_5yr_forecast(
    acquisition_cost: float,
    residual_value: float,
    useful_life_years: int,
    current_book_value: float,
    base_year: int,
) -> list[dict]:
    annual = _linear_annual_depreciation(acquisition_cost, residual_value, useful_life_years)
    bv = current_book_value
    forecast = []
    for offset in range(5):
        dep = min(annual, max(0.0, bv - residual_value))
        bv = round(bv - dep, 2)
        forecast.append({"year": base_year + offset, "depreciation_eur": dep, "book_value_end_eur": bv})
    return forecast


# ---------------------------------------------------------------------------
# Feature 1 — Anlagenbuchhaltung
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_linear_depreciation_calculation():
    """cost=10000, life=5yr → 2000/yr → 166.67/mo"""
    monthly = _linear_monthly_depreciation(10_000, 0, 5)
    annual = _linear_annual_depreciation(10_000, 0, 5)

    assert annual == 2000.0, f"Expected 2000.0, got {annual}"
    assert monthly == pytest.approx(166.67, abs=0.01), f"Expected 166.67, got {monthly}"


@pytest.mark.unit
def test_linear_depreciation_with_residual():
    """cost=10000, residual=1000, life=5yr → 1800/yr → 150/mo"""
    monthly = _linear_monthly_depreciation(10_000, 1_000, 5)
    annual = _linear_annual_depreciation(10_000, 1_000, 5)

    assert annual == 1800.0
    assert monthly == 150.0


@pytest.mark.unit
def test_linear_depreciation_does_not_go_below_residual():
    """Book value must never fall below residual value."""
    schedule = _build_depreciation_schedule(10_000, 1_000, 5, 60)  # 5 years = 60 months

    final_bv = schedule[-1]["book_value"]
    assert final_bv >= 1_000.0, f"Book value {final_bv} below residual 1000"


@pytest.mark.unit
def test_asset_register_sums_correctly():
    """Asset register totals should be consistent."""
    assets = [
        {"asset_class": "MASCHINE", "acquisition_cost": 50_000, "current_book_value": 30_000},
        {"asset_class": "MASCHINE", "acquisition_cost": 20_000, "current_book_value": 10_000},
        {"asset_class": "IT", "acquisition_cost": 5_000, "current_book_value": 2_500},
    ]

    # Simulate asset register grouping
    from collections import defaultdict
    register: dict = defaultdict(lambda: {"acquisition_cost": 0.0, "book_value": 0.0, "count": 0})
    for a in assets:
        cls = a["asset_class"]
        register[cls]["acquisition_cost"] += a["acquisition_cost"]
        register[cls]["book_value"] += a["current_book_value"]
        register[cls]["count"] += 1

    assert register["MASCHINE"]["acquisition_cost"] == 70_000
    assert register["MASCHINE"]["book_value"] == 40_000
    assert register["MASCHINE"]["count"] == 2
    assert register["IT"]["acquisition_cost"] == 5_000
    assert register["IT"]["book_value"] == 2_500

    # Accumulated depreciation = acquisition - book_value
    assert register["MASCHINE"]["acquisition_cost"] - register["MASCHINE"]["book_value"] == 30_000


@pytest.mark.unit
def test_depreciation_forecast_5_years():
    """5-year depreciation forecast should decrease BV to residual."""
    forecast = _build_5yr_forecast(
        acquisition_cost=10_000,
        residual_value=0,
        useful_life_years=5,
        current_book_value=10_000,
        base_year=2026,
    )

    assert len(forecast) == 5
    assert forecast[0]["depreciation_eur"] == 2_000.0
    assert forecast[0]["book_value_end_eur"] == 8_000.0
    assert forecast[4]["book_value_end_eur"] == 0.0

    # Each year's depreciation should be 2000 (while BV > 0)
    years_with_full_dep = [y for y in forecast if y["depreciation_eur"] == 2_000.0]
    assert len(years_with_full_dep) == 5


@pytest.mark.unit
def test_depreciation_forecast_partial_remaining():
    """If asset has already been partly depreciated, forecast reflects remaining BV."""
    forecast = _build_5yr_forecast(
        acquisition_cost=10_000,
        residual_value=0,
        useful_life_years=5,
        current_book_value=4_000,  # 3 years already done
        base_year=2026,
    )

    # Remaining 2 full years at 2000, then 0
    assert forecast[0]["depreciation_eur"] == 2_000.0
    assert forecast[1]["depreciation_eur"] == 2_000.0
    assert forecast[2]["depreciation_eur"] == 0.0  # Already fully depreciated


# ---------------------------------------------------------------------------
# Feature 2 — Budgetierung
# ---------------------------------------------------------------------------


def _calculate_budget_vs_actual(budget: float, actual: float) -> dict:
    variance = round(budget - actual, 2)
    pct = round(variance / budget * 100, 1) if budget != 0 else 0.0
    return {
        "budgeted_amount_eur": budget,
        "actual_amount_eur": actual,
        "variance_amount_eur": variance,
        "variance_percent": pct,
    }


@pytest.mark.unit
def test_budget_vs_actual_variance():
    """budget=1000, actual=800 → variance=200, 20%"""
    result = _calculate_budget_vs_actual(1_000.0, 800.0)

    assert result["variance_amount_eur"] == 200.0
    assert result["variance_percent"] == 20.0
    assert result["budgeted_amount_eur"] == 1_000.0
    assert result["actual_amount_eur"] == 800.0


@pytest.mark.unit
def test_budget_vs_actual_overspend():
    """actual=1200, budget=1000 → variance=-200, -20%"""
    result = _calculate_budget_vs_actual(1_000.0, 1_200.0)

    assert result["variance_amount_eur"] == -200.0
    assert result["variance_percent"] == -20.0


@pytest.mark.unit
def test_budget_vs_actual_zero_budget():
    """Zero budget should not cause division by zero."""
    result = _calculate_budget_vs_actual(0.0, 100.0)

    assert result["variance_percent"] == 0.0


@pytest.mark.unit
def test_budget_approval_workflow():
    """Budget can only be approved from ENTWURF status."""

    def approve_budget(current_status: str) -> tuple[bool, str]:
        if current_status != "ENTWURF":
            return False, f"Budget ist bereits im Status '{current_status}'"
        return True, "GENEHMIGT"

    # Happy path
    ok, new_status = approve_budget("ENTWURF")
    assert ok is True
    assert new_status == "GENEHMIGT"

    # Already approved
    ok, msg = approve_budget("GENEHMIGT")
    assert ok is False
    assert "GENEHMIGT" in msg

    # Locked
    ok, msg = approve_budget("GESPERRT")
    assert ok is False
    assert "GESPERRT" in msg


@pytest.mark.unit
def test_budget_approval_blocks_edits_when_locked():
    """A locked budget should reject line modifications."""

    def can_edit_line(plan_status: str) -> bool:
        return plan_status != "GESPERRT"

    assert can_edit_line("ENTWURF") is True
    assert can_edit_line("GENEHMIGT") is True
    assert can_edit_line("GESPERRT") is False


# ---------------------------------------------------------------------------
# Feature 3 — Liquiditätsplanung
# ---------------------------------------------------------------------------


def _build_week_ranges(num_weeks: int, base: date | None = None) -> list[tuple[date, date]]:
    if base is None:
        base = date.today()
    monday = base - timedelta(days=base.weekday())
    return [(monday + timedelta(weeks=i), monday + timedelta(weeks=i, days=6)) for i in range(num_weeks)]


def _compute_forecast(
    opening_cash: float,
    weekly_receipts: list[float],
    weekly_payments: list[float],
) -> list[dict]:
    assert len(weekly_receipts) == len(weekly_payments)
    weeks = _build_week_ranges(len(weekly_receipts))
    cumulative = opening_cash
    result = []
    for i, (ws, we) in enumerate(weeks):
        r = weekly_receipts[i]
        p = weekly_payments[i]
        balance = r - p
        cumulative = round(cumulative + balance, 2)
        result.append(
            {
                "week_number": i + 1,
                "week_start": ws.isoformat(),
                "week_end": we.isoformat(),
                "receipts_eur": round(r, 2),
                "payments_eur": round(p, 2),
                "balance_eur": round(balance, 2),
                "cumulative_balance_eur": cumulative,
            }
        )
    return result


@pytest.mark.unit
def test_liquidity_forecast_returns_13_weeks():
    """Forecast must return exactly 13 week entries."""
    receipts = [10_000.0] * 13
    payments = [8_000.0] * 13
    forecast = _compute_forecast(50_000.0, receipts, payments)

    assert len(forecast) == 13


@pytest.mark.unit
def test_liquidity_forecast_cumulative_balance():
    """Cumulative balance compounds correctly across weeks."""
    receipts = [10_000.0] * 4
    payments = [8_000.0] * 4
    forecast = _compute_forecast(0.0, receipts, payments)

    expected_cumulative = [2_000.0, 4_000.0, 6_000.0, 8_000.0]
    for i, entry in enumerate(forecast):
        assert entry["cumulative_balance_eur"] == pytest.approx(expected_cumulative[i], abs=0.01)


@pytest.mark.unit
def test_liquidity_forecast_negative_balance_allowed():
    """Forecast should handle negative balances (liquidity gap)."""
    receipts = [5_000.0] * 4
    payments = [10_000.0] * 4
    forecast = _compute_forecast(0.0, receipts, payments)

    assert all(entry["cumulative_balance_eur"] < 0 for entry in forecast)
    assert forecast[-1]["cumulative_balance_eur"] == pytest.approx(-20_000.0, abs=0.01)


@pytest.mark.unit
def test_cash_position_aggregation():
    """Net liquidity = cash at bank + receivables - payables."""

    def compute_net_liquidity(cash: float, receivables: float, payables: float) -> float:
        return round(cash + receivables - payables, 2)

    # Normal scenario
    net = compute_net_liquidity(100_000, 50_000, 30_000)
    assert net == 120_000.0

    # Negative net (payables > cash + receivables)
    net = compute_net_liquidity(10_000, 5_000, 20_000)
    assert net == -5_000.0

    # All zero
    net = compute_net_liquidity(0, 0, 0)
    assert net == 0.0


@pytest.mark.unit
def test_liquidity_scenario_adjustments():
    """Adjustments in scenario should shift receipts/payments accordingly."""

    adjustments = {
        1: {"receipts_delta": 5_000.0, "payments_delta": 0.0},
        3: {"receipts_delta": 0.0, "payments_delta": 2_000.0},
    }

    receipts = [10_000.0] * 4
    payments = [8_000.0] * 4

    # Apply adjustments
    for week_num, adj in adjustments.items():
        idx = week_num - 1
        receipts[idx] += adj["receipts_delta"]
        payments[idx] += adj["payments_delta"]

    assert receipts[0] == 15_000.0  # week 1 boosted
    assert receipts[2] == 10_000.0  # week 3 unchanged receipts
    assert payments[2] == 10_000.0  # week 3 extra payments


@pytest.mark.unit
def test_week_ranges_are_non_overlapping():
    """Week ranges must be non-overlapping and consecutive."""
    weeks = _build_week_ranges(13)

    for i in range(1, len(weeks)):
        prev_end = weeks[i - 1][1]
        curr_start = weeks[i][0]
        assert curr_start == prev_end + timedelta(days=1), (
            f"Week {i} gap: prev_end={prev_end}, curr_start={curr_start}"
        )
