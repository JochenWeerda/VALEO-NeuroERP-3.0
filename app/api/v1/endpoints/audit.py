"""
Audit Logging API
Extended audit trail for compliance (GDPR, GoBD, etc.)
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


class AuditLogEntry(BaseModel):
    """Audit log entry model."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    user_id: str
    user_email: str
    tenant_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: dict
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    

class AuditLogCreate(BaseModel):
    """Create audit log entry."""
    user_id: str
    user_email: str
    tenant_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: dict
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@router.post("/log", response_model=AuditLogEntry, summary="Audit log anlegen")
async def create_audit_log(
    entry: AuditLogCreate,
    db: Session = Depends(get_db)
):
    """Create new audit log entry."""
    from app.infrastructure.models import AuditLog
    from uuid import uuid4
    from app.core.logging import get_correlation_id
    
    log_entry = AuditLog(
        id=str(uuid4()),
        timestamp=datetime.utcnow(),
        user_id=entry.user_id,
        user_email=entry.user_email,
        tenant_id=entry.tenant_id,
        action=entry.action,
        entity_type=entry.entity_type,
        entity_id=entry.entity_id,
        changes=entry.changes,
        ip_address=entry.ip_address,
        user_agent=entry.user_agent,
        correlation_id=get_correlation_id()
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    logger.info(
        f"Audit: {entry.action} on {entry.entity_type}/{entry.entity_id} "
        f"by {entry.user_email}"
    )
    
    return log_entry


@router.get("/logs", response_model=List[AuditLogEntry], summary="Audit logs abrufen")
async def get_audit_logs(
    tenant_id: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Query audit logs with filters. Returns [] if table missing or error."""
    from app.infrastructure.models import AuditLog
    from sqlalchemy import and_

    try:
        query = db.query(AuditLog)
        filters = []
        if tenant_id:
            filters.append(AuditLog.tenant_id == tenant_id)
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if entity_id:
            filters.append(AuditLog.entity_id == entity_id)
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action == action)
        if from_ts:
            filters.append(AuditLog.timestamp >= from_ts)
        if to_ts:
            filters.append(AuditLog.timestamp <= to_ts)
        if filters:
            query = query.filter(and_(*filters))
        logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
        return [
            AuditLogEntry(
                id=log.id,
                timestamp=log.timestamp,
                user_id=log.user_id,
                user_email=log.user_email or "",
                tenant_id=log.tenant_id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                changes=log.changes or {},
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                correlation_id=log.correlation_id,
            )
            for log in logs
        ]
    except Exception as e:
        logger.warning("get_audit_logs: %s", e)
        return []


@router.get("/stats", summary="Audit stats abrufen",
    response_model=CompatFlexOut
)
async def get_audit_stats(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get audit statistics. Returns default stats if table missing or error."""
    from app.infrastructure.models import AuditLog
    from sqlalchemy import func

    default = {
        "total_entries": 0,
        "actions": [],
        "entity_types": [],
        "top_users": [],
        "timestamp": datetime.utcnow().isoformat(),
    }
    try:
        base_query = db.query(AuditLog)
        if tenant_id:
            base_query = base_query.filter(AuditLog.tenant_id == tenant_id)
        total = base_query.count()

        actions_query = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label("count"),
        )
        if tenant_id:
            actions_query = actions_query.filter(AuditLog.tenant_id == tenant_id)
        actions = actions_query.group_by(AuditLog.action).all()

        entities_query = db.query(
            AuditLog.entity_type,
            func.count(AuditLog.id).label("count"),
        )
        if tenant_id:
            entities_query = entities_query.filter(AuditLog.tenant_id == tenant_id)
        entities = entities_query.group_by(AuditLog.entity_type).all()

        top_users_query = db.query(
            AuditLog.user_email,
            func.count(AuditLog.id).label("count"),
        )
        if tenant_id:
            top_users_query = top_users_query.filter(AuditLog.tenant_id == tenant_id)
        top_users = (
            top_users_query.group_by(AuditLog.user_email)
            .order_by(func.count(AuditLog.id).desc())
            .limit(10)
            .all()
        )

        return {
            "total_entries": total,
            "actions": [{"action": a, "count": c} for a, c in actions],
            "entity_types": [{"type": e, "count": c} for e, c in entities],
            "top_users": [{"user": u or "", "count": c} for u, c in top_users],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.warning("get_audit_stats: %s", e)
        return default

