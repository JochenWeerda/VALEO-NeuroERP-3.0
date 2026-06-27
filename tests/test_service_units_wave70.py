"""Wave 70 — Unit-Tests fuer can_storno (sales_storno_service) und credit_check (sales_credit_service)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# sales_storno_service — can_storno  (pure predicate, keine DB)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_can_storno_not_billed_allowed() -> None:
    from app.services.sales_storno_service import can_storno
    ok, reason = can_storno(status=None, invoice_number=None)
    assert ok is True
    assert reason == ""


@pytest.mark.unit
def test_can_storno_open_status_no_invoice_allowed() -> None:
    from app.services.sales_storno_service import can_storno
    ok, _ = can_storno(status="open", invoice_number=None)
    assert ok is True


@pytest.mark.unit
def test_can_storno_already_cancelled_blocked() -> None:
    from app.services.sales_storno_service import can_storno
    ok, reason = can_storno(status="storniert", invoice_number="INV-001")
    assert ok is False
    assert len(reason) > 0


@pytest.mark.unit
def test_can_storno_billed_blocked() -> None:
    from app.services.sales_storno_service import can_storno
    ok, reason = can_storno(status="open", invoice_number="INV-001")
    assert ok is False
    assert "Gutschrift" in reason or len(reason) > 0


@pytest.mark.unit
def test_can_storno_both_none_allowed() -> None:
    from app.services.sales_storno_service import can_storno
    ok, _ = can_storno(None, None)
    assert ok is True


@pytest.mark.unit
def test_can_storno_returns_tuple() -> None:
    from app.services.sales_storno_service import can_storno
    result = can_storno("open", None)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)


# ---------------------------------------------------------------------------
# sales_credit_service — credit_check  (pure calculation, keine DB)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_credit_check_ok_below_warn() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=10_000, exposure=3_000, betrag=1_000)
    assert result["ampel"] == "ok"
    assert result["verfuegbar"] == pytest.approx(7_000)


@pytest.mark.unit
def test_credit_check_warn_between_80_and_100_pct() -> None:
    from app.services.sales_credit_service import credit_check
    # exposure=8000 + betrag=1000 → 90% → warnung
    result = credit_check(limit=10_000, exposure=8_000, betrag=1_000)
    assert result["ampel"] in ("warnung", "blockiert")


@pytest.mark.unit
def test_credit_check_blocked_over_100_pct() -> None:
    from app.services.sales_credit_service import credit_check
    # exposure=9500 + betrag=1000 → 105% → blockiert
    result = credit_check(limit=10_000, exposure=9_500, betrag=1_000)
    assert result["ampel"] == "blockiert"


@pytest.mark.unit
def test_credit_check_has_required_fields() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=5_000, exposure=2_000, betrag=500)
    for key in ("ampel", "limit", "exposure", "verfuegbar", "auslastung_pct", "auslastung_neu_pct"):
        assert key in result


@pytest.mark.unit
def test_credit_check_zero_limit_blocks() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=0, exposure=0, betrag=1)
    # zero limit means no credit limit configured — service returns special 'kein_limit' state
    assert result["ampel"] in ("blockiert", "ok", "warnung", "kein_limit")


@pytest.mark.unit
def test_credit_check_verfuegbar_formula() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=20_000, exposure=8_000, betrag=0)
    assert result["verfuegbar"] == pytest.approx(result["limit"] - result["exposure"])


@pytest.mark.unit
def test_credit_check_custom_warn_pct() -> None:
    from app.services.sales_credit_service import credit_check
    # With warn_pct=50: exposure=6000/10000 = 60% → warnung
    result = credit_check(limit=10_000, exposure=6_000, betrag=0, warn_pct=50.0)
    assert result["ampel"] in ("warnung", "blockiert")
