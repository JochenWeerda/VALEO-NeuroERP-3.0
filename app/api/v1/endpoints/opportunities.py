"""CRM Sales Opportunities API endpoints proxied through crm-sales."""

from __future__ import annotations

from math import ceil
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ....core.config import settings
from ....integrations.crm_core_client import (
    create_opportunity as crm_create_opportunity,
    delete_opportunity as crm_delete_opportunity,
    get_opportunity as crm_get_opportunity,
    list_opportunities as crm_list_opportunities,
    update_opportunity as crm_update_opportunity,
)
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Opportunity, OpportunityCreate, OpportunityUpdate

router = APIRouter()


@router.post("/", response_model=Opportunity, status_code=status.HTTP_201_CREATED)
async def create_opportunity(opportunity_data: OpportunityCreate):
    """Create a new sales opportunity via crm-sales."""
    try:
        created = await crm_create_opportunity(opportunity_data.model_dump())
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create opportunity: {exc}") from exc
    return Opportunity.model_validate(created)


@router.get("/", response_model=PaginatedResponse[Opportunity])
async def list_opportunities(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
):
    """List sales opportunities from crm-sales with pagination."""
    try:
        opportunities, total = await crm_list_opportunities(
            tenant_id=tenant_id,
            status=status,
            assigned_to=assigned_to,
            skip=skip,
            limit=limit
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list opportunities: {exc}") from exc

    pages = ceil(total / limit) if total else 1
    return PaginatedResponse[Opportunity](
        items=[Opportunity.model_validate(opportunity) for opportunity in opportunities],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{opportunity_id}", response_model=Opportunity)
async def get_opportunity(opportunity_id: str):
    """Get a specific sales opportunity by ID."""
    try:
        opportunity = await crm_get_opportunity(opportunity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Opportunity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve opportunity: {exc}") from exc
    return Opportunity.model_validate(opportunity)


@router.put("/{opportunity_id}", response_model=Opportunity)
async def update_opportunity(opportunity_id: str, opportunity_data: OpportunityUpdate):
    """Update a sales opportunity via crm-sales."""
    try:
        updated = await crm_update_opportunity(opportunity_id, opportunity_data.model_dump(exclude_unset=True))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Opportunity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update opportunity: {exc}") from exc
    return Opportunity.model_validate(updated)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(opportunity_id: str):
    """Delete a sales opportunity via crm-sales."""
    try:
        await crm_delete_opportunity(opportunity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Opportunity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete opportunity: {exc}") from exc