"""Service für Exportgenehmigungen."""

from __future__ import annotations

from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.schemas.permits import ExportPermitCreate, ExportPermitRead, ExportPermitUpdate


class PermitService:
    """Kapselt CRUD für Exportgenehmigungen."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_permit(self, payload: ExportPermitCreate) -> ExportPermitRead:
        permit = models.ExportPermit(
            tenant_id=payload.tenant_id,
            permit_number=payload.permit_number,
            country_destination=payload.country_destination,
            validity_start=payload.validity_start,
            validity_end=payload.validity_end,
            goods_description=payload.goods_description,
            control_list_entries=payload.control_list_entries,
            metadata=payload.metadata,
        )
        self._session.add(permit)
        await self._session.flush()
        return await self._to_schema(permit)

    async def list_permits(self, tenant_id: str) -> List[ExportPermitRead]:
        result = await self._session.execute(
            select(models.ExportPermit).where(models.ExportPermit.tenant_id == tenant_id)
        )
        permits = result.scalars().all()
        return [await self._to_schema(permit) for permit in permits]

    async def update_permit(self, permit_id: UUID, payload: ExportPermitUpdate) -> ExportPermitRead:
        permit = await self._session.get(models.ExportPermit, permit_id)
        if not permit:
            raise KeyError(f"Permit {permit_id} nicht gefunden.")

        if payload.status:
            permit.status = models.ExportPermitStatus(payload.status)
        if payload.validity_end:
            permit.validity_end = payload.validity_end
        if payload.metadata:
            permit.metadata.update(payload.metadata)
        await self._session.flush()
        return await self._to_schema(permit)

    async def _to_schema(self, permit: models.ExportPermit) -> ExportPermitRead:
        return ExportPermitRead(
            id=permit.id,
            tenant_id=permit.tenant_id,
            permit_number=permit.permit_number,
            country_destination=permit.country_destination,
            validity_start=permit.validity_start,
            validity_end=permit.validity_end,
            goods_description=permit.goods_description,
            control_list_entries=permit.control_list_entries,
            metadata=permit.metadata,
            status=permit.status.value,
        )
