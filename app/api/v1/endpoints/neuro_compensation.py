"""Compensation Engine — REST API (NC-006)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Optional

from app.services.compensation_engine import compensate, get_compensation_run

router = APIRouter(prefix="/neuro/compensate", tags=["neuro-core", "compensation"])


class CompensateRequest(BaseModel):
    error: str = Field(..., description="Fehlerbeschreibung")
    strategy: str = Field("retry_linear", description="retry_linear|retry_exponential|rollback|alternative_path|escalate")
    context: Optional[dict[str, Any]] = Field(default_factory=dict)
    rollback_steps: Optional[list[dict]] = Field(default_factory=list)


@router.post("")
async def do_compensate(request: CompensateRequest):
    run = await compensate(
        error_context={"error": request.error, **(request.context or {})},
        strategy=request.strategy,
        rollback_steps=request.rollback_steps,
    )
    return run.to_dict()


@router.get("/{run_id}")
async def get_run(run_id: str):
    run = get_compensation_run(run_id)
    if not run:
        raise HTTPException(404, "Compensation run not found")
    return run.to_dict()


@router.post("/{run_id}/retry")
async def manual_retry(run_id: str):
    run = get_compensation_run(run_id)
    if not run:
        raise HTTPException(404, "Compensation run not found")
    new_run = await compensate(
        error_context={"error": run.error, "previous_run": run_id},
        strategy="retry_linear",
    )
    return new_run.to_dict()
