"""Wave 95 — Unit-Tests fuer procurement_match_service, pos_accounting_service,
pos_tagesabschluss_service, scheduler_heartbeat (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# procurement_match_service — match_position, match_three_way_value, calculate_ers_credit
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_match_position_vollstaendig() -> None:
    from app.services.procurement_match_service import match_position
    result = match_position(Decimal("100"), Decimal("100"), toleranz_pct=Decimal("2"))
    assert result["status"] == "vollstaendig"
    assert result["abweichung"] is False


@pytest.mark.unit
def test_match_position_teilgeliefert() -> None:
    from app.services.procurement_match_service import match_position
    result = match_position(Decimal("100"), Decimal("80"), toleranz_pct=Decimal("2"))
    assert result["status"] == "teilgeliefert"
    assert result["offen"] == pytest.approx(20.0)


@pytest.mark.unit
def test_match_position_toleranz_accepted_as_vollstaendig() -> None:
    from app.services.procurement_match_service import match_position
    # 99 delivered vs 100 ordered = 1% deviation within 2% tolerance
    result = match_position(Decimal("100"), Decimal("99"), toleranz_pct=Decimal("2"))
    assert result["abweichung_pct"] == pytest.approx(-1.0)


@pytest.mark.unit
def test_match_position_result_has_required_keys() -> None:
    from app.services.procurement_match_service import match_position
    result = match_position(Decimal("50"), Decimal("50"), toleranz_pct=Decimal("0"))
    for key in ("bestellt", "geliefert", "offen", "status", "abweichung"):
        assert key in result


@pytest.mark.unit
def test_match_three_way_value_abgeglichen() -> None:
    from app.services.procurement_match_service import match_three_way_value
    result = match_three_way_value(Decimal("1000"), Decimal("1000"), toleranz_pct=Decimal("1"))
    assert result["status"] == "abgeglichen"
    assert result["abweichung"] is False


@pytest.mark.unit
def test_match_three_way_value_wertabweichung() -> None:
    from app.services.procurement_match_service import match_three_way_value
    result = match_three_way_value(Decimal("1000"), Decimal("900"), toleranz_pct=Decimal("1"))
    assert result["abweichung"] is True
    assert result["differenz"] == pytest.approx(-100.0)


@pytest.mark.unit
def test_calculate_ers_credit_abgeglichen_not_berechtigt() -> None:
    from app.services.procurement_match_service import calculate_ers_credit
    positionen = [{"menge": Decimal("10"), "einheitspreis": Decimal("200"), "mwst_satz": Decimal("7")}]
    three_way = {"status": "abgeglichen", "abweichung": False}
    result = calculate_ers_credit(positionen, three_way)
    assert result["berechtigt"] is False


# ---------------------------------------------------------------------------
# pos_accounting_service — build_pos_closing_lines  (pure accounting mapping)
# ---------------------------------------------------------------------------

def _make_amounts(**kwargs):
    from app.services.pos_accounting_service import PosClosingAmounts
    defaults = {f: Decimal("0") for f in ["cash_sales", "card_sales", "paypal_sales", "b2b_sales",
                                           "voucher_redemptions", "voucher_issues", "cash_withdrawals",
                                           "cash_difference"]}
    defaults.update({k: Decimal(str(v)) for k, v in kwargs.items()})
    return PosClosingAmounts(**defaults)


@pytest.mark.unit
def test_build_pos_closing_lines_with_cash_sales() -> None:
    from app.services.pos_accounting_service import build_pos_closing_lines
    amounts = _make_amounts(cash_sales=Decimal("1000"))
    lines = build_pos_closing_lines(amounts)
    assert len(lines) > 0


@pytest.mark.unit
def test_build_pos_closing_lines_zero_amounts_no_lines() -> None:
    from app.services.pos_accounting_service import build_pos_closing_lines
    amounts = _make_amounts()
    lines = build_pos_closing_lines(amounts)
    assert lines == []


@pytest.mark.unit
def test_build_pos_closing_lines_returns_list() -> None:
    from app.services.pos_accounting_service import build_pos_closing_lines
    amounts = _make_amounts(card_sales=Decimal("500"))
    lines = build_pos_closing_lines(amounts)
    assert isinstance(lines, list)


@pytest.mark.unit
def test_build_pos_closing_lines_line_has_account_number() -> None:
    from app.services.pos_accounting_service import build_pos_closing_lines
    amounts = _make_amounts(cash_sales=Decimal("1000"))
    lines = build_pos_closing_lines(amounts)
    for line in lines:
        assert hasattr(line, "account_number")
        assert len(line.account_number) > 0


# ---------------------------------------------------------------------------
# pos_tagesabschluss_service — simulate_tse_signatur  (pure simulation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_simulate_tse_signatur_returns_dict() -> None:
    from app.services.pos_tagesabschluss_service import simulate_tse_signatur
    result = simulate_tse_signatur("KASSE-001", 42, 15000.0)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_simulate_tse_signatur_has_required_keys() -> None:
    from app.services.pos_tagesabschluss_service import simulate_tse_signatur
    result = simulate_tse_signatur("KASSE-001", 1, 0.0)
    for key in ("tse_serial", "tse_signatur", "tse_zeitpunkt"):
        assert key in result


@pytest.mark.unit
def test_simulate_tse_signatur_serial_starts_with_prefix() -> None:
    from app.services.pos_tagesabschluss_service import simulate_tse_signatur
    result = simulate_tse_signatur("KASSE-007", 1, 0.0)
    # Serial contains simulation prefix
    assert result["tse_serial"].startswith("SIM-")


# ---------------------------------------------------------------------------
# scheduler_heartbeat — evaluate_scheduler_heartbeats  (pure health check)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_scheduler_heartbeats_active_worker() -> None:
    from app.core.scheduler_heartbeat import evaluate_scheduler_heartbeats, WorkerHeartbeat, SchedulerNodeStatus
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    hb = WorkerHeartbeat(
        scheduler_id="SCH-001", worker_id="W1", worker_klasse="CronWorker",
        heartbeat_at=now - timedelta(seconds=5),
        lease_until=now + timedelta(seconds=55),
    )
    result = evaluate_scheduler_heartbeats([hb], scheduler_id="SCH-001", evaluated_at=now)
    assert result.status == SchedulerNodeStatus.ACTIVE


@pytest.mark.unit
def test_evaluate_scheduler_heartbeats_no_workers_no_heartbeats() -> None:
    from app.core.scheduler_heartbeat import evaluate_scheduler_heartbeats
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    result = evaluate_scheduler_heartbeats([], scheduler_id="SCH-001", evaluated_at=now)
    assert result is not None
    assert result.scheduler_id == "SCH-001"


@pytest.mark.unit
def test_evaluate_scheduler_heartbeats_result_has_schema_version() -> None:
    from app.core.scheduler_heartbeat import evaluate_scheduler_heartbeats
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    result = evaluate_scheduler_heartbeats([], scheduler_id="SCH-001", evaluated_at=now)
    assert result.schema_version is not None
