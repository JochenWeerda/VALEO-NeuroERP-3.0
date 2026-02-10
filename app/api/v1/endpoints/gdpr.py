"""
GDPR API Endpoints
Implements Right-to-Access, Right-to-Delete, Data-Portability
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rbac import require_role, Role, get_tenant_id
from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/data-export/{user_id}")
async def export_user_data(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    GDPR Article 15: Right to Access
    Export all data for a user.
    """
    tenant_id = get_tenant_id(request)
    
    logger.info(f"GDPR data-export requested for user: {user_id}")
    
    try:
        from app.infrastructure.models import (
            User, Customer, AuditLog, JournalEntry
        )
        
        # Get user
        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Collect all user data
        data = {
            "personal_data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": user.roles,
                "created_at": user.created_at.isoformat(),
            },
            "audit_logs": [],
            "created_entities": {
                "customers": [],
                "journal_entries": []
            },
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "tenant_id": tenant_id,
                "format": "JSON"
            }
        }
        
        # Get audit logs
        audit_logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).limit(1000).all()
        
        data["audit_logs"] = [
            {
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id
            }
            for log in audit_logs
        ]
        
        logger.info(
            f"GDPR data-export completed for {user_id}: "
            f"{len(audit_logs)} audit logs"
        )
        
        return data
        
    except Exception as e:
        logger.error(f"GDPR data-export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_data(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_role(Role.ADMIN))
):
    """
    GDPR Article 17: Right to Erasure
    Delete all user data (with anonymization for audit-trail).
    """
    tenant_id = get_tenant_id(request)
    
    logger.warning(f"GDPR deletion requested for user: {user_id}")
    
    try:
        from app.infrastructure.models import User, AuditLog
        
        # Get user
        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Strategy: Soft-Delete + Anonymization
        # Hard-Delete würde GoBD-Audit-Trail verletzen
        
        # 1. Anonymize personal data
        user.email = f"deleted-{user_id}@anonymized.local"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.deleted_at = datetime.utcnow()
        user.is_active = False
        
        # 2. Anonymize in audit logs (nur PII)
        db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).update({
            "user_email": f"deleted-{user_id}@anonymized.local",
            "ip_address": "0.0.0.0"
        })
        
        db.commit()
        
        logger.info(f"GDPR deletion completed for {user_id} (anonymized)")
        
    except Exception as e:
        logger.error(f"GDPR deletion failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/export-portable/{user_id}")
async def export_portable_data(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    GDPR Article 20: Right to Data Portability
    Export data in structured, machine-readable format.
    """
    tenant_id = get_tenant_id(request)
    
    logger.info(f"GDPR portable-export requested for user: {user_id}")
    
    # Same as data-export but in standardized format
    data = await export_user_data(user_id, request, db)
    
    # Add portability-specific metadata
    data["portability_metadata"] = {
        "format": "JSON",
        "schema_version": "1.0",
        "standards": ["GDPR Article 20"],
        "compatible_with": ["other_erp_systems"]
    }
    
    return data

