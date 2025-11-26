from __future__ import annotations

import pytest

from app.schemas.preference import BomComponent, PreferenceCalculationRequest
from app.services.preference_service import PreferenceService


class FakeSession:
    def add(self, _):
        return None

    async def flush(self):
        return None


@pytest.mark.asyncio
async def test_preference_service_calculates_ratio():
    session = FakeSession()
    service = PreferenceService(session)  # type: ignore[arg-type]

    payload = PreferenceCalculationRequest(
        tenant_id="tenant-a",
        bill_of_materials_id="BOM-1",
        agreement_code="EU-CH",
        components=[
            BomComponent(component_id="1", origin="EU", value=60.0, originating=True),
            BomComponent(component_id="2", origin="CN", value=40.0, originating=False),
        ],
    )

    result = await service.calculate(payload)
    assert result.qualifies is True
    assert result.originating_value_percent == 60.0
