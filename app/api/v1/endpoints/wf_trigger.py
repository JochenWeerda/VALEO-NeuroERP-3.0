"""WF-TRIGGER-001: Status-Trigger → Folgeaktion-API."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.wf_trigger_service import WfTriggerService, TRIGGER_MAP

router = APIRouter(prefix="/wf-trigger", tags=["workflow", "automation"])


class TriggerIn(BaseModel):
    entity_type: str
    entity_id: str
    new_status: str
    context: dict[str, Any] = {}


@router.post("", status_code=200, summary="Status-Trigger manuell feuern (WF-TRIGGER-001)")
def fire_trigger(
    body: TriggerIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Feuert alle registrierten Folgeaktionen für entity_type+new_status.

    Wird normalerweise von Domain-Services intern aufgerufen.
    Dieser Endpoint ermöglicht manuelles Nachfeuern (z.B. nach Datenmigration).
    """
    svc = WfTriggerService(db, tenant_id)
    results = svc.fire(body.entity_type, body.entity_id, body.new_status, body.context)
    return {"entity_type": body.entity_type, "entity_id": body.entity_id,
            "new_status": body.new_status, "actions": results}


@router.get("/map", summary="Trigger-Map: alle registrierten Automationen")
def get_trigger_map() -> dict:
    """Gibt die vollständige Trigger-Konfiguration zurück."""
    return {"trigger_map": TRIGGER_MAP}


@router.get("/log", summary="Trigger-Ausführungslog")
def get_trigger_log(
    entity_type: str | None = Query(None),
    entity_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Listet gefeuerte Trigger-Aktionen aus dem Ausführungslog."""
    from sqlalchemy import text
    where = "tenant_id = :tid"
    params: dict = {"tid": tenant_id, "lim": limit}
    if entity_type:
        where += " AND entity_type = :etype"
        params["etype"] = entity_type
    if entity_id:
        where += " AND entity_id = :eid"
        params["eid"] = entity_id
    try:
        rows = db.execute(text(f"""
            SELECT id, entity_type, entity_id, trigger_status,
                   actions AS action, result, error_detail AS error_message, fired_at
              FROM domain_ops.wf_trigger_log
             WHERE {where}
             ORDER BY fired_at DESC
             LIMIT :lim
        """), params).fetchall()
        return {
            "items": [
                {"id": str(r[0]), "entity_type": r[1], "entity_id": r[2],
                 "trigger_status": r[3], "action": r[4], "result": r[5],
                 "error_message": r[6],
                 "fired_at": r[7].isoformat() if r[7] else None}
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
