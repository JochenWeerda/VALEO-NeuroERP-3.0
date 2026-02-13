from decimal import Decimal

from scripts.backfill_agrar_mig01 import normalize_silo_number, sanitize_weights


def test_normalize_silo_number_sanitizes_and_caps_length():
    value = normalize_silo_number("  silo 12/ost +++ ")
    assert value == "SILO-12-OST"

    long_value = normalize_silo_number("x" * 100)
    assert len(long_value) == 50
    assert long_value == "X" * 50


def test_normalize_silo_number_uses_fallback_for_empty_input():
    assert normalize_silo_number("") == "LEGACY-DEFAULT"
    assert normalize_silo_number(None) == "LEGACY-DEFAULT"


def test_sanitize_weights_corrects_invalid_net_and_tare():
    gross, tare, net, corrected = sanitize_weights(10, 12, -5)
    assert gross == Decimal("10.000")
    assert tare == Decimal("10.000")
    assert net == Decimal("0.000")
    assert corrected is True


def test_sanitize_weights_keeps_valid_values():
    gross, tare, net, corrected = sanitize_weights(12.3456, 2.1111, 10.2345)
    assert gross == Decimal("12.346")
    assert tare == Decimal("2.111")
    assert net == Decimal("10.235")
    assert corrected is False
