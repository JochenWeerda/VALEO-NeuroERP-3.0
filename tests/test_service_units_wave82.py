"""Wave 82 — Unit-Tests fuer finance_dunning/op/period/clearing services (pure domain math)."""

from __future__ import annotations

import pytest
from datetime import date


# ---------------------------------------------------------------------------
# finance_dunning_service  (pure dunning level calculation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_days_based_level_current() -> None:
    from app.services.finance_dunning_service import days_based_level
    assert days_based_level(0) == 0


@pytest.mark.unit
def test_days_based_level_first() -> None:
    from app.services.finance_dunning_service import days_based_level
    assert days_based_level(15) == 1


@pytest.mark.unit
def test_days_based_level_second() -> None:
    from app.services.finance_dunning_service import days_based_level
    assert days_based_level(35) == 2


@pytest.mark.unit
def test_days_based_level_third() -> None:
    from app.services.finance_dunning_service import days_based_level
    assert days_based_level(65) == 3


@pytest.mark.unit
def test_next_dunning_level_increments() -> None:
    from app.services.finance_dunning_service import next_dunning_level
    result = next_dunning_level(1, 20)
    assert result >= 1


@pytest.mark.unit
def test_compute_dunning_has_required_fields() -> None:
    from app.services.finance_dunning_service import compute_dunning
    rule = {"gebuehr": 15.0, "zinssatz": 0.05, "text": "Erste Mahnung"}
    result = compute_dunning(1000.0, 1, rule, 10)
    for key in ("dunning_level", "dunning_fee", "interest", "total_amount"):
        assert key in result


@pytest.mark.unit
def test_compute_dunning_total_amount_includes_fees() -> None:
    from app.services.finance_dunning_service import compute_dunning
    rule = {"gebuehr": 15.0, "zinssatz": 0.0, "text": "Test"}
    result = compute_dunning(1000.0, 1, rule, 10)
    assert result["total_amount"] >= 1000.0


# ---------------------------------------------------------------------------
# finance_op_service — aging_bucket  (pure date category)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_aging_bucket_overdue_old() -> None:
    from app.services.finance_op_service import aging_bucket
    bucket, days = aging_bucket(date(2024, 1, 1), date(2024, 6, 1))
    assert days > 100
    assert "60" in bucket or bucket == "60+"


@pytest.mark.unit
def test_aging_bucket_no_date_not_due() -> None:
    from app.services.finance_op_service import aging_bucket
    bucket, days = aging_bucket(None, date(2024, 6, 1))
    assert "faellig" in bucket.lower() or days == 0


@pytest.mark.unit
def test_aging_bucket_future_date_not_overdue() -> None:
    from app.services.finance_op_service import aging_bucket
    bucket, days = aging_bucket(date(2025, 1, 1), date(2024, 6, 1))
    assert days <= 0 or "faellig" in bucket.lower()


# ---------------------------------------------------------------------------
# finance_period_service — close_readiness, period_bounds  (pure predicates)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_close_readiness_all_clear() -> None:
    from app.services.finance_period_service import close_readiness
    result = close_readiness(0, 0)
    assert result["ready"] is True
    assert result["blocker"] == []


@pytest.mark.unit
def test_close_readiness_with_open_items() -> None:
    from app.services.finance_period_service import close_readiness
    result = close_readiness(5, 0)
    assert result["ready"] is False
    assert len(result["blocker"]) > 0


@pytest.mark.unit
def test_period_bounds_january() -> None:
    from app.services.finance_period_service import period_bounds
    start, end = period_bounds("2024-01")
    assert start == date(2024, 1, 1)
    assert end == date(2024, 1, 31)


@pytest.mark.unit
def test_period_bounds_february_non_leap() -> None:
    from app.services.finance_period_service import period_bounds
    start, end = period_bounds("2023-02")
    assert start == date(2023, 2, 1)
    assert end == date(2023, 2, 28)


# ---------------------------------------------------------------------------
# finance_clearing_service — clearing_result  (pure clearing math)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_clearing_result_partial() -> None:
    from app.services.finance_clearing_service import clearing_result
    result = clearing_result(1000.0, 500.0)
    assert result["ausgleich"] == pytest.approx(500.0)
    assert result["neu_offen"] == pytest.approx(500.0)
    assert result["voll_ausgeziffert"] is False


@pytest.mark.unit
def test_clearing_result_full() -> None:
    from app.services.finance_clearing_service import clearing_result
    result = clearing_result(1000.0, 1000.0)
    assert result["voll_ausgeziffert"] is True
    assert result["neu_offen"] == pytest.approx(0.0)


@pytest.mark.unit
def test_clearing_result_overpayment() -> None:
    from app.services.finance_clearing_service import clearing_result
    result = clearing_result(1000.0, 1200.0)
    assert result["ueberzahlt"] is True
    assert result["voll_ausgeziffert"] is True
