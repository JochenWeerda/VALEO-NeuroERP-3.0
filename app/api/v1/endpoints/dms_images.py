"""
DMS image endpoints (l3c-dms extension)
CRUD for document images and thumbnails.
"""

from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form,
    Response,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7
from ....integrations.dms_client import get_document_url, is_configured


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


class DMSSearchItem(BaseModel):
    id: str
    document_id: str
    document_name: str
    document_type: Optional[str] = None
    document_category: Optional[str] = None
    description: Optional[str] = None
    document_number: Optional[str] = None
    article_id: str
    article_number: str
    article_name: str
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    created_at: Optional[str] = None
    source_route: str
    preview_url: Optional[str] = None


class DMSSearchResponse(BaseModel):
    items: list[DMSSearchItem]
    total: int
    page: int
    page_size: int
    external_gate: str


@router.get("/search", response_model=DMSSearchResponse, summary="DMS-Volltextsuche")
async def search_dms_documents(
    q: str = Query("", max_length=200),
    document_type: Optional[str] = Query(None, max_length=50),
    document_category: Optional[str] = Query(None, max_length=50),
    article_id: Optional[str] = Query(None, max_length=80),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> DMSSearchResponse:
    """Tenant-sichere lokale Metadaten-/Volltextsuche mit optionalem Mayan-Deep-Link."""
    where = ["a.tenant_id = :tid", "a.deleted_at IS NULL"]
    params: dict[str, Any] = {"tid": tenant_id}
    if q.strip():
        where.append(
            "(ad.document_name ILIKE :q OR ad.description ILIKE :q "
            "OR ad.dokument_nummer ILIKE :q OR a.article_number ILIKE :q "
            "OR a.name ILIKE :q OR a.search_vector @@ plainto_tsquery('simple', :tsq))"
        )
        params.update(q=f"%{q.strip()}%", tsq=q.strip())
    if document_type:
        where.append("ad.document_type = :document_type")
        params["document_type"] = document_type
    if document_category:
        where.append("ad.document_category = :document_category")
        params["document_category"] = document_category
    if article_id:
        where.append("ad.article_id = :article_id")
        params["article_id"] = article_id
    where_sql = " AND ".join(where)
    total = db.execute(
        text(
            f"SELECT COUNT(*) FROM domain_inventory.article_documents ad "
            f"JOIN domain_inventory.articles a ON a.id=ad.article_id WHERE {where_sql}"
        ),
        params,
    ).scalar_one()
    params.update(limit=page_size, offset=(page - 1) * page_size)
    rows = (
        db.execute(
            text(
                f"""
            SELECT ad.id,ad.document_id,ad.document_name,ad.document_type,
                   ad.document_category,ad.description,ad.dokument_nummer,
                   ad.valid_from,ad.valid_to,ad.created_at,
                   a.id article_id,a.article_number,a.name article_name
              FROM domain_inventory.article_documents ad
              JOIN domain_inventory.articles a ON a.id=ad.article_id
             WHERE {where_sql}
             ORDER BY ad.created_at DESC,ad.document_name
             LIMIT :limit OFFSET :offset
            """
            ),
            params,
        )
        .mappings()
        .all()
    )
    configured = is_configured()
    items = []
    for row in rows:
        item = dict(row)
        item["valid_from"] = str(item["valid_from"]) if item.get("valid_from") else None
        item["valid_to"] = str(item["valid_to"]) if item.get("valid_to") else None
        item["created_at"] = str(item["created_at"]) if item.get("created_at") else None
        item["source_route"] = f"/artikel/stamm/{item['article_id']}"
        item["preview_url"] = (
            get_document_url(item["document_id"]) if configured else None
        )
        items.append(DMSSearchItem(**item))
    return DMSSearchResponse(
        items=items,
        total=int(total),
        page=page,
        page_size=page_size,
        external_gate="configured" if configured else "not_configured",
    )


@router.get(
    "/documents", response_model=list[DMSDocumentOut], summary="Dms documents auflisten"
)
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
            rows = db.execute(
                text("""
                SELECT ad.id, ad.file_name, ad.mime_type,
                       COALESCE(ad.file_size, 0) AS size,
                       COALESCE(ad.file_url, '/api/v1/dms/documents/' || ad.id || '/download') AS url
                FROM domain_inventory.article_documents ad
                WHERE ad.article_id = :eid
                ORDER BY ad.created_at DESC
                LIMIT 100
            """),
                {"eid": entity_id},
            ).fetchall()
        else:
            where = "WHERE 1=1"
            if entity_type:
                where += " AND ad.document_type = :etype"
                params["etype"] = entity_type
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            rows = db.execute(
                text(f"""
                SELECT ad.id, ad.file_name, ad.mime_type,
                       COALESCE(ad.file_size, 0) AS size,
                       COALESCE(ad.file_url, '/api/v1/dms/documents/' || ad.id || '/download') AS url
                FROM domain_inventory.article_documents ad
                {where}
                ORDER BY ad.created_at DESC
                LIMIT 100
            """),
                params,
            ).fetchall()

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


@router.get("/images", response_model=list[DMSImageOut], summary="Dms images auflisten")
async def list_dms_images(
    document_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Bilder zu einem Dokument — filtert nach Bild-MIME-Typen."""
    if not document_id:
        return []
    try:
        rows = db.execute(
            text("""
            SELECT ad.id, ad.file_name,
                   COALESCE(ad.file_url, '/api/v1/dms/documents/' || ad.id || '/download') AS url
            FROM domain_inventory.article_documents ad
            WHERE ad.id = :did
              AND ad.mime_type LIKE 'image/%'
            LIMIT 50
        """),
            {"did": document_id},
        ).fetchall()

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


@router.post(
    "/documents",
    response_model=DMSDocumentOut,
    status_code=201,
    summary="Dms document hochladen",
)
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

    db.execute(
        text("""
        INSERT INTO domain_inventory.article_documents
            (id, article_id, file_name, mime_type, file_size, file_url, document_type, created_at)
        VALUES
            (:id, :article_id, :file_name, :mime_type, :file_size, :file_url, :doc_type, NOW())
    """),
        {
            "id": doc_id,
            "article_id": entity_id or None,
            "file_name": file.filename or "upload",
            "mime_type": file.content_type or "application/octet-stream",
            "file_size": len(content),
            "file_url": file_url,
            "doc_type": entity_type,
        },
    )
    db.commit()

    return DMSDocumentOut(
        id=doc_id,
        filename=file.filename or "upload",
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        url=file_url,
    )


@router.delete(
    "/documents/{doc_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
    summary="Dms document löschen",
)
async def delete_dms_document(
    doc_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a document from the DMS store."""
    result = db.execute(
        text("DELETE FROM domain_inventory.article_documents WHERE id = :id"),
        {"id": doc_id},
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    return Response(status_code=204)
