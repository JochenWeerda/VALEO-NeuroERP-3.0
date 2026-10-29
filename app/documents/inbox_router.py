"""HTTP-Vertrag der Launcher-Inbox. Haengt am vorhandenen Documents-Router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.finance_roles import beleg_read
from app.core.database import get_db
from app.core.tenant import get_tenant_id

from .inbox_contract import BOOKING_BLOCKED_REASON, PIPELINE_GAPS
from .inbox_service import build_item, build_queue, prepare_item

inbox_router = APIRouter(tags=["documents-inbox"], dependencies=[Depends(beleg_read)])


@inbox_router.get("/inbox/queue")
def inbox_queue(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
) -> dict:
    return build_queue(db, tenant_id, nutzer, limit=limit)


@inbox_router.get("/inbox/{item_id}")
def inbox_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
) -> dict:
    item = build_item(db, tenant_id, item_id, nutzer)
    if item is None:
        raise HTTPException(status_code=404, detail="Inbox-Dokument nicht gefunden")
    return {"ok": True, "item": item, "booking_allowed": False, "gaps": list(PIPELINE_GAPS)}


@inbox_router.post("/inbox/{item_id}/prepare")
def inbox_prepare(
    item_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
) -> dict:
    prepared = prepare_item(db, tenant_id, item_id, nutzer)
    if prepared is None:
        raise HTTPException(status_code=404, detail="Inbox-Dokument nicht gefunden")
    return prepared


@inbox_router.post("/inbox/{item_id}/approve")
def inbox_approve_blocked(
    item_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
) -> dict:
    """Freigabe bucht nicht. Der Client oeffnet die bestehende Belegmaske."""
    item = build_item(db, tenant_id, item_id, nutzer)
    if item is None:
        raise HTTPException(status_code=404, detail="Inbox-Dokument nicht gefunden")
    raise HTTPException(
        status_code=409,
        detail={
            "code": "booking_not_from_inbox",
            "message": BOOKING_BLOCKED_REASON,
            "open_mask": item["proposal"]["target_route"],
            "can_open": item.get("can_open", False),
            "prefill": item["command"]["prefill"],
            "prepare_path": f"/api/mcp/documents/inbox/{item_id}/prepare",
            "gaps": list(PIPELINE_GAPS),
        },
    )
