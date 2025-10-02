"""
Tenant API endpoints
RESTful API for tenant management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import TenantRepository
from ....core.dependency_container import container
from ..schemas.shared import (
    TenantCreate, TenantUpdate, Tenant
)
from ..schemas.base import PaginatedResponse
from ..schemas.base import PaginationParams

router = APIRouter(tags=["tenants"])


@router.post("/", response_model=Tenant, status_code=201)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tenant.

    This endpoint allows creating a new tenant in the system.
    The tenant will be used for multi-tenant data isolation.
    """
    try:
        tenant_repo = container.resolve(TenantRepository)
        tenant = await tenant_repo.create(tenant_data.model_dump(), tenant_data.name)  # Use tenant name as tenant_id for simplicity
        return Tenant.model_validate(tenant)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create tenant: {str(e)}")


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Get tenant by ID.

    Retrieve detailed information about a specific tenant.
    """
    try:
        tenant_repo = container.resolve(TenantRepository)
        tenant = await tenant_repo.get_by_id(tenant_id, tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return Tenant.model_validate(tenant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tenant: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Tenant])
async def list_tenants(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List tenants with pagination.

    Retrieve a paginated list of all tenants in the system.
    """
    try:
        tenant_repo = container.resolve(TenantRepository)

        # For listing all tenants, we use a dummy tenant_id since this is a system-wide operation
        # In a real implementation, this would require admin privileges
        tenants = await tenant_repo.get_all("system", skip, limit)
        total = await tenant_repo.count("system")

        return PaginatedResponse[Tenant](
            items=[Tenant.model_validate(tenant) for tenant in tenants],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tenants: {str(e)}")


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db)
):
    """
    Update tenant information.

    Modify tenant details such as name, domain, or settings.
    """
    try:
        tenant_repo = container.resolve(TenantRepository)
        tenant = await tenant_repo.update(tenant_id, tenant_data.model_dump(exclude_unset=True), tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return Tenant.model_validate(tenant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tenant: {str(e)}")


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete tenant (soft delete).

    Mark a tenant as inactive. This is a soft delete operation.
    """
    try:
        tenant_repo = container.resolve(TenantRepository)
        success = await tenant_repo.delete(tenant_id, tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tenant not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")