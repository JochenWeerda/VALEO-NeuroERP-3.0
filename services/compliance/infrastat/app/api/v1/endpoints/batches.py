"""Batch-Management-Endpunkte."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session import get_session
from app.schemas.declaration import DeclarationBatch
from app.schemas.submission import SubmissionRequest, SubmissionResponse
from app.services.submission_service import SubmissionService
from app.dependencies import get_submission_service


router = APIRouter()


@router.get("/", response_model=List[DeclarationBatch])
async def list_batches(
    tenant_id: str,
    session: AsyncSession = Depends(get_session),
) -> List[DeclarationBatch]:
    stmt = (
        select(models.DeclarationBatch)
        .where(models.DeclarationBatch.tenant_id == tenant_id)
        .order_by(models.DeclarationBatch.reference_period.desc())
    )
    result = await session.execute(stmt)
    batches = result.scalars().unique().all()
    return [DeclarationBatch.model_validate(batch, from_attributes=True) for batch in batches]


@router.get("/{batch_id}", response_model=DeclarationBatch)
async def get_batch(
    batch_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> DeclarationBatch:
    batch = await session.get(models.DeclarationBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch nicht gefunden.")
    await session.refresh(batch)
    return DeclarationBatch.model_validate(batch, from_attributes=True)


@router.post("/{batch_id}/submit", response_model=SubmissionResponse)
async def submit_batch(
    batch_id: UUID,
    payload: SubmissionRequest,
    session: AsyncSession = Depends(get_session),
    submission_service: SubmissionService = Depends(get_submission_service),
) -> SubmissionResponse:
    batch = await session.get(models.DeclarationBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch nicht gefunden.")
    if batch.status not in {models.DeclarationStatus.READY, models.DeclarationStatus.VALIDATING}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch-Status {batch.status} erlaubt keine Übermittlung.",
        )

    response = await submission_service.submit(batch, payload)
    return response

