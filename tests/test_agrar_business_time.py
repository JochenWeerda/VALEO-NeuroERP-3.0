from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.schemas.agrar import (
    DuengerCreate,
    DuengerUpdate,
    PSMCreate,
    PSMUpdate,
    SaatgutCreate,
    SaatgutUpdate,
)
from app.domains.agrar.api import duenger, psm, saatgut


class _Query:
    def __init__(self, first_result=None, captured_filters=None):
        self._first_result = first_result
        self._captured_filters = captured_filters

    def filter(self, *conditions):
        if self._captured_filters is not None:
            self._captured_filters.extend(conditions)
        return self

    def group_by(self, *_args):
        return self

    def first(self):
        return self._first_result

    def all(self):
        return []

    def count(self):
        return 0


class _CreateDb:
    def query(self, *_args):
        return _Query()


class _UpdateDb:
    def query(self, *_args):
        return _Query(SimpleNamespace())


def _expiry(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("module", "endpoint", "payload"),
    [
        (
            psm,
            psm.create_psm,
            PSMCreate(
                tenant_id="tenant-1",
                artikelnummer="PSM-1",
                name="PSM",
                wirkstoff="Wirkstoff",
                mittel_typ="Herbizid",
                bvl_nummer="BVL-1",
                zulassung_ablauf=_expiry("2099-01-01T23:59:59"),
            ),
        ),
        (
            saatgut,
            saatgut.create_saatgut,
            SaatgutCreate(
                artikelnummer="SAAT-1",
                name="Saatgut",
                sorte="Sorte",
                art="Weizen",
                ablauf_zulassung=_expiry("2099-01-01T23:59:59"),
            ),
        ),
        (
            duenger,
            duenger.create_duenger,
            DuengerCreate(
                artikelnummer="DUE-1",
                name="Duenger",
                typ="Mineralisch",
                ablauf_zulassung=_expiry("2099-01-01T23:59:59"),
            ),
        ),
    ],
)
def test_create_rejects_expiry_before_configured_business_day(
    monkeypatch: pytest.MonkeyPatch, module, endpoint, payload
) -> None:
    monkeypatch.setattr(module, "business_today", lambda: date(2099, 1, 2))

    with pytest.raises(HTTPException, match="Approval expiry date cannot be in the past"):
        asyncio.run(endpoint(payload, tenant_id="tenant-1", db=_CreateDb()))


@pytest.mark.parametrize(
    ("module", "endpoint", "payload"),
    [
        (psm, psm.update_psm, PSMUpdate(zulassung_ablauf=_expiry("2099-01-01T23:59:59"))),
        (
            saatgut,
            saatgut.update_saatgut,
            SaatgutUpdate(ablauf_zulassung=_expiry("2099-01-01T23:59:59")),
        ),
        (
            duenger,
            duenger.update_duenger,
            DuengerUpdate(ablauf_zulassung=_expiry("2099-01-01T23:59:59")),
        ),
    ],
)
def test_update_rejects_expiry_before_configured_business_day(
    monkeypatch: pytest.MonkeyPatch, module, endpoint, payload
) -> None:
    monkeypatch.setattr(module, "business_today", lambda: date(2099, 1, 2))

    with pytest.raises(HTTPException, match="Approval expiry date cannot be in the past"):
        asyncio.run(endpoint("record-1", payload, tenant_id="tenant-1", db=_UpdateDb()))


def test_psm_warning_window_uses_one_consistent_business_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def configured_day() -> date:
        nonlocal calls
        calls += 1
        return date(2099, 1, 2)

    captured_filters = []

    class StatsDb:
        def query(self, *_args):
            return _Query(first_result=(None, None), captured_filters=captured_filters)

    monkeypatch.setattr(psm, "business_today", configured_day)
    result = asyncio.run(psm.get_psm_stats(tenant_id="tenant-1", db=StatsDb()))

    bound_dates = {
        condition.right.value
        for condition in captured_filters
        if hasattr(condition, "right") and isinstance(getattr(condition.right, "value", None), date)
    }
    assert calls == 1
    assert {date(2099, 1, 2), date(2099, 4, 2)} <= bound_dates
    assert result["approval_warnings"] == {"expiring_soon": 0, "already_expired": 0}
