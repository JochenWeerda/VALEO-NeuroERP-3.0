"""Endpunkte für Präferenzkalkulationen."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.dependencies import get_preference_service
from app.schemas.preference import PreferenceCalculationRequest, PreferenceCalculationResponse
from app.services.preference_service import PreferenceService

router = APIRouter()


@router.post("/calculate", response_model=PreferenceCalculationResponse, status_code=status.HTTP_201_CREATED)
async def calculate_preference(
    payload: PreferenceCalculationRequest,
    service: PreferenceService = Depends(get_preference_service),
) -> PreferenceCalculationResponse:
    return await service.calculate(payload)
