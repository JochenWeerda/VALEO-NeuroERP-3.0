"""Tenant-safe DMS metadata search and article-document links."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7
from ....integrations.dms_client import get_document_url, is_configured, upload_document

router = APIRouter()


class DMSDocumentOut(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    url: Optional[str] = None


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
    external_gate: str


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
    """Search local metadata and provide an optional external DMS deep link."""
    where = ["a.tenant_id=:tid", "ad.tenant_id=:tid", "a.deleted_at IS NULL"]
    params: dict[str, Any] = {"tid": tenant_id}
    if q.strip():
        where.append(
            "(ad.document_name ILIKE :q OR ad.description ILIKE :q "
            "OR ad.dokument_nummer ILIKE :q OR a.article_number ILIKE :q "
            "OR a.name ILIKE :q OR a.search_vector @@ plainto_tsquery('simple', :tsq))"
        )
        params.update(q=f"%{q.strip()}%", tsq=q.strip())
    if document_type:
        where.append("ad.document_type=:document_type")
        params["document_type"] = document_type
    if document_category:
        where.append("ad.document_category=:document_category")
        params["document_category"] = document_category
    if article_id:
        where.append("ad.article_id=:article_id")
        params["article_id"] = article_id
    where_sql = " AND ".join(where)
    total = db.execute(
        text(f"SELECT COUNT(*) FROM domain_inventory.article_documents ad JOIN domain_inventory.articles a ON a.id=ad.article_id WHERE {where_sql}"),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        params,
    ).scalar_one()
    query_params = {**params, "limit": page_size, "offset": (page - 1) * page_size}
    rows = db.execute(
        text(f"""
          SELECT ad.id,ad.document_id,ad.document_name,ad.document_type,
                 ad.document_category,ad.description,ad.dokument_nummer,
                 ad.valid_from,ad.valid_to,ad.created_at,
                 a.id article_id,a.article_number,a.name article_name
            FROM domain_inventory.article_documents ad
            JOIN domain_inventory.articles a ON a.id=ad.article_id
           WHERE {where_sql}
           ORDER BY ad.created_at DESC,ad.document_name
           LIMIT :limit OFFSET :offset
        """),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        query_params,
    ).mappings().all()
    configured = is_configured()
    gate = "configured" if configured else "not_configured"
    items: list[DMSSearchItem] = []
    for row in rows:
        item = dict(row)
        item["valid_from"] = str(item["valid_from"]) if item.get("valid_from") else None
        item["valid_to"] = str(item["valid_to"]) if item.get("valid_to") else None
        item["created_at"] = str(item["created_at"]) if item.get("created_at") else None
        item["document_number"] = item.pop("dokument_nummer", None)
        item["source_route"] = f"/artikel/stamm/{item['article_id']}"
        item["preview_url"] = get_document_url(item["document_id"]) if configured else None
        item["external_gate"] = gate
        items.append(DMSSearchItem(**item))
    return DMSSearchResponse(items=items, total=int(total), page=page, page_size=page_size, external_gate=gate)


@router.get("/documents", response_model=list[DMSDocumentOut], summary="DMS documents auflisten")
async def list_dms_documents(
    entity_type: Optional[str] = Query(None, description="e.g. 'article', 'customer'"),
    entity_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[DMSDocumentOut]:
    """List canonical metadata without hiding database contract errors."""
    where = ["ad.tenant_id=:tid", "a.tenant_id=:tid", "a.deleted_at IS NULL"]
    params: dict[str, Any] = {"tid": tenant_id}
    if entity_type == "article" and entity_id:
        where.append("ad.article_id=:eid")
        params["eid"] = entity_id
    elif entity_type and entity_type != "article":
        where.append("ad.document_type=:etype")
        params["etype"] = entity_type
    rows = db.execute(
        text(f"""
          SELECT ad.id,ad.document_id,ad.document_name,ad.document_type
            FROM domain_inventory.article_documents ad
            JOIN domain_inventory.articles a ON a.id=ad.article_id
           WHERE {' AND '.join(where)} ORDER BY ad.created_at DESC LIMIT 100
        """),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        params,
    ).mappings().all()
    configured = is_configured()
    return [DMSDocumentOut(
        id=str(row["id"]),
        filename=str(row["document_name"] or "unknown"),
        mime_type=str(row["document_type"]) if "/" in str(row["document_type"] or "") else "application/octet-stream",
        size=0,
        url=get_document_url(row["document_id"]) if configured else None,
    ) for row in rows]


@router.get("/images", response_model=list[DMSImageOut], summary="DMS images auflisten")
async def list_dms_images(
    document_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[DMSImageOut]:
    """Resolve a tenant-owned image reference only when the DMS is available."""
    if not document_id or not is_configured():
        return []
    rows = db.execute(
        text("""
          SELECT ad.id,ad.document_id FROM domain_inventory.article_documents ad
          JOIN domain_inventory.articles a ON a.id=ad.article_id
          WHERE ad.id=:did AND ad.tenant_id=:tid AND a.tenant_id=:tid
            AND ad.document_type LIKE 'image/%' AND a.deleted_at IS NULL LIMIT 50
        """),
        {"did": document_id, "tid": tenant_id},
    ).mappings().all()
    return [DMSImageOut(
        id=str(row["id"]),
        document_id=str(row["document_id"]),
        thumbnail_url=get_document_url(row["document_id"]),
        full_url=get_document_url(row["document_id"]),
    ) for row in rows]


@router.post("/documents", response_model=DMSDocumentOut, status_code=201, summary="DMS document hochladen")
async def upload_dms_document(
    file: UploadFile = File(...),
    entity_type: str = Form("article"),
    entity_id: str = Form(""),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> DMSDocumentOut:
    """Upload externally first, then persist a canonical tenant-owned link."""
    if entity_type != "article" or not entity_id:
        raise HTTPException(status_code=422, detail="Nur Artikel-Dokumente mit entity_id werden unterstuetzt")
    owns_article = db.execute(
        text("SELECT 1 FROM domain_inventory.articles WHERE id=:id AND tenant_id=:tid AND deleted_at IS NULL"),
        {"id": entity_id, "tid": tenant_id},
    ).scalar_one_or_none()
    if owns_article is None:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    if not is_configured():
        raise HTTPException(status_code=503, detail="Externes DMS ist nicht konfiguriert")
    content = await file.read()
    filename = file.filename or "upload"
    temp_path: Optional[str] = None
    try:
        with NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        result = upload_document("article", filename, temp_path, {"tenant_id": tenant_id, "article_id": entity_id})
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
    if not result.get("ok") or result.get("document_id") is None:
        raise HTTPException(status_code=502, detail=f"DMS-Upload fehlgeschlagen: {result.get('error', 'unbekannt')}")
    link_id = uuid7()
    external_id = str(result["document_id"])
    db.execute(
        text("""
          INSERT INTO domain_inventory.article_documents
            (id,tenant_id,article_id,document_id,document_name,document_type,created_at)
          VALUES (:id,:tid,:article_id,:document_id,:document_name,:document_type,NOW())
        """),
        {"id": link_id, "tid": tenant_id, "article_id": entity_id, "document_id": external_id,
         "document_name": filename, "document_type": file.content_type or "application/octet-stream"},
    )
    db.commit()
    return DMSDocumentOut(id=link_id, filename=filename, mime_type=file.content_type or "application/octet-stream",
                          size=len(content), url=str(result.get("url") or get_document_url(external_id)))


@router.delete("/documents/{doc_id}", status_code=204, response_class=Response, response_model=None, summary="DMS document loeschen")
async def delete_dms_document(
    doc_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Unlink tenant-owned metadata; the immutable external original remains."""
    result = db.execute(
        text("DELETE FROM domain_inventory.article_documents WHERE id=:id AND tenant_id=:tid"),
        {"id": doc_id, "tid": tenant_id},
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
    return Response(status_code=204)
