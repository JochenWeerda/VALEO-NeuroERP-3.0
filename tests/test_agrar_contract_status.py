from decimal import Decimal

from app.services.agrar_contract_service import _compute_status


def test_compute_status_open_when_no_allocation():
    status = _compute_status(Decimal("100.000"), Decimal("100.000"), "open")
    assert status == "open"


def test_compute_status_partial_when_remaining_less_than_total():
    status = _compute_status(Decimal("100.000"), Decimal("40.000"), "open")
    assert status == "partially_allocated"


def test_compute_status_fulfilled_when_remaining_zero():
    status = _compute_status(Decimal("100.000"), Decimal("0.000"), "open")
    assert status == "fulfilled"


def test_compute_status_cancelled_is_stable():
    status = _compute_status(Decimal("100.000"), Decimal("60.000"), "cancelled")
    assert status == "cancelled"

