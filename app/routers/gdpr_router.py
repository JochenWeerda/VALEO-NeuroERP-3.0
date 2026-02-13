"""
GDPR Compliance Router
Data erasure and privacy endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from sqlalchemy import text
from app.core.database_pg import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gdpr", tags=["gdpr"])


@router.delete("/erase/{user_id}")
async def erase_user_data(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    GDPR Right to Erasure (Art. 17)
    
    Löscht alle personenbezogenen Daten eines Users
    
    ⚠️ Requires admin scope: gdpr:erase
    """
    try:
        # Anonymize user in audit trails
        await db.execute(
            text("UPDATE workflow_audit SET user = 'DELETED' WHERE user = :user_id"),
            {"user_id": user_id}
        )
        
        # Anonymize user in archive
        await db.execute(
            text("UPDATE archive_index SET user = 'DELETED' WHERE user = :user_id"),
            {"user_id": user_id}
        )
        
        # Anonymize user in documents
        await db.execute(
            text("UPDATE documents_header SET created_by = 'DELETED' WHERE created_by = :user_id"),
            {"user_id": user_id}
        )
        
        await db.commit()
        
        logger.info(f"GDPR erasure completed for user: {user_id}")
        
        return {
            "ok": True,
            "message": f"User data erased for {user_id}",
            "anonymized": True
        }
    
    except Exception as e:
        logger.error(f"GDPR erasure failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{user_id}")
async def export_user_data(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    GDPR Right to Data Portability (Art. 20)
    
    Exportiert alle personenbezogenen Daten eines Users
    
    ⚠️ Requires scope: gdpr:export
    """
    try:
        # Fetch user's audit trail
        result = await db.execute(
            text("SELECT * FROM workflow_audit WHERE user = :user_id"),
            {"user_id": user_id}
        )
        audit_entries = [dict(row._mapping) for row in result]
        
        # Fetch user's documents
        result = await db.execute(
            text("SELECT * FROM documents_header WHERE created_by = :user_id"),
            {"user_id": user_id}
        )
        documents = [dict(row._mapping) for row in result]
        
        # Fetch user's archive entries
        result = await db.execute(
            text("SELECT * FROM archive_index WHERE user = :user_id"),
            {"user_id": user_id}
        )
        archives = [dict(row._mapping) for row in result]
        
        return {
            "ok": True,
            "user_id": user_id,
            "data": {
                "audit_trail": audit_entries,
                "documents": documents,
                "archives": archives
            }
        }
    
    except Exception as e:
        logger.error(f"GDPR export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

