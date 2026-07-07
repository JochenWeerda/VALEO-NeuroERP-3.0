"""UIX-063 planning calendar API."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.calendar_projection_service import CALENDAR_LAYERS, CalendarProjectionService

router = APIRouter(prefix="/planung/kalender", tags=["planung", "kalender"])


class CalendarItemOut(BaseModel):
    id: str
    tenant_id: str
    source: str
    source_key: str
    layer: str
    item_type: str
    title: str
    starts_at: str
    ends_at: str | None = None
    all_day: bool
    status: str
    object_type: str | None = None
    object_id: str | None = None
    object_screen_id: str | None = None
    object_route: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ReprojectOut(BaseModel):
    tenantId: str
    horizonDays: int
    projected: int
    sources: dict[str, int]


class IcsTokenOut(BaseModel):
    token: str
    feedUrl: str


def _parse_dt(value: str | None, fallback: datetime) -> datetime:
    if not value:
        return fallback
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid datetime: {value}") from exc


def _item_out(row: dict[str, Any]) -> CalendarItemOut:
    def to_iso(value: Any) -> str | None:
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    payload = row.get("payload") or {}
    if isinstance(payload, str):
        import json
        try:
            payload = json.loads(payload)
        except ValueError:
            payload = {}
    return CalendarItemOut(
        id=str(row.get("id")),
        tenant_id=str(row.get("tenant_id")),
        source=str(row.get("source")),
        source_key=str(row.get("source_key")),
        layer=str(row.get("layer")),
        item_type=str(row.get("item_type")),
        title=str(row.get("title")),
        starts_at=str(to_iso(row.get("starts_at"))),
        ends_at=to_iso(row.get("ends_at")),
        all_day=bool(row.get("all_day")),
        status=str(row.get("status")),
        object_type=row.get("object_type"),
        object_id=row.get("object_id"),
        object_screen_id=row.get("object_screen_id"),
        object_route=row.get("object_route"),
        payload=payload if isinstance(payload, dict) else {},
    )


def _layers(value: str | None) -> list[str] | None:
    if not value:
        return None
    layers = [part.strip() for part in value.split(",") if part.strip()]
    invalid = [layer for layer in layers if layer not in CALENDAR_LAYERS]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Invalid layers: {', '.join(invalid)}")
    return layers


@router.get("", response_model=list[CalendarItemOut], summary="Planungskalender auflisten")
async def list_calendar_items(
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None),
    layers: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[CalendarItemOut]:
    now = datetime.now(UTC)
    from_ts = _parse_dt(from_, now - timedelta(days=7))
    to_ts = _parse_dt(to, now + timedelta(days=30))
    if to_ts <= from_ts:
        raise HTTPException(status_code=422, detail="to must be after from")
    try:
        rows = CalendarProjectionService(db).list_items(tenant_id, from_ts, to_ts, _layers(layers))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="calendar_items table not available") from exc
    return [_item_out(row) for row in rows]


@router.post("/reproject", response_model=ReprojectOut, summary="Planungskalender neu projizieren")
async def reproject_calendar(
    horizon_days: int = Query(default=120, ge=1, le=366),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ReprojectOut:
    try:
        result = CalendarProjectionService(db).reproject(tenant_id, horizon_days=horizon_days)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="calendar_items table not available") from exc
    return ReprojectOut(**result)


@router.post("/items/{item_id}/confirm", response_model=CalendarItemOut, summary="Kalender-Vorschlag bestaetigen")
async def confirm_calendar_item(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CalendarItemOut:
    row = CalendarProjectionService(db).transition_proposed(tenant_id, item_id, "confirmed")
    if not row:
        raise HTTPException(status_code=409, detail="Only proposed calendar items can be confirmed")
    return _item_out(row)


@router.post("/items/{item_id}/dismiss", response_model=CalendarItemOut, summary="Kalender-Vorschlag verwerfen")
async def dismiss_calendar_item(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CalendarItemOut:
    row = CalendarProjectionService(db).transition_proposed(tenant_id, item_id, "dismissed")
    if not row:
        raise HTTPException(status_code=409, detail="Only proposed calendar items can be dismissed")
    return _item_out(row)


@router.get("/ics-token", response_model=IcsTokenOut, summary="ICS Feed Token ausstellen")
async def issue_ics_token(
    user_ref: str = Query(default="default", max_length=128),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> IcsTokenOut:
    token = CalendarProjectionService(db).issue_ics_token(tenant_id, user_ref=user_ref)
    return IcsTokenOut(token=token, feedUrl=f"/api/v1/planung/kalender/ics?token={token}")


@router.post("/ics-token/rotate", response_model=IcsTokenOut, summary="ICS Feed Token rotieren")
async def rotate_ics_token(
    user_ref: str = Query(default="default", max_length=128),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> IcsTokenOut:
    token = CalendarProjectionService(db).issue_ics_token(tenant_id, user_ref=user_ref)
    return IcsTokenOut(token=token, feedUrl=f"/api/v1/planung/kalender/ics?token={token}")


@router.get("/ics", summary="ICS Feed abrufen")
async def get_ics_feed(
    token: str = Query(..., min_length=16),
    db: Session = Depends(get_db),
) -> Response:
    service = CalendarProjectionService(db)
    tenant_id = service.tenant_for_ics_token(token)
    if not tenant_id:
        raise HTTPException(status_code=404, detail="ICS token not found")
    now = datetime.now(UTC)
    content = service.ics_content(tenant_id, now - timedelta(days=30), now + timedelta(days=366))
    return Response(content=content, media_type="text/calendar; charset=utf-8")
