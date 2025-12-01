"""
Paperless-ngx API Client

Kommunikation mit dem Paperless-ngx Backend via REST API.
"""
import httpx
from typing import Optional, List, Dict, Any, BinaryIO
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PaperlessClient:
    """Client für Paperless-ngx REST API"""
    
    def __init__(self):
        self.base_url = settings.PAPERLESS_URL.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.headers = {
            "Authorization": f"Token {settings.PAPERLESS_TOKEN}",
            "Accept": "application/json",
        }
        self.timeout = settings.PAPERLESS_TIMEOUT
    
    def _get_client(self) -> httpx.AsyncClient:
        """Create async HTTP client"""
        return httpx.AsyncClient(
            base_url=self.api_url,
            headers=self.headers,
            timeout=self.timeout
        )
    
    # ==================== Documents ====================
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def list_documents(
        self,
        query: Optional[str] = None,
        tags: Optional[List[int]] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """Liste Dokumente mit optionaler Filterung"""
        params = {
            "page": page,
            "page_size": page_size,
        }
        if query:
            params["query"] = query
        if tags:
            params["tags__id__in"] = ",".join(str(t) for t in tags)
        
        async with self._get_client() as client:
            response = await client.get("/documents/", params=params)
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_document(self, document_id: int) -> Dict[str, Any]:
        """Einzelnes Dokument abrufen"""
        async with self._get_client() as client:
            response = await client.get(f"/documents/{document_id}/")
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        title: Optional[str] = None,
        tags: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Dokument hochladen"""
        files = {"document": (filename, file)}
        data = {}
        if title:
            data["title"] = title
        if tags:
            data["tags"] = tags
        
        async with self._get_client() as client:
            response = await client.post(
                "/documents/post_document/",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def update_document(
        self,
        document_id: int,
        title: Optional[str] = None,
        tags: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Dokument-Metadaten aktualisieren"""
        data = {}
        if title is not None:
            data["title"] = title
        if tags is not None:
            data["tags"] = tags
        
        async with self._get_client() as client:
            response = await client.patch(f"/documents/{document_id}/", json=data)
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def delete_document(self, document_id: int) -> bool:
        """Dokument löschen"""
        async with self._get_client() as client:
            response = await client.delete(f"/documents/{document_id}/")
            response.raise_for_status()
            return True
    
    async def download_document(self, document_id: int) -> bytes:
        """Dokument herunterladen"""
        async with self._get_client() as client:
            response = await client.get(f"/documents/{document_id}/download/")
            response.raise_for_status()
            return response.content
    
    async def get_thumbnail(self, document_id: int) -> bytes:
        """Dokument-Thumbnail abrufen"""
        async with self._get_client() as client:
            response = await client.get(f"/documents/{document_id}/thumb/")
            response.raise_for_status()
            return response.content
    
    # ==================== Tags ====================
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def list_tags(self) -> Dict[str, Any]:
        """Alle Tags abrufen"""
        async with self._get_client() as client:
            response = await client.get("/tags/")
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_tag(self, name: str, color: Optional[str] = None) -> Dict[str, Any]:
        """Tag erstellen"""
        data = {"name": name}
        if color:
            data["color"] = color
        
        async with self._get_client() as client:
            response = await client.post("/tags/", json=data)
            response.raise_for_status()
            return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_or_create_tag(self, name: str) -> int:
        """Tag abrufen oder erstellen, gibt Tag-ID zurück"""
        tags_response = await self.list_tags()
        
        for tag in tags_response.get("results", []):
            if tag["name"] == name:
                return tag["id"]
        
        # Tag existiert nicht, erstellen
        new_tag = await self.create_tag(name)
        return new_tag["id"]
    
    # ==================== Search ====================
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search(self, query: str, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
        """Volltextsuche in Dokumenten"""
        params = {
            "query": query,
            "page": page,
            "page_size": page_size,
        }
        
        async with self._get_client() as client:
            response = await client.get("/documents/", params=params)
            response.raise_for_status()
            return response.json()
    
    # ==================== Health ====================
    
    async def health_check(self) -> bool:
        """Prüfe ob Paperless erreichbar ist und API-Token gültig ist"""
        try:
            async with self._get_client() as client:
                # Verwende /documents/ Endpoint - gibt 200 bei gültigem Token
                response = await client.get("/documents/", params={"page_size": 1})
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Paperless health check failed: {e}")
            return False


# Singleton-Instanz
paperless_client = PaperlessClient()

