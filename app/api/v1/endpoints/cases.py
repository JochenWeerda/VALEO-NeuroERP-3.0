"""CRM Service Cases API endpoints proxied through crm-service."""

from __future__ import annotations

from math import ceil
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ....core.config import settings
from ....integrations.crm_core_client import (
    create_case as crm_create_case,
    delete_case as crm_delete_case,
    escalate_case as crm_escalate_case,
    get_case as crm_get_case,
    list_cases as crm_list_cases,
    update_case as crm_update_case,
)
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Case, CaseCreate, CaseUpdate

router = APIRouter()


@router.post("/", response_model=Case, status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreate):
    """Create a new support case via crm-service."""
    try:
        created = await crm_create_case(case_data.model_dump())
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create case: {exc}") from exc
    return Case.model_validate(created)


@router.get("/", response_model=PaginatedResponse[Case])
async def list_cases(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
):
    """List support cases from crm-service with pagination."""
    try:
        cases, total = await crm_list_cases(
            tenant_id=tenant_id,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            customer_id=customer_id,
            skip=skip,
            limit=limit
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list cases: {exc}") from exc

    pages = ceil(total / limit) if total else 1
    return PaginatedResponse[Case](
        items=[Case.model_validate(case) for case in cases],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{case_id}", response_model=Case)
async def get_case(case_id: str):
    """Get a specific support case by ID."""
    try:
        case = await crm_get_case(case_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Case not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve case: {exc}") from exc
    return Case.model_validate(case)


@router.put("/{case_id}", response_model=Case)
async def update_case(case_id: str, case_data: CaseUpdate):
    """Update a support case via crm-service."""
    try:
        updated = await crm_update_case(case_id, case_data.model_dump(exclude_unset=True))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Case not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update case: {exc}") from exc
    return Case.model_validate(updated)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: str):
    """Delete a support case via crm-service."""
    try:
        await crm_delete_case(case_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Case not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete case: {exc}") from exc


@router.post("/{case_id}/escalate", response_model=dict)
async def escalate_case(
    case_id: str,
    reason: str = Query(..., description="Reason for escalation"),
    escalated_by: str = Query(..., description="User performing escalation"),
):
    """Escalate a support case via crm-service."""
    try:
        result = await crm_escalate_case(case_id, reason, escalated_by)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Case not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to escalate case: {exc}") from exc
    return result