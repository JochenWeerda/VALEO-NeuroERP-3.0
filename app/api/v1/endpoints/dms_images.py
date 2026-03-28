"""
DMS image endpoints (l3c-dms extension)
GET for document images and thumbnails.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db

router = APIRouter()


class DMSDocumentOut(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    url: str


class DMSImageOut(BaseModel):
    id: str
    document_id: str
    thumbnail_url: str
    full_url: str


@router.get("/documents", response_model=list[DMSDocumentOut])
async def list_dms_documents(
    entity_type: Optional[str] = Query(None, description="e.g. 'article', 'customer'"),
    entity_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Dokumente aus article_documents oder generischem Document-Store."""
    try:
        conditions = []
        params: dict = {}

        if entity_type == "article" and entity_id:
            rows = db.execute(text("""
                SELECT ad.id, ad.file_name, ad.mime_type,
                       COALESCE(ad.file_size, 0) AS size,
                       COALESCE(ad.file_url, '/api/v1/dms/documents/' || ad.id || '/download') AS url
                FROM domain_inventory.article_documents ad
                WHERE ad.article_id = :eid
                ORDER BY ad.created_at DESC
                LIMIT 100
            """), {"eid": entity_id}).fetchall()
        else:
            where = "WHERE 1=1"
            if entity_type:
                where += " AND ad.document_type = :etype"
                params["etype"] = entity_type
            rows = db.execute(text(f"""
                SELECT ad.id, ad.file_name, ad.mime_type,
                       COALESCE(ad.file_size, 0) AS size,
                       COALESCE(ad.file_url, '/api/v1/dms/documents/' || ad.id || '/download') AS url
                FROM domain_inventory.article_documents ad
                {where}
                ORDER BY ad.created_at DESC
                LIMIT 100
            """), params).fetchall()

        return [
            DMSDocumentOut(
                id=r.id,
                filename=r.file_name or "unknown",
                mime_type=r.mime_type or "application/octet-stream",
                size=r.size,
                url=r.url,
            )
            for r in rows
        ]
    except Exception:
        return []


@router.get("/images", response_model=list[DMSImageOut])
async def list_dms_images(
    document_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Bilder zu einem Dokument — filtert nach Bild-MIME-Typen."""
    if not document_id:
        return []
    try:
        rows = db.execute(text("""
            SELECT ad.id, ad.file_name,
                   COALESCE(ad.file_url, '/api/v1/dms/documents/' || ad.id || '/download') AS url
            FROM domain_inventory.article_documents ad
            WHERE ad.id = :did
              AND ad.mime_type LIKE 'image/%'
            LIMIT 50
        """), {"did": document_id}).fetchall()

        return [
            DMSImageOut(
                id=r.id,
                document_id=document_id,
                thumbnail_url=r.url,
                full_url=r.url,
            )
            for r in rows
        ]
    except Exception:
        return []
