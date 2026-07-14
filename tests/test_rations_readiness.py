from datetime import date, datetime, timezone

from app.agrar.rations.readiness import evaluate_material, summarize


DAY = date(2026, 7, 14)


def _row(**overrides):
    values = dict(feed_id="mais", name="Maissilage", daily_kg=1000.0,
        stock_kg=20_000.0, forage=True, analysis_id="a1", analysis_date=date(2026, 7, 1),
        selected_analysis_id="a1", price_eur_t=55.0, price_valid_from=date(2026, 1, 1),
        price_valid_to=date(2026, 12, 31), price_updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc), as_of=DAY)
    values.update(overrides)
    return evaluate_material(**values)


def test_ready_material_has_deterministic_reach() -> None:
    row = _row()
    assert row["status"] == "ready"
    assert row["reach_days"] == 20.0


def test_stock_below_three_days_blocks() -> None:
    row = _row(stock_kg=2500.0)
    assert row["status"] == "blocked"
    assert row["issues"][0]["code"] == "stock_critical"


def test_missing_analysis_and_expired_price_block() -> None:
    row = _row(analysis_id=None, analysis_date=None, price_valid_to=date(2026, 7, 13))
    assert {issue["code"] for issue in row["issues"]} == {"analysis_missing", "price_expired"}


def test_analysis_change_and_low_reach_warn() -> None:
    row = _row(stock_kg=10_000.0, selected_analysis_id="old")
    assert row["status"] == "warning"
    assert {issue["code"] for issue in row["issues"]} == {"stock_low", "analysis_changed"}


def test_summary_counts_findings_not_only_materials() -> None:
    summary = summarize([_row(stock_kg=1000.0, analysis_id=None, analysis_date=None), _row()], DAY)
    assert summary["status"] == "blocked"
    assert summary["blocker_count"] == 2

