"""LOG-FRACHTBRIEF-001 — GET/POST /api/v1/logistik/frachtbriefe."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(tags=["logistik", "frachtbriefe"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class FrachtbriefOut(BaseSchema):
    id: str
    nummer: str
    kennzeichen: Optional[str] = None
    artikel: Optional[str] = None
    menge: Optional[Decimal] = None
    absender: Optional[str] = None
    empfaenger: Optional[str] = None
    datum: date
    status: str
    tour_id: Optional[str] = None
    lieferschein_ref: Optional[str] = None


class FrachtbriefCreate(BaseSchema):
    nummer: str = Field(min_length=1, max_length=60)
    kennzeichen: Optional[str] = Field(default=None, max_length=20)
    artikel: Optional[str] = Field(default=None, max_length=120)
    menge: Optional[Decimal] = Field(default=None, ge=0)
    absender: Optional[str] = Field(default=None, max_length=120)
    empfaenger: Optional[str] = Field(default=None, max_length=120)
    datum: date
    tour_id: Optional[str] = Field(default=None, max_length=36)
    lieferschein_ref: Optional[str] = Field(default=None, max_length=60)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/frachtbriefe",
    response_model=list[FrachtbriefOut],
    summary="Frachtbriefe auflisten",
)
def list_frachtbriefe(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    tour_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[FrachtbriefOut]:
    where = "tenant_id = :tenant_id"
    params: dict = {"tenant_id": tenant_id}
    if status_filter:
        where += " AND status = :status"
        params["status"] = status_filter
    if tour_id:
        where += " AND tour_id = :tour_id"
        params["tour_id"] = tour_id
    rows = db.execute(
        text(
            f"SELECT * FROM domain_logistics.frachtbriefe"  # nosec S608 — column names code-controlled, values parameterized
            f" WHERE {where} ORDER BY datum DESC, created_at DESC LIMIT :limit"
        ),
        {**params, "limit": limit},
    ).mappings().all()
    return [FrachtbriefOut.model_validate(dict(r)) for r in rows]


@router.post(
    "/frachtbriefe",
    response_model=FrachtbriefOut,
    status_code=status.HTTP_201_CREATED,
    summary="Frachtbrief anlegen",
)
def create_frachtbrief(
    payload: FrachtbriefCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> FrachtbriefOut:
    fb_id = str(uuid.uuid4())
    db.execute(
        text(
            "INSERT INTO domain_logistics.frachtbriefe"
            " (id, tenant_id, nummer, kennzeichen, artikel, menge, absender, empfaenger,"
            "  datum, status, tour_id, lieferschein_ref)"
            " VALUES (:id, :tenant_id, :nummer, :kennzeichen, :artikel, :menge, :absender,"
            "         :empfaenger, :datum, 'erstellt', :tour_id, :lieferschein_ref)"
        ),
        {
            "id": fb_id,
            "tenant_id": tenant_id,
            **payload.model_dump(),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_logistics.frachtbriefe WHERE id = :id"),
        {"id": fb_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Frachtbrief konnte nicht gespeichert werden")
    return FrachtbriefOut.model_validate(dict(row))


@router.patch(
    "/frachtbriefe/{fb_id}/status",
    response_model=FrachtbriefOut,
    summary="Frachtbrief-Status aktualisieren",
)
def update_frachtbrief_status(
    fb_id: str,
    new_status: str = Query(..., alias="status", pattern="^(erstellt|unterwegs|zugestellt|storniert)$"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> FrachtbriefOut:
    result = db.execute(
        text(
            "UPDATE domain_logistics.frachtbriefe SET status = :status,"
            " updated_at = :now WHERE id = :id AND tenant_id = :tenant_id RETURNING *"
        ),
        {"status": new_status, "now": datetime.now(timezone.utc), "id": fb_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not result:
        raise HTTPException(status_code=404, detail="Frachtbrief nicht gefunden")
    db.commit()
    return FrachtbriefOut.model_validate(dict(result))
