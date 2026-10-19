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
from app.core.tenant import get_tenant_id
from fastapi import Request
from app.auth.deps import get_current_user, User as AuthenticatedUser

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.gdpr_schemas import GdprOut


router = APIRouter()


def _authorize_subject(user_id: str, actor: AuthenticatedUser, *, keycloak_id: str | None = None, erase: bool = False) -> None:
    """Profile access follows the verified identity; erasure is administrative."""
    if not actor.get('sub') or ('admin' not in actor.get('roles', []) and
                                (erase or actor['sub'] not in {user_id, keycloak_id})):
        raise HTTPException(status_code=403, detail="Not authorized for this data subject")


@router.get("/data-export/{user_id}", summary="User data exportieren",
    response_model=GdprOut
)
async def export_user_data(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    actor: AuthenticatedUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    GDPR Article 15: Right to Access
    Export all data for a user.
    """
    
    logger.info("GDPR data-export requested")
    
    try:
        from app.infrastructure.models import (
            User, AuditLog
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
        _authorize_subject(user_id, actor, keycloak_id=user.keycloak_id)
        
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
            AuditLog.user_id == user_id,
            AuditLog.tenant_id == tenant_id,
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
        
        logger.info("GDPR data-export completed; audit rows=%d", len(audit_logs))
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GDPR data-export failed (%s)", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User data export failed"
        )


@router.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Lokales Benutzerprofil anonymisieren",
    response_model=None
)
async def delete_user_data(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    actor: AuthenticatedUser = Depends(get_current_user),
):
    """
    Administratively anonymize the tenant-local profile.
    Retained evidence stays intact. Provider-account deletion and the complete
    data-subject erasure workflow require their separate identity/retention paths.
    """
    
    _authorize_subject(user_id, actor, erase=True)
    logger.warning("GDPR local profile anonymization requested")
    
    try:
        from app.infrastructure.models import User
        
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
        
        # Retained audit evidence is immutable. Any policy-driven erasure of
        # evidence requires the separate retention process, never this profile update.
        
        db.commit()
        
        logger.info("GDPR local profile anonymization completed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GDPR profile anonymization failed (%s)", type(e).__name__)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User profile anonymization failed"
        )


@router.get("/export-portable/{user_id}", summary="Portable data exportieren",
    response_model=GdprOut
)
async def export_portable_data(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    actor: AuthenticatedUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    GDPR Article 20: Right to Data Portability
    Export data in structured, machine-readable format.
    """
    
    logger.info("GDPR portable-export requested")
    
    # Same as data-export but in standardized format
    data = await export_user_data(user_id, request, db, tenant_id, actor)
    
    # Add portability-specific metadata
    data["portability_metadata"] = {
        "format": "JSON",
        "schema_version": "1.0",
        "standards": ["GDPR Article 20"],
        "compatible_with": ["other_erp_systems"]
    }
    
    return data

