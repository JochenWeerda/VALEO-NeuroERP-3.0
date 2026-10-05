from __future__ import annotations

from datetime import date

import pytest

from app.api.v1.endpoints import personal
from app.services import personal_service


pytestmark = pytest.mark.unit


def test_hr_date_fallbacks_use_configured_business_day(monkeypatch):
    local_day = date(2026, 10, 1)
    monkeypatch.setattr(personal, "business_today", lambda: local_day)
    monkeypatch.setattr(personal_service, "business_today", lambda: local_day)

    assert personal._to_iso(None) == "2026-10-01"
    assert personal_service.PersonalService._add_years(None, 1) == "2027-10-01"
    assert personal_service.PersonalService._add_years("ungueltig", 2) == "2028-10-01"


@pytest.mark.asyncio
async def test_driver_time_default_uses_configured_business_day(monkeypatch):
    local_day = date(2026, 10, 1)

    class _Service:
        def __init__(self, db, tenant_id):
            assert db == "db"
            assert tenant_id == "tenant-a"

        def get_driver_time_data(self, target_date):
            assert target_date == "2026-10-01"
            raise RuntimeError("force documented pilot fallback")

    monkeypatch.setattr(personal, "business_today", lambda: local_day)
    monkeypatch.setattr(personal, "PersonalService", _Service)

    result = await personal.get_driver_time_summary(datum=None, tenant_id="tenant-a", db="db")

    assert result.datum == "2026-10-01"
    assert result.source == "pilot-fallback"
