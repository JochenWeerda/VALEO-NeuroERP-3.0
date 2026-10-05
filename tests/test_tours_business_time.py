from __future__ import annotations

from datetime import date

import pytest

from app.api.v1.endpoints import tours


pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_today_tours_uses_configured_business_day(monkeypatch):
    local_day = date(2026, 10, 1)
    received: list[date] = []

    class _Repository:
        def __init__(self, db):
            assert db == "db"

        def get_by_date(self, value):
            received.append(value)
            return ["tour-local-day"]

    monkeypatch.setattr(tours, "TourRepository", _Repository)
    monkeypatch.setattr(tours, "business_today", lambda: local_day)

    result = await tours.get_today_tours(db="db")

    assert received == [local_day]
    assert result == ["tour-local-day"]
