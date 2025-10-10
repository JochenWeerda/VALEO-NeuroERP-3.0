"""
Workflow Router
API-Endpoints für Workflow-Management mit State-Machine und SSE-Broadcasts
"""

from __future__ import annotations
from fastapi import APIRouter, Body, HTTPException
from typing import Literal
import time
import logging

from app.services.workflow_service import workflow
from app.core.sse import sse_hub
from app.core.metrics import workflow_transitions_total
from app.repositories.workflow_repository import WorkflowRepository
from app.core.database_pg import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

# In-memory stores (DEPRECATED - wird durch PostgreSQL ersetzt)
_STATE: dict[tuple[str, str], str] = {}      # (domain,number) -> state
_AUDIT: dict[tuple[str, str], list] = {}

# PostgreSQL-Repository (wird schrittweise aktiviert)
async def get_workflow_repo(db: AsyncSession = get_db()) -> WorkflowRepository:
    """FastAPI Dependency für WorkflowRepository"""
    return WorkflowRepository(db)

# Export für andere Module
__all__ = ["_STATE"]


@router.get("/{domain}/{number}")
async def get_status(domain: Literal["sales", "purchase"], number: str):
    """
    Holt aktuellen Workflow-Status für Beleg

    Args:
        domain: Belegtyp (sales/purchase)
        number: Beleg-Nummer

    Returns:
        Status-Info
    """
    try:
        st = _STATE.get((domain, number), "draft")
        return {"ok": True, "state": st}
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{domain}/{number}/transition")
async def do_transition(
    domain: Literal["sales", "purchase"],
    number: str,
    action: Literal["submit", "approve", "reject", "post"],
    payload: dict = Body(...)
):
    """
    Führt Workflow-Transition aus

    Args:
        domain: Belegtyp
        number: Beleg-Nummer
        action: Aktion
        payload: Beleg-Daten für Guards

    Returns:
        Neuer Status
    """
    try:
        cur = _STATE.get((domain, number), "draft")

        # Guards werden in workflow.next() geprüft
        ok, nxt, msg = workflow.next(domain, cur, action, payload)
        if not ok:
            raise HTTPException(400, detail=msg)

        _STATE[(domain, number)] = nxt
        _AUDIT.setdefault((domain, number), []).append({
            "ts": int(time.time()),
            "from": cur,
            "to": nxt,
            "action": action
        })

        # Prometheus Metric
        workflow_transitions_total.labels(domain=domain, action=action, status=nxt).inc()

        # SSE Broadcast
        import asyncio
        asyncio.create_task(sse_hub.broadcast("workflow", {
            "id": f"workflow-{domain}-{number}-{int(time.time())}",
            "ts": time.time(),
            "source": "mcp",
            "topic": "workflow",
            "domain": domain,
            "number": number,
            "action": action,
            "fromState": cur,
            "toState": nxt,
        }))

        logger.info(f"Workflow transition: {domain}/{number} {cur} → {nxt} ({action})")
        return {"ok": True, "state": nxt}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to transition workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain}/{number}/audit")
async def audit(domain: Literal["sales", "purchase"], number: str):
    """
    Holt Audit-Trail für Beleg

    Args:
        domain: Belegtyp
        number: Beleg-Nummer

    Returns:
        Audit-Einträge
    """
    try:
        items = _AUDIT.get((domain, number), [])

        # SSE Broadcast für Audit-Abruf
        import asyncio
        asyncio.create_task(sse_hub.broadcast("workflow", {
            "id": f"audit-{domain}-{number}-{int(time.time())}",
            "ts": time.time(),
            "source": "mcp",
            "topic": "workflow",
            "type": "audit_access",
            "domain": domain,
            "number": number,
            "count": len(items),
        }))

        return {"ok": True, "items": items}
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/replay/{channel}")
async def replay_events(channel: str, since: float = 0.0):
    """
    Replay von Workflow-Events seit Timestamp

    Args:
        channel: SSE-Channel (z.B. "workflow")
        since: Unix-Timestamp für Replay-Start

    Returns:
        Events seit dem angegebenen Zeitpunkt
    """
    try:
        # Sammle alle relevanten Events seit dem Timestamp
        events = []

        # Durchsuche alle Workflow-States und deren Audit-Trails
        for (domain, number), audit_trail in _AUDIT.items():
            for entry in audit_trail:
                if entry["ts"] >= since:
                    events.append({
                        "id": f"replay-{domain}-{number}-{entry['ts']}",
                        "ts": entry["ts"],
                        "source": "mcp",
                        "topic": "workflow",
                        "type": "replay",
                        "domain": domain,
                        "number": number,
                        "action": entry["action"],
                        "fromState": entry["from"],
                        "toState": entry["to"],
                    })

        # Sortiere nach Timestamp
        events.sort(key=lambda x: x["ts"])

        return {"ok": True, "events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Failed to replay events: {e}")
        raise HTTPException(status_code=500, detail=str(e))