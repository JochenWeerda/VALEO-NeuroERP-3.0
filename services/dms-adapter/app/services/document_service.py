"""
Document Service

Business-Logik für Dokumentenverwaltung.
Verbindet ERP-Geschäftsobjekte mit Paperless-ngx Dokumenten.
"""
from typing import Optional, List, BinaryIO
from datetime import datetime
import logging

from app.config import get_settings
from app.services.paperless_client import paperless_client
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse,
    DocumentLinkRequest,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Service für Dokumentenverwaltung"""
    
    def __init__(self):
        self.paperless = paperless_client
    
    # ==================== Tag-Hilfsmethoden ====================
    
    def _build_tag_name(self, prefix: str, value: str) -> str:
        """Erstelle Tag-Namen nach Konvention"""
        return f"{prefix}:{value}"
    
    async def _get_business_tags(
        self,
        tenant_id: str,
        business_object_type: Optional[str] = None,
        business_object_id: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[int]:
        """Hole oder erstelle Tags für Geschäftsobjekt-Verknüpfung"""
        tag_ids = []
        
        # Tenant-Tag (immer erforderlich)
        tenant_tag = self._build_tag_name(settings.TAG_PREFIX_TENANT, tenant_id)
        tag_ids.append(await self.paperless.get_or_create_tag(tenant_tag))
        
        # Business-Object-Tags (optional)
        if business_object_type:
            obj_type_tag = self._build_tag_name(settings.TAG_PREFIX_OBJECT_TYPE, business_object_type)
            tag_ids.append(await self.paperless.get_or_create_tag(obj_type_tag))
        
        if business_object_id:
            obj_id_tag = self._build_tag_name(settings.TAG_PREFIX_OBJECT_ID, business_object_id)
            tag_ids.append(await self.paperless.get_or_create_tag(obj_id_tag))
        
        if document_type:
            doc_type_tag = self._build_tag_name(settings.TAG_PREFIX_DOCTYPE, document_type)
            tag_ids.append(await self.paperless.get_or_create_tag(doc_type_tag))
        
        return tag_ids
    
    async def _get_tag_ids_for_filter(self, tenant_id: str) -> List[int]:
        """Hole Tag-IDs für Tenant-Filterung"""
        tenant_tag = self._build_tag_name(settings.TAG_PREFIX_TENANT, tenant_id)
        try:
            tag_id = await self.paperless.get_or_create_tag(tenant_tag)
            return [tag_id]
        except Exception:
            return []
    
    # ==================== Dokument-Operationen ====================
    
    async def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        tenant_id: str,
        title: Optional[str] = None,
        business_object_type: Optional[str] = None,
        business_object_id: Optional[str] = None,
        document_type: Optional[str] = None,
        additional_tags: Optional[List[str]] = None,
    ) -> DocumentResponse:
        """
        Dokument hochladen und mit Geschäftsobjekt verknüpfen.
        
        Args:
            file: Datei-Objekt
            filename: Dateiname
            tenant_id: Mandanten-ID
            title: Dokumenttitel (optional)
            business_object_type: z.B. INVOICE, ORDER, CUSTOMER
            business_object_id: z.B. Rechnungsnummer
            document_type: z.B. rechnung, lieferschein
            additional_tags: Zusätzliche Tags
        
        Returns:
            DocumentResponse mit Dokument-Metadaten
        """
        # Tags vorbereiten
        tag_ids = await self._get_business_tags(
            tenant_id=tenant_id,
            business_object_type=business_object_type,
            business_object_id=business_object_id,
            document_type=document_type,
        )
        
        # Zusätzliche Tags hinzufügen
        if additional_tags:
            for tag_name in additional_tags:
                tag_id = await self.paperless.get_or_create_tag(tag_name)
                tag_ids.append(tag_id)
        
        # Dokument hochladen
        result = await self.paperless.upload_document(
            file=file,
            filename=filename,
            title=title or filename,
            tags=tag_ids,
        )
        
        # Response aufbereiten
        return DocumentResponse(
            id=result.get("id") or result.get("task_id"),
            paperless_id=result.get("id"),
            title=title or filename,
            filename=filename,
            tenant_id=tenant_id,
            business_object_type=business_object_type,
            business_object_id=business_object_id,
            document_type=document_type,
            created_at=datetime.utcnow(),
            download_url=f"/api/dms/documents/{result.get('id')}/download",
        )
    
    async def list_documents(
        self,
        tenant_id: str,
        business_object_type: Optional[str] = None,
        business_object_id: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> DocumentListResponse:
        """
        Dokumente auflisten mit Filterung nach Geschäftsobjekt.
        
        Args:
            tenant_id: Mandanten-ID (Pflicht für Isolation)
            business_object_type: Filter nach Objekt-Typ
            business_object_id: Filter nach Objekt-ID
            query: Volltextsuche
            page: Seite
            page_size: Einträge pro Seite
        
        Returns:
            DocumentListResponse mit Dokumenten-Liste
        """
        # Tags für Filterung holen
        filter_tags = await self._get_tag_ids_for_filter(tenant_id)
        
        # Weitere Filter-Tags hinzufügen
        if business_object_type:
            obj_type_tag = self._build_tag_name(settings.TAG_PREFIX_OBJECT_TYPE, business_object_type)
            try:
                tag_id = await self.paperless.get_or_create_tag(obj_type_tag)
                filter_tags.append(tag_id)
            except Exception:
                pass
        
        if business_object_id:
            obj_id_tag = self._build_tag_name(settings.TAG_PREFIX_OBJECT_ID, business_object_id)
            try:
                tag_id = await self.paperless.get_or_create_tag(obj_id_tag)
                filter_tags.append(tag_id)
            except Exception:
                pass
        
        # Dokumente abrufen
        result = await self.paperless.list_documents(
            query=query,
            tags=filter_tags if filter_tags else None,
            page=page,
            page_size=page_size,
        )
        
        # Response aufbereiten
        documents = []
        for doc in result.get("results", []):
            documents.append(DocumentResponse(
                id=doc["id"],
                paperless_id=doc["id"],
                title=doc.get("title", ""),
                filename=doc.get("original_file_name", ""),
                file_type=doc.get("original_file_name", "").split(".")[-1] if doc.get("original_file_name") else None,
                size_kb=doc.get("file_size", 0) / 1024 if doc.get("file_size") else None,
                tenant_id=tenant_id,
                created_at=doc.get("created"),
                download_url=f"/api/dms/documents/{doc['id']}/download",
                thumbnail_url=f"/api/dms/documents/{doc['id']}/thumbnail",
            ))
        
        return DocumentListResponse(
            data=documents,
            total=result.get("count", 0),
            page=page,
            page_size=page_size,
        )
    
    async def get_document(self, document_id: int, tenant_id: str) -> Optional[DocumentResponse]:
        """Einzelnes Dokument abrufen"""
        doc = await self.paperless.get_document(document_id)
        
        # TODO: Tenant-Prüfung (Tags checken)
        
        return DocumentResponse(
            id=doc["id"],
            paperless_id=doc["id"],
            title=doc.get("title", ""),
            filename=doc.get("original_file_name", ""),
            file_type=doc.get("original_file_name", "").split(".")[-1] if doc.get("original_file_name") else None,
            size_kb=doc.get("file_size", 0) / 1024 if doc.get("file_size") else None,
            tenant_id=tenant_id,
            created_at=doc.get("created"),
            download_url=f"/api/dms/documents/{doc['id']}/download",
            thumbnail_url=f"/api/dms/documents/{doc['id']}/thumbnail",
        )
    
    async def download_document(self, document_id: int, tenant_id: str) -> bytes:
        """Dokument herunterladen"""
        # TODO: Tenant-Prüfung
        return await self.paperless.download_document(document_id)
    
    async def get_thumbnail(self, document_id: int, tenant_id: str) -> bytes:
        """Thumbnail abrufen"""
        # TODO: Tenant-Prüfung
        return await self.paperless.get_thumbnail(document_id)
    
    async def link_document(
        self,
        paperless_document_id: int,
        tenant_id: str,
        business_object_type: str,
        business_object_id: str,
        document_type: Optional[str] = None,
    ) -> DocumentResponse:
        """
        Bestehendes Dokument nachträglich mit Geschäftsobjekt verknüpfen.
        Für Inbox-Workflow: Unzugeordnete Dokumente zuordnen.
        """
        # Aktuelle Tags holen
        doc = await self.paperless.get_document(paperless_document_id)
        current_tags = doc.get("tags", [])
        
        # Neue Tags hinzufügen
        new_tag_ids = await self._get_business_tags(
            tenant_id=tenant_id,
            business_object_type=business_object_type,
            business_object_id=business_object_id,
            document_type=document_type,
        )
        
        # Tags zusammenführen (ohne Duplikate)
        all_tags = list(set(current_tags + new_tag_ids))
        
        # Dokument aktualisieren
        await self.paperless.update_document(
            document_id=paperless_document_id,
            tags=all_tags,
        )
        
        return await self.get_document(paperless_document_id, tenant_id)
    
    async def delete_document(self, document_id: int, tenant_id: str) -> bool:
        """Dokument löschen"""
        # TODO: Tenant-Prüfung
        return await self.paperless.delete_document(document_id)
    
    async def get_inbox(self, tenant_id: str, page: int = 1, page_size: int = 25) -> DocumentListResponse:
        """
        Unzugeordnete Dokumente (Inbox) abrufen.
        Dokumente mit Tenant-Tag aber ohne Business-Object-Tags.
        """
        # Tenant-Tag holen
        tenant_tag_ids = await self._get_tag_ids_for_filter(tenant_id)
        
        # Alle Dokumente mit Tenant-Tag
        result = await self.paperless.list_documents(
            tags=tenant_tag_ids,
            page=page,
            page_size=page_size,
        )
        
        # Filtern: nur Dokumente OHNE OBJ-Tags
        inbox_docs = []
        for doc in result.get("results", []):
            # Prüfe ob OBJ-Tag vorhanden
            tags = await self._get_document_tags(doc["id"])
            has_obj_tag = any(
                t.startswith(f"{settings.TAG_PREFIX_OBJECT_TYPE}:") 
                for t in tags
            )
            
            if not has_obj_tag:
                inbox_docs.append(DocumentResponse(
                    id=doc["id"],
                    paperless_id=doc["id"],
                    title=doc.get("title", ""),
                    filename=doc.get("original_file_name", ""),
                    file_type=doc.get("original_file_name", "").split(".")[-1] if doc.get("original_file_name") else None,
                    size_kb=doc.get("file_size", 0) / 1024 if doc.get("file_size") else None,
                    tenant_id=tenant_id,
                    created_at=doc.get("created"),
                    download_url=f"/api/dms/documents/{doc['id']}/download",
                    thumbnail_url=f"/api/dms/documents/{doc['id']}/thumbnail",
                ))
        
        return DocumentListResponse(
            data=inbox_docs,
            total=len(inbox_docs),
            page=page,
            page_size=page_size,
        )
    
    async def _get_document_tags(self, document_id: int) -> List[str]:
        """Hole Tag-Namen für ein Dokument"""
        doc = await self.paperless.get_document(document_id)
        tag_ids = doc.get("tags", [])
        
        # Tag-Namen auflösen
        all_tags = await self.paperless.list_tags()
        tag_map = {t["id"]: t["name"] for t in all_tags.get("results", [])}
        
        return [tag_map.get(tid, "") for tid in tag_ids]
    
    async def search(
        self,
        tenant_id: str,
        query: str,
        page: int = 1,
        page_size: int = 25,
    ) -> DocumentListResponse:
        """Volltextsuche mit Tenant-Isolation"""
        # Suche durchführen
        result = await self.paperless.search(query=query, page=page, page_size=page_size)
        
        # Ergebnisse nach Tenant filtern
        tenant_tag = self._build_tag_name(settings.TAG_PREFIX_TENANT, tenant_id)
        all_tags = await self.paperless.list_tags()
        tenant_tag_id = None
        for t in all_tags.get("results", []):
            if t["name"] == tenant_tag:
                tenant_tag_id = t["id"]
                break
        
        filtered_docs = []
        for doc in result.get("results", []):
            if tenant_tag_id and tenant_tag_id in doc.get("tags", []):
                filtered_docs.append(DocumentResponse(
                    id=doc["id"],
                    paperless_id=doc["id"],
                    title=doc.get("title", ""),
                    filename=doc.get("original_file_name", ""),
                    file_type=doc.get("original_file_name", "").split(".")[-1] if doc.get("original_file_name") else None,
                    size_kb=doc.get("file_size", 0) / 1024 if doc.get("file_size") else None,
                    tenant_id=tenant_id,
                    created_at=doc.get("created"),
                    download_url=f"/api/dms/documents/{doc['id']}/download",
                    thumbnail_url=f"/api/dms/documents/{doc['id']}/thumbnail",
                ))
        
        return DocumentListResponse(
            data=filtered_docs,
            total=len(filtered_docs),
            page=page,
            page_size=page_size,
        )
    
    async def health_check(self) -> bool:
        """Prüfe Paperless-Verbindung"""
        return await self.paperless.health_check()


# Singleton-Instanz
document_service = DocumentService()

