from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from app.db import models
from app.schemas.permits import ExportPermitCreate, ExportPermitUpdate
from app.services.permit_service import PermitService


class FakeSession:
    def __init__(self):
        self.objects = {}

    def add(self, obj):
        self.objects[obj.id] = obj

    def add_all(self, objs):
        for obj in objs:
            self.add(obj)

    async def flush(self):
        return None

    async def get(self, model, pk):
        return self.objects.get(pk)

    async def execute(self, _):
        class Result:
            def __init__(self, values):
                self._values = values

            def scalars(self):
                return self

            def all(self):
                return list(self._values)

        return Result(self.objects.values())


@pytest.mark.asyncio
async def test_permit_service_create_and_update():
    session = FakeSession()
    service = PermitService(session)  # type: ignore[arg-type]

    create_payload = ExportPermitCreate(
        tenant_id="tenant-a",
        permit_number="P-1",
        country_destination="US",
        validity_start=date(2025, 1, 1),
        validity_end=date(2025, 12, 31),
        goods_description="Test",
        control_list_entries=["5A002"],
        metadata={},
    )

    created = await service.create_permit(create_payload)
    assert created.permit_number == "P-1"

    update_payload = ExportPermitUpdate(status="approved")
    updated = await service.update_permit(created.id, update_payload)
    assert updated.status == "approved"
