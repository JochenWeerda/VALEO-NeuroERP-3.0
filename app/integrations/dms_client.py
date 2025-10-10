"""
Mayan-DMS Client
Adapter für VALEO-NeuroERP → Mayan-DMS-Integration
"""

import httpx
import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Config-Pfad
CONFIG_PATH = Path("data/config/dms.json")

# Lade Config (falls vorhanden)
_cfg = {}
if CONFIG_PATH.exists():
    try:
        _cfg = json.loads(CONFIG_PATH.read_text())
    except Exception as e:
        logger.warning(f"Failed to load DMS config: {e}")

# DMS-Connection (ENV-Override möglich)
DMS_BASE = os.environ.get("DMS_BASE") or _cfg.get("base") or "http://localhost:8010"
DMS_TOKEN = os.environ.get("DMS_TOKEN") or ""  # Token nie in Config speichern!


def get_client() -> httpx.Client:
    """
    Erstellt DMS-Client mit gespeicherter/ENV-Konfiguration
    
    Returns:
        httpx.Client für Mayan-API
    """
    if not DMS_TOKEN:
        raise ValueError("DMS_TOKEN not configured. Set via ENV or admin UI.")
    
    return httpx.Client(
        base_url=DMS_BASE,
        headers={"Authorization": f"Token {DMS_TOKEN}"},
        timeout=15.0
    )


def upload_document(
    domain: str,
    doc_number: str,
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Lädt Dokument zu Mayan-DMS hoch
    
    Args:
        domain: Belegtyp (z.B. "sales_order")
        doc_number: Belegnummer
        file_path: Pfad zur Datei (PDF)
        metadata: Optional metadata (customerId, status, etc.)
    
    Returns:
        Response mit document_id
    """
    try:
        # Hole Document-Type-ID aus Config
        if not CONFIG_PATH.exists():
            raise ValueError("DMS not configured. Run bootstrap first.")
        
        config = json.loads(CONFIG_PATH.read_text())
        doc_types = config.get("document_types", {})
        
        if domain not in doc_types:
            raise ValueError(f"Document type not found: {domain}")
        
        doc_type_id = doc_types[domain]
        
        with get_client() as client:
            # Upload file
            with open(file_path, "rb") as f:
                files = {"file": f}
                data = {"document_type_id": doc_type_id}
                
                response = client.post("/api/documents/documents/", files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                document_id = result["id"]
                
                # Set metadata (falls vorhanden)
                if metadata:
                    meta_ids = config.get("metadata_types", {})
                    
                    for key, value in metadata.items():
                        if key in meta_ids:
                            meta_id = meta_ids[key]
                            client.post(
                                f"/api/documents/documents/{document_id}/metadata/",
                                json={
                                    "metadata_type_id": meta_id,
                                    "value": str(value)
                                }
                            )
                
                logger.info(f"Uploaded document to DMS: {doc_number} → ID {document_id}")
                
                return {
                    "ok": True,
                    "document_id": document_id,
                    "url": f"{DMS_BASE}/documents/{document_id}/"
                }
    
    except Exception as e:
        logger.error(f"Failed to upload document to DMS: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


def get_document_url(document_id: int) -> str:
    """
    Generiert URL zu Dokument in Mayan-DMS
    
    Args:
        document_id: Mayan-Document-ID
    
    Returns:
        URL zum Dokument
    """
    return f"{DMS_BASE}/documents/{document_id}/"


def is_configured() -> bool:
    """
    Prüft, ob DMS konfiguriert ist
    
    Returns:
        True wenn DMS-Config vorhanden
    """
    return CONFIG_PATH.exists() and bool(DMS_TOKEN)

