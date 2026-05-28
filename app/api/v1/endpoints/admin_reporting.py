"""Admin CRUD for self-service report permissions."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema


router = APIRouter()


class ReportPermissionIn(BaseModel):
    role_id: str = Field(..., min_length=1, max_length=64)
    report_key: str = Field(..., min_length=1, max_length=120)
    can_view: bool = True
    can_export: bool = False
    allowed_scopes: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    active: bool = True


class ReportPermissionOut(ReportPermissionIn):
    id: str
    created_at: str
    updated_at: str


def _jsonable(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for key, value in list(out.items()):
        if isinstance(value, UUID):
            out[key] = str(value)
        elif isinstance(value, datetime):
            out[key] = value.isoformat()
    return out


@router.get("/report-permissions", response_model=list[ReportPermissionOut], summary="Report permissions auflisten")
def list_report_permissions(
    role_id: str | None = Query(default=None),
    report_key: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if role_id:
        where.append("role_id = :role_id")
        params["role_id"] = role_id
    if report_key:
        where.append("report_key = :report_key")
        params["report_key"] = report_key
    if active_only:
        where.append("active = true")
    rows = db.execute(
        text(
            f"""
            SELECT id, role_id, report_key, can_view, can_export, allowed_scopes, filters, active, created_at, updated_at
            FROM domain_shared.admin_report_permissions
            WHERE {' AND '.join(where)}
            ORDER BY role_id ASC, report_key ASC
            """
        ),
        params,
    ).mappings().all()
    return [ReportPermissionOut(**_jsonable(dict(row))) for row in rows]


@router.get("/report-permissions/{permission_id}", response_model=ReportPermissionOut, summary="Report permission abrufen")
def get_report_permission(
    permission_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT id, role_id, report_key, can_view, can_export, allowed_scopes, filters, active, created_at, updated_at
            FROM domain_shared.admin_report_permissions
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {"tenant_id": tenant_id, "id": permission_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Report permission not found")
    return ReportPermissionOut(**_jsonable(dict(row)))


@router.post("/report-permissions", response_model=ReportPermissionOut, status_code=201, summary="Report permission anlegen")
def create_report_permission(
    payload: ReportPermissionIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item_id = str(uuid4())
    try:
        row = db.execute(
            text(
                """
                INSERT INTO domain_shared.admin_report_permissions
                (id, tenant_id, role_id, report_key, can_view, can_export, allowed_scopes, filters, active, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :role_id, :report_key, :can_view, :can_export, CAST(:allowed_scopes AS jsonb), CAST(:filters AS jsonb), :active, NOW(), NOW())
                RETURNING id, role_id, report_key, can_view, can_export, allowed_scopes, filters, active, created_at, updated_at
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "role_id": payload.role_id.strip(),
                "report_key": payload.report_key.strip(),
                "can_view": payload.can_view,
                "can_export": payload.can_export,
                "allowed_scopes": json.dumps(payload.allowed_scopes),
                "filters": json.dumps(payload.filters),
                "active": payload.active,
            },
        ).mappings().first()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create report permission: {exc}") from exc
    return ReportPermissionOut(**_jsonable(dict(row)))


@router.put("/report-permissions/{permission_id}", response_model=ReportPermissionOut, summary="Report permission aktualisieren")
def update_report_permission(
    permission_id: str,
    payload: ReportPermissionIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_report_permissions
            SET role_id=:role_id,
                report_key=:report_key,
                can_view=:can_view,
                can_export=:can_export,
                allowed_scopes=CAST(:allowed_scopes AS jsonb),
                filters=CAST(:filters AS jsonb),
                active=:active,
                updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": permission_id,
            "role_id": payload.role_id.strip(),
            "report_key": payload.report_key.strip(),
            "can_view": payload.can_view,
            "can_export": payload.can_export,
            "allowed_scopes": json.dumps(payload.allowed_scopes),
            "filters": json.dumps(payload.filters),
            "active": payload.active,
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Report permission not found")
    db.commit()
    return get_report_permission(permission_id, tenant_id, db)


@router.delete("/report-permissions/{permission_id}", status_code=204, response_class=Response, response_model=None, summary="Report permission löschen")
def delete_report_permission(
    permission_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_report_permissions WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": permission_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Report permission not found")
    db.commit()
    return None
