"""MOB-SYNC-001: Mobile Offline-Sync Endpoints.

POST /mobile/sync-events  — Offline-Queue hochladen
POST /mobile/sync-process — Queue verarbeiten (Server-seitig oder Cron)
GET  /mobile/sync-queue   — Queue-Status abrufen
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mobile_sync_service import MobileSyncService

router = APIRouter(prefix="/mobile", tags=["mobile", "sync"])


class MobileEvent(BaseModel):
    event_type: str = Field(..., description="delivery_confirmation | inventory_count | qs_probe_result | harvest_acceptance | silo_transfer | generic")
    payload: dict = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class SyncBatchIn(BaseModel):
    device_id: str = Field(..., min_length=1)
    events: list[MobileEvent] = Field(..., min_length=1, max_length=200)


class RetryEventIn(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


class ProcessQueueIn(BaseModel):
    reason: str = Field(default="Manuelle MDE-Verarbeitung", min_length=5, max_length=500)


@router.post("/sync-events", response_model=dict, summary="MOB-SYNC-001: Offline-Events in Queue hochladen", status_code=202)
def sync_events(
    body: SyncBatchIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Nimmt einen Batch von Offline-Events vom Gerät entgegen und legt sie in die Queue.

    Idempotent: gleiche idempotency_key×device_id werden nur einmal gespeichert.
    """
    svc = MobileSyncService(db, tenant_id)
    results = svc.enqueue_events(
        device_id=body.device_id,
        events=[e.model_dump() for e in body.events],
    )
    queued = sum(1 for r in results if r["status"] in {"queued", "duplicate"})
    return {
        "received": len(body.events),
        "queued": queued,
        "rejected": len(results) - queued,
        "results": results,
    }


@router.post("/sync-process", response_model=dict, summary="Pending Events verarbeiten")
def process_queue(
    request: Request,
    body: ProcessQueueIn | None = None,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Verarbeitet bis zu `limit` ausstehende Events aus der Queue.
    Kann manuell oder per Cron aufgerufen werden.
    """
    svc = MobileSyncService(db, tenant_id)
    actor = (request.headers.get("X-User-ID") or "mde-operator")[:120]
    return svc.process_pending(limit=limit, actor=actor, reason=(body.reason if body else "Manuelle MDE-Verarbeitung"))


@router.get("/sync-queue", response_model=dict, summary="Queue-Status abrufen")
def get_queue(
    status: Optional[str] = Query(None, description="pending | processing | done | failed | quarantined"),
    device_id: Optional[str] = Query(None, max_length=120),
    event_type: Optional[str] = Query(None, max_length=80),
    q: Optional[str] = Query(None, max_length=160),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    sort: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = MobileSyncService(db, tenant_id)
    try:
        return svc.list_queue_page(
            status=status,
            device_id=device_id,
            event_type=event_type,
            q=q,
            page=page,
            page_size=page_size,
            sort=sort,
            sort_dir=sort_dir,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/sync-summary", response_model=dict, summary="MDE Queue-Zusammenfassung abrufen")
def get_queue_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, int]:
    return MobileSyncService(db, tenant_id).queue_summary()


@router.post("/sync-queue/{event_id}/retry", response_model=dict, summary="Fehlgeschlagenes MDE-Ereignis wiederholen")
def retry_event(
    event_id: str,
    body: RetryEventIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    actor = (request.headers.get("X-User-ID") or "mde-operator")[:120]
    try:
        return MobileSyncService(db, tenant_id).retry_event(event_id, actor=actor, reason=body.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/sync-queue/{event_id}/audit", response_model=list[dict], summary="MDE-Ereignis-Audit abrufen")
def get_event_audit(
    event_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    try:
        return MobileSyncService(db, tenant_id).event_audit(event_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
