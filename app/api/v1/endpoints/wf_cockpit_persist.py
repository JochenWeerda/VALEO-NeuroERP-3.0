"""WF-COCKPIT-PERSIST-001 — DB-backed Cockpit API (Dead-Letter + Detail)."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.wf_cockpit_persist_service import WorkflowCockpitPersistService

router = APIRouter(prefix="/workflow/cockpit-db", tags=["workflow", "cockpit"])


def _svc(
    db: Session = Depends(get_db),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> WorkflowCockpitPersistService:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return WorkflowCockpitPersistService(db=db, tenant_id=x_tenant_id)


@router.get("/instances", response_model=dict[str, Any], summary="Cockpit-Instanzen (DB)")
def list_instances(
    status: str | None = Query(None),
    process_key: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: WorkflowCockpitPersistService = Depends(_svc),
) -> dict[str, Any]:
    items = svc.list_instances(
        status=status, process_key=process_key, limit=limit, offset=offset
    )
    return {"items": items, "count": len(items)}


@router.get("/instances/{process_instance_id}", response_model=dict[str, Any], summary="Cockpit-Instanz-Detail")
def get_instance(
    process_instance_id: str,
    svc: WorkflowCockpitPersistService = Depends(_svc),
) -> dict[str, Any]:
    detail = svc.get_instance_detail(process_instance_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Prozess-Instanz nicht gefunden")
    return detail


@router.get("/dead-letter", response_model=dict[str, Any], summary="Dead-Letter-Sicht: FAILED / BLOCKED_EXTERNAL_GATE")
def dead_letter(
    limit: int = Query(100, ge=1, le=500),
    svc: WorkflowCockpitPersistService = Depends(_svc),
) -> dict[str, Any]:
    return svc.dead_letter_view(limit=limit)


@router.post("/instances", response_model=dict[str, Any], summary="Cockpit-Instanz manuell anlegen/aktualisieren")
def upsert_instance(
    body: dict[str, Any],
    svc: WorkflowCockpitPersistService = Depends(_svc),
) -> dict[str, Any]:
    process_instance_id = body.get("process_instance_id", "")
    if not process_instance_id:
        raise HTTPException(status_code=422, detail="process_instance_id erforderlich")
    svc.upsert_instance(
        process_instance_id=process_instance_id,
        process_key=body.get("process_key", "unknown"),
        status=body.get("status", "running"),
        correlation_id=body.get("correlation_id", process_instance_id),
        current_step=body.get("current_step"),
        business_object_ref=body.get("business_object_ref"),
        audit_ref=body.get("audit_ref"),
    )
    return {"process_instance_id": process_instance_id, "ok": True}


@router.post(
    "/instances/{process_instance_id}/blockers/{blocker_id}/resolve",
    response_model=dict[str, Any],
    summary="Blocker als resolved markieren",
)
def resolve_blocker(
    process_instance_id: str,
    blocker_id: str,
    svc: WorkflowCockpitPersistService = Depends(_svc),
) -> dict[str, Any]:
    resolved = svc.resolve_blocker(blocker_id=blocker_id)
    if not resolved:
        raise HTTPException(status_code=404, detail="Blocker nicht gefunden oder bereits resolved")
    return {"blocker_id": blocker_id, "resolved": True}
