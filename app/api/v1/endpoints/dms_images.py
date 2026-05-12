"""
DMS image endpoints (l3c-dms extension)
CRUD for document images and thumbnails.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7

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
        _conditions = []  # noqa: F841
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


@router.post("/documents", response_model=DMSDocumentOut, status_code=201)
async def upload_dms_document(
    file: UploadFile = File(...),
    entity_type: str = Form("article"),
    entity_id: str = Form(""),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Upload a document to the DMS store."""
    content = await file.read()
    doc_id = uuid7()
    file_url = f"/api/v1/dms/documents/{doc_id}/download"

    db.execute(text("""
        INSERT INTO domain_inventory.article_documents
            (id, article_id, file_name, mime_type, file_size, file_url, document_type, created_at)
        VALUES
            (:id, :article_id, :file_name, :mime_type, :file_size, :file_url, :doc_type, NOW())
    """), {
        "id": doc_id,
        "article_id": entity_id or None,
        "file_name": file.filename or "upload",
        "mime_type": file.content_type or "application/octet-stream",
        "file_size": len(content),
        "file_url": file_url,
        "doc_type": entity_type,
    })
    db.commit()

    return DMSDocumentOut(
        id=doc_id,
        filename=file.filename or "upload",
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        url=file_url,
    )


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_dms_document(
    doc_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a document from the DMS store."""
    result = db.execute(text(
        "DELETE FROM domain_inventory.article_documents WHERE id = :id"
    ), {"id": doc_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    return Response(status_code=204)
