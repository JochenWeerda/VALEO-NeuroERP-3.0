"""
CRM Lead management endpoints
RESTful API for lead management with clean architecture
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import LeadRepository
from ....core.dependency_container import container
from ..schemas.crm import (
    LeadCreate, LeadUpdate, Lead
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=Lead, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lead.

    This endpoint allows creating a new sales lead in the CRM system.
    """
    try:
        lead_repo = container.resolve(LeadRepository)
        lead = await lead_repo.create(lead_data.model_dump(), lead_data.tenant_id)
        return Lead.model_validate(lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Lead])
async def list_leads(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List leads with pagination and filtering.

    Retrieve a paginated list of leads with optional filtering.
    """
    try:
        lead_repo = container.resolve(LeadRepository)

        # Use provided tenant_id or default to system for now
        effective_tenant_id = tenant_id or "system"

        leads = await lead_repo.get_all(effective_tenant_id, skip, limit, status, assigned_to)
        total = await lead_repo.count(effective_tenant_id, status, assigned_to)

        return PaginatedResponse[Lead](
            items=[Lead.model_validate(lead) for lead in leads],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list leads: {str(e)}")


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: str,
    db: Session = Depends(get_db)
):
    """
    Get lead by ID.

    Retrieve detailed information about a specific lead.
    """
    try:
        lead_repo = container.resolve(LeadRepository)
        lead = await lead_repo.get_by_id(lead_id, "system")  # TODO: tenant context
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return Lead.model_validate(lead)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lead: {str(e)}")


@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db)
):
    """
    Update lead information.

    Modify lead details such as status, priority, or assignment.
    """
    try:
        lead_repo = container.resolve(LeadRepository)
        lead = await lead_repo.update(lead_id, lead_data.model_dump(exclude_unset=True), "system")  # TODO: tenant context
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return Lead.model_validate(lead)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lead: {str(e)}")


@router.post("/{lead_id}/convert", response_model=dict)
async def convert_lead(
    lead_id: str,
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Convert lead to customer.

    Convert a qualified lead into a customer record.
    """
    try:
        lead_repo = container.resolve(LeadRepository)
        success = await lead_repo.convert_to_customer(lead_id, customer_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=400, detail="Failed to convert lead")
        return {"message": "Lead converted successfully", "customer_id": customer_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert lead: {str(e)}")


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete lead (soft delete).

    Mark a lead as inactive. This is a soft delete operation.
    """
    try:
        lead_repo = container.resolve(LeadRepository)
        success = await lead_repo.delete(lead_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete lead: {str(e)}")