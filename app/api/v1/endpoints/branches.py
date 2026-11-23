"""Branches (Niederlassungen) CRUD endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.auth.deps import require_roles
from pydantic import BaseModel, Field, computed_field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/admin/branches", tags=["admin", "branches"])

_NUR_ADMIN = [Depends(require_roles("admin"))]  # Konfiguration: wie admin_core

# Mandant aus der geprueften Anmeldung (get_tenant_id). Bis 27.10.2026 kam er aus ?tenant_id=
# mit dem Standardmandanten als Rueckfall.


class BranchBase(BaseModel):
    branch_number: int = Field(ge=0, description="Branch number (0 = main branch)")
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[dict] = None
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


_BRANCH_VERSION_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class BranchUpdate(BaseModel):
    expected_version: int | None = Field(default=None, ge=0, le=9007199254740991)
    name: Optional[str] = None
    address: Optional[dict] = None
    is_active: Optional[bool] = None


class Branch(BranchBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def version(self) -> int:
        # Preserve PostgreSQL's microsecond precision in the browser's integer version.
        age = self.updated_at - _BRANCH_VERSION_EPOCH
        return (age.days * 86400 + age.seconds) * 1000000 + age.microseconds


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


@router.post("", response_model=Branch, status_code=status.HTTP_201_CREATED, summary="Branch anlegen", dependencies=_NUR_ADMIN)
async def create_branch(
    payload: BranchCreate,
    tenant_id: str = Depends(get_tenant_id),
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
                :id, :tenant_id, :branch_number, :name, CAST(:address AS jsonb), :is_active, NOW(), NOW()
            )
        """),
        {
            "id": branch_id,
            "tenant_id": tenant_id,
            "branch_number": payload.branch_number,
            "name": payload.name,
            "address": json.dumps(payload.address or {}),
            "is_active": payload.is_active,
        }
    )
    db.commit()
    
    row = _get_branch_or_404(db, branch_id, tenant_id)
    return Branch(**dict(row))


@router.get("", response_model=list[Branch], summary="Branches auflisten")
async def list_branches(
    tenant_id: str = Depends(get_tenant_id),
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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get a branch by ID."""
    row = _get_branch_or_404(db, branch_id, tenant_id)
    return Branch(**dict(row))


@router.put("/{branch_id}", response_model=Branch, summary="Branch aktualisieren", dependencies=_NUR_ADMIN)
async def update_branch(
    branch_id: str,
    payload: BranchUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update a branch and return the exact row written by this request."""
    updates = {
        key: value
        for key, value in payload.model_dump(exclude_unset=True, exclude={"expected_version"}).items()
        if value is not None
    }
    if not updates:
        _get_branch_or_404(db, branch_id, tenant_id)
        raise HTTPException(status_code=400, detail="No fields to update")

    if "address" in updates:
        updates["address"] = json.dumps(updates["address"])
    set_clause = ", ".join(
        "address = CAST(:address AS jsonb)" if key == "address" else f"{key} = :{key}"
        for key in updates
    )

    params = {**updates, "id": branch_id, "tenant_id": tenant_id}
    version_condition = ""
    if payload.expected_version is not None:
        params["expected_updated_at"] = _BRANCH_VERSION_EPOCH + timedelta(microseconds=payload.expected_version)
        version_condition = "AND updated_at = :expected_updated_at"

    row = db.execute(
        text(f"""
            UPDATE domain_shared.branches
            SET {set_clause}, updated_at = GREATEST(clock_timestamp(), updated_at + INTERVAL '1 microsecond')
            WHERE id = :id AND tenant_id = :tenant_id {version_condition}
            RETURNING *
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).mappings().first()
    if row is None:
        if payload.expected_version is not None:
            _get_branch_or_404(db, branch_id, tenant_id)
            raise HTTPException(status_code=409, detail="Branch has changed")
        raise HTTPException(status_code=404, detail="Branch not found")
    result = Branch(**dict(row))
    db.commit()
    return result


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Branch löschen",
    response_model=None, dependencies=_NUR_ADMIN)
async def delete_branch(
    branch_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a branch."""
    zweig = dict(_get_branch_or_404(db, branch_id, tenant_id))

    # Belege tragen die Niederlassung im Kopfbaustein organisation (BELEG-052), als Kennung oder
    # Niederlassungsnummer. Eine Niederlassung mit Belegen bleibt stehen - sonst zeigten diese ins Leere.
    belegt = db.execute(
        text("""
            SELECT COUNT(*) FROM domain_docflow.document_headers
            WHERE tenant_id = :tenant_id AND deleted_at IS NULL
              AND bausteine #>> '{organisation,niederlassung}' IN (:id, :kuerzel)
        """),
        {"tenant_id": tenant_id, "id": str(branch_id), "kuerzel": str(zweig["branch_number"] if zweig.get("branch_number") is not None else branch_id)},
    ).scalar()
    if belegt:
        raise HTTPException(status_code=409, detail=f"Die Niederlassung steht auf {belegt} Beleg(en) und bleibt.")
    db.execute(
        text("""
            DELETE FROM domain_shared.branches 
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": branch_id, "tenant_id": tenant_id}
    )
    db.commit()
    
    return None


