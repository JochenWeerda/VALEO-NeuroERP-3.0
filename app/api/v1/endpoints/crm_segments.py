"""
CRM Kundensegmente — CRUD-Stub

GET    /crm/segments          Liste aller Kundensegmente
POST   /crm/segments          Neues Segment anlegen
GET    /crm/segments/{id}     Segment abrufen
PUT    /crm/segments/{id}     Segment aktualisieren
DELETE /crm/segments/{id}     Segment löschen
"""
from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query

from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/crm/segments", tags=["crm", "segments"])

_SEGMENTS: dict[str, dict[str, Any]] = {}
_ID_SEQ = 0


def _next_id() -> str:
    global _ID_SEQ
    _ID_SEQ += 1
    return str(_ID_SEQ)


@router.get("", summary="Kundensegmente auflisten")
@router.get("/", summary="Kundensegmente auflisten", include_in_schema=False)
async def list_segments(
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    items = list(_SEGMENTS.values())
    if search:
        items = [s for s in items if search.lower() in s.get("name", "").lower()]
    return {"items": items[offset : offset + limit], "total": len(items)}


@router.post("", status_code=201, summary="Kundensegment anlegen")
@router.post("/", status_code=201, include_in_schema=False)
async def create_segment(
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    seg_id = _next_id()
    segment = {"id": seg_id, "tenant_id": tenant_id, **body}
    _SEGMENTS[seg_id] = segment
    return segment


@router.get("/{segment_id}", summary="Kundensegment abrufen")
async def get_segment(
    segment_id: str = Path(...),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    seg = _SEGMENTS.get(segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="Segment nicht gefunden")
    return seg


@router.put("/{segment_id}", summary="Kundensegment aktualisieren")
async def update_segment(
    segment_id: str = Path(...),
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    if segment_id not in _SEGMENTS:
        raise HTTPException(status_code=404, detail="Segment nicht gefunden")
    _SEGMENTS[segment_id].update(body)
    return _SEGMENTS[segment_id]


@router.delete("/{segment_id}", status_code=204, summary="Kundensegment löschen")
async def delete_segment(
    segment_id: str = Path(...),
    tenant_id: str = Depends(get_tenant_id),
) -> None:
    _SEGMENTS.pop(segment_id, None)
