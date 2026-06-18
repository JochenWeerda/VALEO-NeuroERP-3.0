"""MOB-SYNC-001: Mobile Offline-Sync Endpoints.

POST /mobile/sync-events  — Offline-Queue hochladen
POST /mobile/sync-process — Queue verarbeiten (Server-seitig oder Cron)
GET  /mobile/sync-queue   — Queue-Status abrufen
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
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


@router.post("/sync-events", summary="MOB-SYNC-001: Offline-Events in Queue hochladen", status_code=202)
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
    queued = sum(1 for r in results if r["status"] == "queued")
    return {
        "received": len(body.events),
        "queued": queued,
        "rejected": len(results) - queued,
        "results": results,
    }


@router.post("/sync-process", summary="Pending Events verarbeiten")
def process_queue(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Verarbeitet bis zu `limit` ausstehende Events aus der Queue.
    Kann manuell oder per Cron aufgerufen werden.
    """
    svc = MobileSyncService(db, tenant_id)
    return svc.process_pending(limit=limit)


@router.get("/sync-queue", summary="Queue-Status abrufen")
def get_queue(
    status: Optional[str] = Query(None, description="pending | processing | done | failed"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = MobileSyncService(db, tenant_id)
    items = svc.list_queue(status=status, limit=limit)
    return {"items": items, "count": len(items)}
