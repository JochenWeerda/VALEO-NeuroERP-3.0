"""Endpunkte für Sanktionslistenscreening."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.dependencies import get_screening_service
from app.schemas.screening import ScreeningRequest, ScreeningResponse
from app.services.screening_service import ScreeningService

router = APIRouter()


@router.post("/matches", response_model=ScreeningResponse, status_code=status.HTTP_200_OK)
async def screen_subject(
    payload: ScreeningRequest,
    service: ScreeningService = Depends(get_screening_service),
) -> ScreeningResponse:
    return await service.screen_subject(payload)
