"""
DMS Webhook Router
Empfängt Webhooks von Mayan-DMS für eingehende Dokumente
"""

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import httpx

from app.integrations.dms_client import get_client, is_configured
from app.integrations.dms_parser import parser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dms", tags=["dms"])


class WebhookPayload(BaseModel):
    """Mayan-Webhook-Payload"""
    event: str  # e.g. "document.created"
    document_id: int
    document_type: Optional[str] = None
    user: Optional[str] = None


class InboxDocument(BaseModel):
    """Dokument in Inbox (Vorschlag zur Erfassung)"""
    id: str
    dms_document_id: int
    dms_url: str
    ocr_text: str
    parsed_fields: Dict[str, Any]
    confidence: float
    status: str = "pending"


# In-Memory Inbox (TODO: durch DB ersetzen)
_INBOX: Dict[str, InboxDocument] = {}


@router.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    """
    Webhook-Handler für Mayan-DMS-Events
    
    Wird aufgerufen wenn:
    - Neues Dokument hochgeladen
    - OCR abgeschlossen
    - Metadaten geändert
    
    Args:
        payload: Webhook-Payload von Mayan
    
    Returns:
        Success-Status
    """
    try:
        logger.info(f"Received DMS webhook: {payload.event} for document {payload.document_id}")
        
        # Nur auf document.created reagieren
        if payload.event == "document.created" or payload.event == "document.ocr.finished":
            await _process_incoming_document(payload.document_id)
        
        return {"ok": True, "message": "Webhook processed"}
    
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_incoming_document(document_id: int):
    """
    Verarbeitet eingehendes Dokument aus DMS
    
    1. Hole OCR-Text aus Mayan
    2. Parse mit DMSParser
    3. Lege in Inbox ab
    """
    if not is_configured():
        logger.warning("DMS not configured, skipping webhook processing")
        return
    
    try:
        # Hole OCR-Text aus Mayan
        with get_client() as client:
            # Get document versions
            response = client.get(f"/api/documents/documents/{document_id}/versions/")
            response.raise_for_status()
            versions = response.json()["results"]
            
            if not versions:
                logger.warning(f"No versions found for document {document_id}")
                return
            
            version_id = versions[0]["id"]
            
            # Get OCR content
            ocr_response = client.get(
                f"/api/documents/documents/{document_id}/versions/{version_id}/ocr_content/"
            )
            ocr_response.raise_for_status()
            ocr_text = ocr_response.text
        
        # Parse OCR-Text
        parse_result = parser.parse(ocr_text)
        
        # Erstelle Inbox-Eintrag
        inbox_doc = InboxDocument(
            id=f"INBOX-{document_id}",
            dms_document_id=document_id,
            dms_url=f"http://localhost:8010/documents/{document_id}/",
            ocr_text=ocr_text[:1000],  # Erste 1000 Zeichen
            parsed_fields=parse_result["fields"],
            confidence=parse_result["confidence"],
            status="pending"
        )
        
        _INBOX[inbox_doc.id] = inbox_doc
        
        logger.info(f"Incoming document processed: {inbox_doc.id}, confidence: {inbox_doc.confidence:.2f}")
    
    except Exception as e:
        logger.error(f"Failed to process incoming document: {e}")


@router.get("/inbox")
async def get_inbox():
    """
    Holt alle Dokumente in Inbox
    
    Returns:
        Liste von Inbox-Dokumenten (Vorschläge zur Erfassung)
    """
    try:
        return {
            "ok": True,
            "items": list(_INBOX.values()),
            "count": len(_INBOX)
        }
    
    except Exception as e:
        logger.error(f"Failed to get inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inbox/{inbox_id}")
async def get_inbox_document(inbox_id: str):
    """
    Holt einzelnes Inbox-Dokument
    
    Args:
        inbox_id: Inbox-ID (z.B. "INBOX-123")
    
    Returns:
        Inbox-Dokument mit parsed_fields
    """
    try:
        if inbox_id not in _INBOX:
            raise HTTPException(status_code=404, detail="Inbox document not found")
        
        return {
            "ok": True,
            "document": _INBOX[inbox_id]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get inbox document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inbox/{inbox_id}/create")
async def create_from_inbox(inbox_id: str, overrides: Dict[str, Any] = Body(...)):
    """
    Erstellt Beleg aus Inbox-Dokument
    
    Args:
        inbox_id: Inbox-ID
        overrides: User-Korrekturen der parsed_fields
    
    Returns:
        Erstellter Beleg
    """
    try:
        if inbox_id not in _INBOX:
            raise HTTPException(status_code=404, detail="Inbox document not found")
        
        inbox_doc = _INBOX[inbox_id]
        
        # Merge parsed_fields + overrides
        fields = {**inbox_doc.parsed_fields, **overrides}
        
        # Erstelle Beleg (TODO: Integration mit document_repository)
        # Für jetzt: Mock-Response
        beleg_number = fields.get("invoice_number", "UNKNOWN")
        
        logger.info(f"Created document from inbox: {inbox_id} → {beleg_number}")
        
        # Markiere als verarbeitet
        inbox_doc.status = "processed"
        
        return {
            "ok": True,
            "number": beleg_number,
            "fields": fields
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create from inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/inbox/{inbox_id}")
async def delete_inbox_document(inbox_id: str):
    """
    Löscht Inbox-Dokument (ablehnen/verwerfen)
    
    Args:
        inbox_id: Inbox-ID
    
    Returns:
        Success-Status
    """
    try:
        if inbox_id in _INBOX:
            del _INBOX[inbox_id]
            logger.info(f"Deleted inbox document: {inbox_id}")
        
        return {"ok": True, "message": "Inbox document deleted"}
    
    except Exception as e:
        logger.error(f"Failed to delete inbox document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

