"""
Lead API endpoints
Full CRUD for lead management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ....core.database import get_db
from ....infrastructure.models import Lead as LeadModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.crm import Lead, LeadCreate, LeadUpdate

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Lead])
async def list_leads(
    tenant_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search in company, contact person"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return a paginated list of leads."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(LeadModel).filter(LeadModel.tenant_id == effective_tenant)
    
    if status:
        query = query.filter(LeadModel.status == status)
    
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                LeadModel.company_name.ilike(like),
                LeadModel.contact_person.ilike(like),
                LeadModel.email.ilike(like),
            )
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[Lead.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
    )


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single lead by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    lead = (
        db.query(LeadModel)
        .filter(
            LeadModel.id == lead_id,
            LeadModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return Lead.model_validate(lead)


@router.post("/", response_model=Lead, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a new lead."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    lead = LeadModel(
        **lead_data.model_dump(),
        tenant_id=effective_tenant
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return Lead.model_validate(lead)


@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update an existing lead."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    lead = (
        db.query(LeadModel)
        .filter(
            LeadModel.id == lead_id,
            LeadModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)
    
    db.commit()
    db.refresh(lead)
    
    return Lead.model_validate(lead)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a lead."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    lead = (
        db.query(LeadModel)
        .filter(
            LeadModel.id == lead_id,
            LeadModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    
    return None

