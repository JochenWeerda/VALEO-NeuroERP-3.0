"""
CRM Customer management endpoints
RESTful API for customer management with clean architecture
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import CustomerRepository
from ....core.dependency_container import container
from ..schemas.crm import (
    CustomerCreate, CustomerUpdate, Customer
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer.

    This endpoint allows creating a new customer in the CRM system.
    The customer will be associated with a specific tenant.
    """
    try:
        customer_repo = container.resolve(CustomerRepository)

        # Check if customer number already exists
        existing = await customer_repo.get_by_customer_number(customer_data.customer_number, customer_data.tenant_id)
        if existing:
            raise HTTPException(status_code=400, detail="Customer number already exists")

        customer = await customer_repo.create(customer_data.model_dump(), customer_data.tenant_id)
        return Customer.model_validate(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search in company name or contact person"),
    db: Session = Depends(get_db)
):
    """
    List customers with pagination and filtering.

    Retrieve a paginated list of customers with optional filtering by tenant and search.
    """
    try:
        customer_repo = container.resolve(CustomerRepository)

        # Use provided tenant_id or default to system for now
        # TODO: Get tenant from authenticated user context
        effective_tenant_id = tenant_id or "system"

        customers = await customer_repo.get_all(effective_tenant_id, skip, limit, search)
        total = await customer_repo.count(effective_tenant_id, search)

        return PaginatedResponse[Customer](
            items=[Customer.model_validate(customer) for customer in customers],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list customers: {str(e)}")


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get customer by ID.

    Retrieve detailed information about a specific customer.
    """
    try:
        customer_repo = container.resolve(CustomerRepository)
        # TODO: Add tenant context from authentication
        customer = await customer_repo.get_by_id(customer_id, "system")  # Temporary
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return Customer.model_validate(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve customer: {str(e)}")


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update customer information.

    Modify customer details such as contact information, address, or status.
    """
    try:
        customer_repo = container.resolve(CustomerRepository)

        # Check for customer number conflicts if being updated
        if customer_data.customer_number:
            existing = await customer_repo.get_by_customer_number(customer_data.customer_number, "system")  # TODO: tenant context
            if existing and existing.id != customer_id:
                raise HTTPException(status_code=400, detail="Customer number already exists")

        customer = await customer_repo.update(customer_id, customer_data.model_dump(exclude_unset=True), "system")  # TODO: tenant context
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return Customer.model_validate(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update customer: {str(e)}")


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete customer (soft delete).

    Mark a customer as inactive. This is a soft delete operation.
    """
    try:
        customer_repo = container.resolve(CustomerRepository)
        success = await customer_repo.delete(customer_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=404, detail="Customer not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete customer: {str(e)}")