"""Geschaeftstag-Vertrag: Buchungsdatum folgt der Ortszeit, nicht UTC."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.business_time import (
    DEFAULT_BUSINESS_TIMEZONE,
    business_date_at,
    business_now,
    business_timezone,
    business_today,
)

pytestmark = pytest.mark.unit


def test_default_timezone_is_berlin(monkeypatch):
    monkeypatch.delenv("BUSINESS_TIMEZONE", raising=False)
    assert str(business_timezone()) == DEFAULT_BUSINESS_TIMEZONE


def test_summer_time_shifts_late_evening_utc_to_next_day(monkeypatch):
    """22:30 UTC ist in MESZ (UTC+2) schon der Folgetag."""
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    instant = datetime(2026, 9, 11, 22, 30, tzinfo=timezone.utc)
    assert business_date_at(instant).isoformat() == "2026-09-12"


def test_winter_time_shifts_late_evening_utc_to_next_day(monkeypatch):
    """23:30 UTC ist in MEZ (UTC+1) schon der Folgetag."""
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    instant = datetime(2026, 1, 11, 23, 30, tzinfo=timezone.utc)
    assert business_date_at(instant).isoformat() == "2026-01-12"


def test_month_boundary_stays_in_the_local_period(monkeypatch):
    """Der Fall, der die Periode verschob: 31.08. 22:30 UTC ist lokal der 01.09."""
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    instant = datetime(2026, 8, 31, 22, 30, tzinfo=timezone.utc)
    business_day = business_date_at(instant)
    assert business_day.isoformat() == "2026-09-01"
    assert business_day.strftime("%Y-%m") == "2026-09"
    assert instant.date().strftime("%Y-%m") == "2026-08"


def test_midday_is_the_same_day_in_both_zones(monkeypatch):
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    instant = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    assert business_date_at(instant) == instant.date()


def test_naive_input_is_read_as_utc(monkeypatch):
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    naive = datetime(2026, 9, 11, 22, 30)
    aware = naive.replace(tzinfo=timezone.utc)
    assert business_date_at(naive) == business_date_at(aware)


def test_utc_configuration_matches_utc_date(monkeypatch):
    monkeypatch.setenv("BUSINESS_TIMEZONE", "UTC")
    instant = datetime(2026, 9, 11, 22, 30, tzinfo=timezone.utc)
    assert business_date_at(instant) == instant.date()


def test_unknown_timezone_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Mars/Olympus_Mons")
    assert str(business_timezone()) == DEFAULT_BUSINESS_TIMEZONE


def test_business_now_is_aware_and_consistent_with_today(monkeypatch):
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    now = business_now()
    assert now.tzinfo is not None
    assert now.utcoffset() in (timedelta(hours=1), timedelta(hours=2))
    assert business_today() == now.date()
