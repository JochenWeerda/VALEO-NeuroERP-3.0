"""
Document Schemas

Pydantic-Schemas für DMS-Adapter API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    """Basis-Schema für Dokumente"""
    title: Optional[str] = None
    business_object_type: Optional[str] = Field(
        None, 
        description="Geschäftsobjekt-Typ (z.B. INVOICE, ORDER, CUSTOMER)"
    )
    business_object_id: Optional[str] = Field(
        None,
        description="Geschäftsobjekt-ID (z.B. Rechnungsnummer)"
    )
    document_type: Optional[str] = Field(
        None,
        description="Dokumenttyp (z.B. rechnung, lieferschein, zertifikat)"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Zusätzliche Tags"
    )


class DocumentCreate(DocumentBase):
    """Schema für Dokument-Upload"""
    tenant_id: str = Field(..., description="Mandanten-ID")


class DocumentLinkRequest(BaseModel):
    """Schema für nachträgliche Verknüpfung"""
    business_object_type: str = Field(
        ..., 
        description="Geschäftsobjekt-Typ"
    )
    business_object_id: str = Field(
        ...,
        description="Geschäftsobjekt-ID"
    )
    document_type: Optional[str] = Field(
        None,
        description="Dokumenttyp"
    )


class DocumentResponse(BaseModel):
    """Schema für Dokument-Antwort"""
    id: int
    paperless_id: Optional[int] = None
    title: str
    filename: Optional[str] = None
    file_type: Optional[str] = None
    size_kb: Optional[float] = None
    tenant_id: Optional[str] = None
    business_object_type: Optional[str] = None
    business_object_id: Optional[str] = None
    document_type: Optional[str] = None
    created_at: Optional[datetime] = None
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema für Dokumenten-Liste"""
    data: List[DocumentResponse]
    total: int
    page: int = 1
    page_size: int = 25


class UploadResponse(BaseModel):
    """Schema für Upload-Antwort"""
    ok: bool = True
    document_id: int
    paperless_id: Optional[int] = None
    title: str
    download_url: str


class SearchRequest(BaseModel):
    """Schema für Suchanfrage"""
    query: str = Field(..., min_length=1, description="Suchbegriff")
    page: int = Field(1, ge=1)
    page_size: int = Field(25, ge=1, le=100)


class HealthResponse(BaseModel):
    """Schema für Health-Check"""
    status: str
    paperless_connected: bool
    database_connected: bool = True

