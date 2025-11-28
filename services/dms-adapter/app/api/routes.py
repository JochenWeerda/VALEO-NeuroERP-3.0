"""
DMS-Adapter API Routes

REST API Endpoints für Dokumentenverwaltung.
"""
from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException, Query, Response
from typing import Optional, List
import logging

from app.services.document_service import document_service
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentLinkRequest,
    UploadResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dms", tags=["DMS"])


# ==================== Health ====================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health-Check Endpoint"""
    paperless_ok = await document_service.health_check()
    return HealthResponse(
        status="healthy" if paperless_ok else "degraded",
        paperless_connected=paperless_ok,
        database_connected=True,  # TODO: DB-Check
    )


# ==================== Documents ====================

@router.post("/documents", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="Dokument-Datei"),
    tenant_id: str = Form(..., description="Mandanten-ID"),
    title: Optional[str] = Form(None, description="Dokumenttitel"),
    business_object_type: Optional[str] = Form(None, description="Geschäftsobjekt-Typ"),
    business_object_id: Optional[str] = Form(None, description="Geschäftsobjekt-ID"),
    document_type: Optional[str] = Form(None, description="Dokumenttyp"),
    tags: Optional[str] = Form(None, description="Komma-getrennte Tags"),
):
    """
    Dokument hochladen und optional mit Geschäftsobjekt verknüpfen.
    
    - **file**: Die hochzuladende Datei
    - **tenant_id**: Mandanten-ID (Pflicht)
    - **title**: Optionaler Titel (sonst Dateiname)
    - **business_object_type**: z.B. INVOICE, ORDER, CUSTOMER
    - **business_object_id**: z.B. Rechnungsnummer 4711
    - **document_type**: z.B. rechnung, lieferschein, zertifikat
    - **tags**: Zusätzliche Tags, komma-getrennt
    """
    try:
        additional_tags = tags.split(",") if tags else None
        
        result = await document_service.upload_document(
            file=file.file,
            filename=file.filename,
            tenant_id=tenant_id,
            title=title,
            business_object_type=business_object_type,
            business_object_id=business_object_id,
            document_type=document_type,
            additional_tags=additional_tags,
        )
        
        return UploadResponse(
            ok=True,
            document_id=result.id,
            paperless_id=result.paperless_id,
            title=result.title,
            download_url=result.download_url,
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload fehlgeschlagen: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID", description="Mandanten-ID"),
    business_object_type: Optional[str] = Query(None, description="Filter nach Objekt-Typ"),
    business_object_id: Optional[str] = Query(None, description="Filter nach Objekt-ID"),
    q: Optional[str] = Query(None, description="Volltextsuche"),
    page: int = Query(1, ge=1, description="Seite"),
    page_size: int = Query(25, ge=1, le=100, description="Einträge pro Seite"),
):
    """
    Dokumente auflisten mit optionaler Filterung.
    
    - **X-Tenant-ID**: Mandanten-ID im Header (Pflicht)
    - **business_object_type**: Filter nach Geschäftsobjekt-Typ
    - **business_object_id**: Filter nach Geschäftsobjekt-ID
    - **q**: Volltextsuche
    """
    try:
        return await document_service.list_documents(
            tenant_id=x_tenant_id,
            business_object_type=business_object_type,
            business_object_id=business_object_id,
            query=q,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        raise HTTPException(status_code=500, detail=f"Abrufen fehlgeschlagen: {str(e)}")


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Einzelnes Dokument abrufen"""
    try:
        result = await document_service.get_document(document_id, x_tenant_id)
        if not result:
            raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document failed: {e}")
        raise HTTPException(status_code=500, detail=f"Abrufen fehlgeschlagen: {str(e)}")


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Dokument herunterladen"""
    try:
        content = await document_service.download_document(document_id, x_tenant_id)
        
        # Content-Type bestimmen (vereinfacht)
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=document_{document_id}"
            }
        )
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=f"Download fehlgeschlagen: {str(e)}")


@router.get("/documents/{document_id}/thumbnail")
async def get_thumbnail(
    document_id: int,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Dokument-Thumbnail abrufen"""
    try:
        content = await document_service.get_thumbnail(document_id, x_tenant_id)
        return Response(content=content, media_type="image/webp")
    except Exception as e:
        logger.error(f"Thumbnail failed: {e}")
        raise HTTPException(status_code=500, detail=f"Thumbnail fehlgeschlagen: {str(e)}")


@router.post("/documents/{paperless_id}/link", response_model=DocumentResponse)
async def link_document(
    paperless_id: int,
    link_request: DocumentLinkRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """
    Bestehendes Dokument mit Geschäftsobjekt verknüpfen.
    
    Für Inbox-Workflow: Unzugeordnete Dokumente nachträglich zuordnen.
    """
    try:
        return await document_service.link_document(
            paperless_document_id=paperless_id,
            tenant_id=x_tenant_id,
            business_object_type=link_request.business_object_type,
            business_object_id=link_request.business_object_id,
            document_type=link_request.document_type,
        )
    except Exception as e:
        logger.error(f"Link document failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verknüpfung fehlgeschlagen: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Dokument löschen"""
    try:
        success = await document_service.delete_document(document_id, x_tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
        return {"ok": True, "message": "Dokument gelöscht"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Löschen fehlgeschlagen: {str(e)}")


# ==================== Inbox ====================

@router.get("/inbox", response_model=DocumentListResponse)
async def get_inbox(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    """
    Unzugeordnete Dokumente (Inbox) abrufen.
    
    Zeigt Dokumente, die noch keinem Geschäftsobjekt zugeordnet sind.
    """
    try:
        return await document_service.get_inbox(
            tenant_id=x_tenant_id,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Get inbox failed: {e}")
        raise HTTPException(status_code=500, detail=f"Inbox-Abruf fehlgeschlagen: {str(e)}")


# ==================== Search ====================

@router.get("/search", response_model=DocumentListResponse)
async def search_documents(
    q: str = Query(..., min_length=1, description="Suchbegriff"),
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    """
    Volltextsuche in Dokumenten.
    
    Nutzt die OCR-Ergebnisse von Paperless-ngx für die Suche.
    """
    try:
        return await document_service.search(
            tenant_id=x_tenant_id,
            query=q,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Suche fehlgeschlagen: {str(e)}")

