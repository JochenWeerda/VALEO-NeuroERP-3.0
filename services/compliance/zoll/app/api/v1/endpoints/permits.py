"""Endpunkte für Exportgenehmigungen."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_permit_service
from app.schemas.permits import ExportPermitCreate, ExportPermitRead, ExportPermitUpdate
from app.services.permit_service import PermitService

router = APIRouter()


@router.post("/", response_model=ExportPermitRead, status_code=status.HTTP_201_CREATED)
async def create_permit(
    payload: ExportPermitCreate,
    service: PermitService = Depends(get_permit_service),
) -> ExportPermitRead:
    return await service.create_permit(payload)


@router.get("/", response_model=List[ExportPermitRead])
async def list_permits(
    tenant_id: str,
    service: PermitService = Depends(get_permit_service),
) -> List[ExportPermitRead]:
    return await service.list_permits(tenant_id)


@router.patch("/{permit_id}", response_model=ExportPermitRead)
async def update_permit(
    permit_id: UUID,
    payload: ExportPermitUpdate,
    service: PermitService = Depends(get_permit_service),
) -> ExportPermitRead:
    try:
        return await service.update_permit(permit_id, payload)
    except KeyError as exc:  # noqa: PERF203
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
