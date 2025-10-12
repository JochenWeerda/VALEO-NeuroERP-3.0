"""
Audit Logging API
Extended audit trail for compliance (GDPR, GoBD, etc.)
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class AuditLogEntry(BaseModel):
    """Audit log entry model."""
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
    
    class Config:
        from_attributes = True


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


@router.post("/log", response_model=AuditLogEntry)
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


@router.get("/logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    tenant_id: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Query audit logs with filters."""
    from app.infrastructure.models import AuditLog
    from sqlalchemy import and_
    
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
    
    if filters:
        query = query.filter(and_(*filters))
    
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return logs


@router.get("/stats")
async def get_audit_stats(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get audit statistics."""
    from app.infrastructure.models import AuditLog
    from sqlalchemy import func, and_
    
    base_query = db.query(AuditLog)
    
    if tenant_id:
        base_query = base_query.filter(AuditLog.tenant_id == tenant_id)
    
    total = base_query.count()
    
    # Actions breakdown
    actions = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).all()
    
    # Entity types breakdown
    entities = db.query(
        AuditLog.entity_type,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.entity_type).all()
    
    # Top users
    top_users = db.query(
        AuditLog.user_email,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.user_email).order_by(
        func.count(AuditLog.id).desc()
    ).limit(10).all()
    
    return {
        "total_entries": total,
        "actions": [{"action": a, "count": c} for a, c in actions],
        "entity_types": [{"type": e, "count": c} for e, c in entities],
        "top_users": [{"user": u, "count": c} for u, c in top_users],
        "timestamp": datetime.utcnow().isoformat()
    }

