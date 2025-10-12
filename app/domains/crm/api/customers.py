"""
Customer API endpoints
Full CRUD for customer management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ....core.database import get_db
from ....infrastructure.models import Customer as CustomerModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.crm import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in name, email, phone"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of customers."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(CustomerModel).filter(CustomerModel.tenant_id == effective_tenant)
    
    if is_active is not None:
        query = query.filter(CustomerModel.is_active == is_active)
    
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                CustomerModel.name.ilike(like),
                CustomerModel.email.ilike(like),
                CustomerModel.phone.ilike(like),
                CustomerModel.customer_number.ilike(like),
            )
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[Customer.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
    )


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single customer by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    customer = (
        db.query(CustomerModel)
        .filter(
            CustomerModel.id == customer_id,
            CustomerModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return Customer.model_validate(customer)


@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer_data: CustomerCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a new customer."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    # Check if customer_number already exists
    existing = (
        db.query(CustomerModel)
        .filter(
            CustomerModel.customer_number == customer_data.customer_number,
            CustomerModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Customer number {customer_data.customer_number} already exists"
        )
    
    customer = CustomerModel(
        **customer_data.model_dump(),
        tenant_id=effective_tenant
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return Customer.model_validate(customer)


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update an existing customer."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    customer = (
        db.query(CustomerModel)
        .filter(
            CustomerModel.id == customer_id,
            CustomerModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
    
    db.commit()
    db.refresh(customer)
    
    return Customer.model_validate(customer)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a customer (soft delete - set is_active=False)."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    customer = (
        db.query(CustomerModel)
        .filter(
            CustomerModel.id == customer_id,
            CustomerModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_active = False
    db.commit()
    
    return None

