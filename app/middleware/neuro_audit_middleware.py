"""
Neuro Audit Middleware — NC-D4
Befuellt das Decision Protocol automatisch aus der Neuro-Core Pipeline.
Loggt jeden Pipeline-Durchlauf als Audit-Eintrag mit Hash-Chain.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def record_pipeline_audit(
    db: Optional[Session],
    tenant_id: str,
    pipeline_result: dict,
    user_id: str = "system",
    channel: str = "api",
) -> Optional[str]:
    if not db or not pipeline_result:
        return None

    trace_id = str(uuid4())
    intent_data = pipeline_result.get("intent", {})
    plan_data = pipeline_result.get("plan")
    status = pipeline_result.get("status", "unknown")

    try:
        from app.services.audit_hardening import append_audit_entry
        append_audit_entry(
            db=db,
            tenant_id=tenant_id,
            action=f"neuro_pipeline:{intent_data.get('intent', 'unknown')}",
            entity_type="neuro_pipeline_run",
            entity_id=plan_data.get("plan_id", trace_id) if plan_data else trace_id,
            user_id=user_id,
            details=json.dumps({
                "trace_id": trace_id,
                "channel": channel,
                "status": status,
                "intent": intent_data,
                "plan_id": plan_data.get("plan_id") if plan_data else None,
                "step_count": plan_data.get("step_count", 0) if plan_data else 0,
                "risk_class": intent_data.get("risk_class", "low"),
                "confidence_score": intent_data.get("confidence_score", 0),
                "verification_status": plan_data.get("verification_status") if plan_data else None,
                "requires_human_approval": plan_data.get("requires_human_approval", False) if plan_data else False,
                "executed_steps": pipeline_result.get("executed_steps"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }),
        )
        logger.info("Pipeline audit recorded: trace=%s intent=%s status=%s", trace_id, intent_data.get("intent"), status)
        return trace_id
    except Exception as exc:
        logger.warning("Failed to record pipeline audit: %s", exc)
        return None


def record_channel_event(
    db: Optional[Session],
    tenant_id: str,
    channel: str,
    event_type: str,
    payload: dict,
    user_id: str = "system",
) -> Optional[str]:
    if not db:
        return None

    trace_id = str(uuid4())
    try:
        from app.services.audit_hardening import append_audit_entry
        append_audit_entry(
            db=db,
            tenant_id=tenant_id,
            action=f"channel:{channel}:{event_type}",
            entity_type="channel_event",
            entity_id=trace_id,
            user_id=user_id,
            details=json.dumps({
                "trace_id": trace_id,
                "channel": channel,
                "event_type": event_type,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }),
        )
        return trace_id
    except Exception as exc:
        logger.warning("Failed to record channel event: %s", exc)
        return None
