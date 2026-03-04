"""
Workflow Router
Persisted workflow endpoints (no in-memory runtime state).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.metrics import workflow_transitions_total
from app.core.sse import sse_hub
from app.models.documents import WorkflowAudit, WorkflowStatus
from app.repositories.workflow_repository import WorkflowRepository
from app.services.workflow_service import workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


def get_workflow_repo(db: Session = Depends(get_db)) -> WorkflowRepository:
    # Ensure persisted workflow tables exist in environments without upfront migrations.
    bind = db.get_bind()
    WorkflowStatus.__table__.create(bind=bind, checkfirst=True)
    WorkflowAudit.__table__.create(bind=bind, checkfirst=True)
    return WorkflowRepository(db)


@router.get("/{domain}/{number}")
async def get_status(
    domain: Literal["sales", "purchase"],
    number: str,
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    try:
        return {"ok": True, "state": repo.get_status(domain, number)}
    except Exception as exc:
        logger.error("Failed to get workflow status: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{domain}/{number}/transition")
async def do_transition(
    domain: Literal["sales", "purchase"],
    number: str,
    action: Literal["submit", "approve", "reject", "post"] | None = None,
    payload: dict = Body(...),
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    try:
        resolved_action = action or payload.get("action")
        if resolved_action not in {"submit", "approve", "reject", "post"}:
            raise HTTPException(status_code=400, detail="Invalid action")
        cur = repo.get_status(domain, number)
        ok, nxt, msg = workflow.next(domain, cur, resolved_action, payload)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)

        reason = payload.get("reason") if isinstance(payload.get("reason"), str) else None
        repo.set_status(domain, number, nxt, user=None)
        repo.add_audit(domain, number, cur, nxt, resolved_action, user=None, reason=reason)

        workflow_transitions_total.labels(domain=domain, action=resolved_action, status=nxt).inc()

        asyncio.create_task(
            sse_hub.broadcast(
                "workflow",
                {
                    "id": f"workflow-{domain}-{number}-{int(time.time())}",
                    "ts": time.time(),
                    "source": "db",
                    "topic": "workflow",
                    "domain": domain,
                    "number": number,
                    "action": resolved_action,
                    "fromState": cur,
                    "toState": nxt,
                },
            )
        )

        return {"ok": True, "state": nxt}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to transition workflow: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{domain}/{number}/audit")
async def audit(
    domain: Literal["sales", "purchase"],
    number: str,
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    try:
        items = repo.get_audit(domain, number)
        payload_items = [
            {
                "ts": int(item.ts),
                "from": item.from_state,
                "to": item.to_state,
                "action": item.action,
                "user": item.user,
                "reason": item.reason,
            }
            for item in items
        ]

        asyncio.create_task(
            sse_hub.broadcast(
                "workflow",
                {
                    "id": f"audit-{domain}-{number}-{int(time.time())}",
                    "ts": time.time(),
                    "source": "db",
                    "topic": "workflow",
                    "type": "audit_access",
                    "domain": domain,
                    "number": number,
                    "count": len(payload_items),
                },
            )
        )

        return {"ok": True, "items": payload_items}
    except Exception as exc:
        logger.error("Failed to get audit trail: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/replay/{channel}")
async def replay_events(
    channel: str,
    since: float = 0.0,
    repo: WorkflowRepository = Depends(get_workflow_repo),
):
    try:
        _ = channel
        stmt = select(WorkflowAudit).where(WorkflowAudit.ts >= int(since)).order_by(WorkflowAudit.ts.asc())
        rows = repo.db.execute(stmt).scalars().all()
        events = [
            {
                "id": f"replay-{row.domain}-{row.doc_number}-{row.ts}",
                "ts": row.ts,
                "source": "db",
                "topic": "workflow",
                "type": "replay",
                "domain": row.domain,
                "number": row.doc_number,
                "action": row.action,
                "fromState": row.from_state,
                "toState": row.to_state,
            }
            for row in rows
        ]
        return {"ok": True, "events": events, "count": len(events)}
    except Exception as exc:
        logger.error("Failed to replay events: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
