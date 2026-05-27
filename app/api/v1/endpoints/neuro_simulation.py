"""Neuro Simulation Engine — REST API (NC-005)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Optional

from app.core.tenant import get_tenant_id
from app.services.neuro_simulation_engine import simulate_dry_run, simulate_what_if, get_simulation_result

router = APIRouter(prefix="/neuro/simulate", tags=["neuro-core", "simulation"])


class SimulateRequest(BaseModel):
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    current_state: Optional[str] = None
    target_state: Optional[str] = None
    amount: Optional[float] = None
    params: Optional[dict[str, Any]] = Field(default_factory=dict)


class WhatIfRequest(SimulateRequest):
    current_data: dict[str, Any] = Field(default_factory=dict)


@router.post("/dry-run", summary="Run dry",
    response_model=dict
)
async def dry_run(request: SimulateRequest, tenant_id: str = Depends(get_tenant_id)):
    result = simulate_dry_run(request.model_dump(exclude_none=True), tenant_id)
    return result.to_dict()


@router.post("", summary="If what",
    response_model=dict
)
async def what_if(request: WhatIfRequest, tenant_id: str = Depends(get_tenant_id)):
    result = simulate_what_if(request.model_dump(exclude_none=True), request.current_data, tenant_id)
    return result.to_dict()


@router.get("/{run_id}", summary="Result abrufen",
    response_model=dict
)
async def get_result(run_id: str):
    result = get_simulation_result(run_id)
    if not result:
        raise HTTPException(404, "Simulation result not found")
    return result.to_dict()
