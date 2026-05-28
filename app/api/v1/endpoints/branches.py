"""Branches (Niederlassungen) CRUD endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/admin/branches", tags=["admin", "branches"])

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class BranchBase(BaseModel):
    branch_number: int = Field(ge=0, description="Branch number (0 = main branch)")
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[dict] = None
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[dict] = None
    is_active: Optional[bool] = None


class Branch(BranchBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


def _get_branch_or_404(db: Session, branch_id: str, tenant_id: str) -> dict:
    """Get branch or raise 404."""
    row = db.execute(
        text("""
            SELECT * FROM domain_shared.branches 
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": branch_id, "tenant_id": tenant_id}
    ).mappings().first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Branch not found")
    return dict(row)


@router.post("", response_model=Branch, status_code=status.HTTP_201_CREATED, summary="Branch anlegen")
async def create_branch(
    payload: BranchCreate,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Create a new branch."""
    from app.core.uuid7 import uuid7
    
    # Check if branch_number already exists for this tenant
    existing = db.execute(
        text("""
            SELECT id FROM domain_shared.branches 
            WHERE tenant_id = :tenant_id AND branch_number = :branch_number
        """),
        {"tenant_id": tenant_id, "branch_number": payload.branch_number}
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Branch number {payload.branch_number} already exists for this tenant"
        )
    
    branch_id = uuid7()
    
    db.execute(
        text("""
            INSERT INTO domain_shared.branches (
                id, tenant_id, branch_number, name, address, is_active, created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :branch_number, :name, :address::jsonb, :is_active, NOW(), NOW()
            )
        """),
        {
            "id": branch_id,
            "tenant_id": tenant_id,
            "branch_number": payload.branch_number,
            "name": payload.name,
            "address": str(payload.address or {}).replace("'", '"'),
            "is_active": payload.is_active,
        }
    )
    db.commit()
    
    row = _get_branch_or_404(db, branch_id, tenant_id)
    return Branch(**dict(row))


@router.get("", response_model=list[Branch], summary="Branches auflisten")
async def list_branches(
    tenant_id: str = Query(DEFAULT_TENANT),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List all branches."""
    query = """
        SELECT * FROM domain_shared.branches 
        WHERE tenant_id = :tenant_id
    """
    params = {"tenant_id": tenant_id}
    
    if active_only:
        query += " AND is_active = TRUE"
    
    query += " ORDER BY branch_number"
    
    rows = db.execute(text(query), params).mappings().all()
    return [Branch(**dict(row)) for row in rows]


@router.get("/{branch_id}", response_model=Branch, summary="Branch abrufen")
async def get_branch(
    branch_id: str,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Get a branch by ID."""
    row = _get_branch_or_404(db, branch_id, tenant_id)
    return Branch(**dict(row))


@router.put("/{branch_id}", response_model=Branch, summary="Branch aktualisieren")
async def update_branch(
    branch_id: str,
    payload: BranchUpdate,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Update a branch."""
    _get_branch_or_404(db, branch_id, tenant_id)
    
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if "address" in updates:
        updates["address"] = str(updates["address"]).replace("'", '"')
        set_clause = ", ".join(f"{k} = :{k}::jsonb" if k == "address" else f"{k} = :{k}" for k in updates.keys())
    else:
        set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    
    updates["id"] = branch_id
    updates["tenant_id"] = tenant_id
    
    db.execute(
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        text(f"""
            UPDATE domain_shared.branches 
            SET {set_clause}, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        updates
    )
    db.commit()
    
    row = _get_branch_or_404(db, branch_id, tenant_id)
    return Branch(**dict(row))


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Branch löschen",
    response_model=None
)
async def delete_branch(
    branch_id: str,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Delete a branch."""
    _get_branch_or_404(db, branch_id, tenant_id)
    
    # Check if branch is used in delivery notes
    used = db.execute(
        text("""
            SELECT COUNT(*) FROM domain_sales.delivery_notes 
            WHERE branch_id = :branch_id
        """),
        {"branch_id": branch_id}
    ).scalar()
    
    if used and used > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete branch: it is used in {used} delivery note(s)"
        )
    
    db.execute(
        text("""
            DELETE FROM domain_shared.branches 
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": branch_id, "tenant_id": tenant_id}
    )
    db.commit()
    
    return None


