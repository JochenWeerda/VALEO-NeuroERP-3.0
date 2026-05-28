"""CRM Service Cases API endpoints proxied through crm-service."""

from __future__ import annotations

from datetime import datetime, timezone
from math import ceil
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
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

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.cases_schemas import CasesOut


router = APIRouter()

# ---------------------------------------------------------------------------
# SLA defaults (hours): {priority: (first_response_h, resolution_h)}
# ---------------------------------------------------------------------------
SLA_RULES: dict[str, tuple[int, int]] = {
    "HIGH": (4, 24),
    "MEDIUM": (8, 48),
    "LOW": (24, 120),
}
_DEFAULT_SLA = SLA_RULES["MEDIUM"]


def _compute_sla(
    created_at: datetime,
    priority: str,
    first_response_at: Optional[datetime],
    resolved_at: Optional[datetime],
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Compute SLA status from case timestamps."""
    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure timezone-aware
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if first_response_at and first_response_at.tzinfo is None:
        first_response_at = first_response_at.replace(tzinfo=timezone.utc)
    if resolved_at and resolved_at.tzinfo is None:
        resolved_at = resolved_at.replace(tzinfo=timezone.utc)

    resp_h, res_h = SLA_RULES.get(priority.upper(), _DEFAULT_SLA)
    resolution_deadline = created_at.timestamp() + res_h * 3600
    response_deadline = created_at.timestamp() + resp_h * 3600

    elapsed = now.timestamp() - created_at.timestamp()
    hours_until_res_breach = (resolution_deadline - now.timestamp()) / 3600

    if resolved_at:
        sla_status = "ok"
    elif now.timestamp() > resolution_deadline:
        sla_status = "breached"
    elif now.timestamp() > resolution_deadline - 3600:
        sla_status = "warning"
    else:
        sla_status = "ok"

    return {
        "sla_status": sla_status,
        "priority": priority,
        "hours_until_breach": max(0.0, round(hours_until_res_breach, 2)),
        "first_response_deadline_hours": resp_h,
        "resolution_deadline_hours": res_h,
        "first_response_at": first_response_at.isoformat() if first_response_at else None,
        "resolution_at": resolved_at.isoformat() if resolved_at else None,
        "elapsed_hours": round(elapsed / 3600, 2),
    }


@router.post("/", response_model=Case, status_code=status.HTTP_201_CREATED, summary="Case anlegen")
async def create_case(case_data: CaseCreate):
    """Create a new support case via crm-service."""
    try:
        created = await crm_create_case(case_data.model_dump())
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create case: {exc}") from exc
    return Case.model_validate(created)


@router.get("/", response_model=PaginatedResponse[Case], summary="Cases auflisten")
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


@router.get("/{case_id}", response_model=Case, summary="Case abrufen")
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


@router.put("/{case_id}", response_model=Case, summary="Case aktualisieren")
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


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Case löschen",
    response_model=None
)
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


@router.post("/{case_id}/escalate", response_model=CasesOut, summary="Case escalate")
async def escalate_case(
    case_id: str,
    reason: str = Query(..., description="Reason for escalation"),
    escalated_by: str = Query(..., description="User performing escalation"),
    db: Session = Depends(get_db),
):
    """Eskalation eines Service-Cases mit Priorität auf CRITICAL."""
    # Try DB update first
    try:
        row = db.execute(
            text("SELECT id, priority, status FROM cases WHERE id = :cid"),
            {"cid": case_id},
        ).fetchone()
        if row:
            db.execute(
                text(
                    """
                    UPDATE cases
                    SET priority = 'HIGH',
                        escalated = TRUE,
                        escalation_reason = :reason,
                        escalated_by = :by,
                        escalated_at = NOW(),
                        updated_at = NOW()
                    WHERE id = :cid
                    """
                ),
                {"reason": reason, "by": escalated_by, "cid": case_id},
            )
            db.commit()
            return {
                "case_id": case_id,
                "escalated": True,
                "priority": "HIGH",
                "escalation_reason": reason,
                "escalated_by": escalated_by,
                "escalated_at": datetime.now(timezone.utc).isoformat(),
            }
    except Exception:
        db.rollback()

    # Fallback to CRM integration
    try:
        result = await crm_escalate_case(case_id, reason, escalated_by)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Case not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to escalate case: {exc}") from exc
    return result


# ---------------------------------------------------------------------------
# SLA endpoints
# ---------------------------------------------------------------------------

@router.get("/sla-dashboard", response_model=CasesOut, tags=["crm", "cases", "sla"], summary="Sla dashboard abrufen")
async def get_sla_dashboard(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """SLA-Dashboard: total, on_time, warning, breached, avg_resolution_hours."""
    try:
        sql = text(
            """
            SELECT
                priority,
                status,
                created_at,
                first_response_at,
                resolved_at
            FROM cases
            WHERE :tid IS NULL OR tenant_id = :tid
            """
        )
        rows = db.execute(sql, {"tid": tenant_id}).fetchall()
    except Exception:
        db.rollback()
        rows = []

    now = datetime.now(timezone.utc)
    total = len(rows)
    on_time = warning = breached = 0
    resolution_hours: list[float] = []

    for row in rows:
        priority = (row[0] or "MEDIUM").upper()
        created_at = row[2]
        first_resp = row[3]
        resolved_at = row[4]

        if created_at is None:
            continue

        sla = _compute_sla(created_at, priority, first_resp, resolved_at, now)
        s = sla["sla_status"]
        if s == "ok":
            on_time += 1
        elif s == "warning":
            warning += 1
        else:
            breached += 1

        if resolved_at:
            if resolved_at.tzinfo is None:
                resolved_at = resolved_at.replace(tzinfo=timezone.utc)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            resolution_hours.append((resolved_at - created_at).total_seconds() / 3600)

    avg_res = round(sum(resolution_hours) / len(resolution_hours), 2) if resolution_hours else None

    return {
        "total": total,
        "on_time": on_time,
        "warning": warning,
        "breached": breached,
        "avg_resolution_hours": avg_res,
        "sla_rules": {k: {"first_response_h": v[0], "resolution_h": v[1]} for k, v in SLA_RULES.items()},
    }


@router.get("/{case_id}/sla-status", response_model=CasesOut, tags=["crm", "cases", "sla"], summary="Case sla status abrufen")
async def get_case_sla_status(
    case_id: str,
    db: Session = Depends(get_db),
):
    """SLA-Status eines einzelnen Cases."""
    try:
        row = db.execute(
            text(
                """
                SELECT id, priority, status, created_at, first_response_at, resolved_at
                FROM cases WHERE id = :cid
                """
            ),
            {"cid": case_id},
        ).fetchone()
    except Exception:
        db.rollback()
        row = None

    if not row:
        # Fallback to CRM service
        try:
            case_data = await crm_get_case(case_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Case nicht gefunden") from exc
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Case konnte nicht geladen werden: {exc}") from exc

        import dateutil.parser as dparser  # type: ignore[import]
        try:
            created_at = dparser.parse(case_data.get("created_at", datetime.now(timezone.utc).isoformat()))
        except Exception:
            created_at = datetime.now(timezone.utc)
        priority = case_data.get("priority", "MEDIUM")
        first_resp = None
        resolved_at = None
    else:
        priority = row[1] or "MEDIUM"
        created_at = row[3]
        first_resp = row[4]
        resolved_at = row[5]
        if created_at is None:
            created_at = datetime.now(timezone.utc)

    return {"case_id": case_id, **_compute_sla(created_at, priority, first_resp, resolved_at)}
