"""
DMS Webhook Router
Empfängt Webhooks von Mayan-DMS für eingehende Dokumente.
Inbox wird in DB persistiert (domain_shared.dms_inbox).
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, Dict, Any
import logging

from app.core.database import Base, get_db
from app.core.uuid7 import uuid7
from app.integrations.dms_client import get_client, is_configured
from app.integrations.dms_parser import parser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dms", tags=["dms"])


class DmsInboxEntry(Base):
    """Persistierter DMS-Inbox-Eintrag."""
    __tablename__ = "dms_inbox"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    dms_document_id = Column(Integer, nullable=False)
    dms_url = Column(String(500), nullable=True)
    ocr_text = Column(Text, nullable=True)
    parsed_fields = Column(JSONB, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WebhookPayload(BaseModel):
    event: str
    document_id: int
    document_type: Optional[str] = None
    user: Optional[str] = None


@router.post("/webhook")
async def handle_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    """Webhook-Handler für Mayan-DMS-Events."""
    try:
        logger.info("Received DMS webhook: %s for document %s", payload.event, payload.document_id)

        if payload.event in ("document.created", "document.ocr.finished"):
            await _process_incoming_document(payload.document_id, db)

        return {"ok": True, "message": "Webhook processed"}

    except Exception as e:
        logger.error("Webhook processing failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


async def _process_incoming_document(document_id: int, db: Session):
    if not is_configured():
        logger.warning("DMS not configured, skipping webhook processing")
        return

    try:
        with get_client() as client:
            response = client.get(f"/api/documents/documents/{document_id}/versions/")
            response.raise_for_status()
            versions = response.json()["results"]

            if not versions:
                logger.warning("No versions found for document %s", document_id)
                return

            version_id = versions[0]["id"]
            ocr_response = client.get(
                f"/api/documents/documents/{document_id}/versions/{version_id}/ocr_content/"
            )
            ocr_response.raise_for_status()
            ocr_text = ocr_response.text

        parse_result = parser.parse(ocr_text)

        entry = DmsInboxEntry(
            id=f"INBOX-{document_id}",
            dms_document_id=document_id,
            dms_url=f"http://localhost:8010/documents/{document_id}/",
            ocr_text=ocr_text[:2000],
            parsed_fields=parse_result["fields"],
            confidence=parse_result["confidence"],
            status="pending",
        )
        db.merge(entry)
        db.commit()

        logger.info("Incoming document processed: %s, confidence: %.2f", entry.id, entry.confidence)

    except Exception as e:
        logger.error("Failed to process incoming document: %s", e)


@router.get("/inbox")
async def get_inbox(db: Session = Depends(get_db)):
    """Holt alle Inbox-Dokumente."""
    items = db.query(DmsInboxEntry).filter(DmsInboxEntry.status == "pending").all()
    return {
        "ok": True,
        "items": [
            {
                "id": i.id,
                "dms_document_id": i.dms_document_id,
                "dms_url": i.dms_url,
                "ocr_text": i.ocr_text,
                "parsed_fields": i.parsed_fields,
                "confidence": i.confidence,
                "status": i.status,
            }
            for i in items
        ],
        "count": len(items),
    }


@router.get("/inbox/{inbox_id}")
async def get_inbox_document(inbox_id: str, db: Session = Depends(get_db)):
    """Holt einzelnes Inbox-Dokument."""
    entry = db.query(DmsInboxEntry).filter(DmsInboxEntry.id == inbox_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox document not found")
    return {"ok": True, "document": {
        "id": entry.id,
        "dms_document_id": entry.dms_document_id,
        "dms_url": entry.dms_url,
        "ocr_text": entry.ocr_text,
        "parsed_fields": entry.parsed_fields,
        "confidence": entry.confidence,
        "status": entry.status,
    }}


@router.post("/inbox/{inbox_id}/create")
async def create_from_inbox(
    inbox_id: str,
    overrides: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """Erstellt Beleg aus Inbox-Dokument."""
    entry = db.query(DmsInboxEntry).filter(DmsInboxEntry.id == inbox_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox document not found")

    fields = {**(entry.parsed_fields or {}), **overrides}
    beleg_number = fields.get("invoice_number", "UNKNOWN")

    entry.status = "processed"
    db.commit()

    logger.info("Created document from inbox: %s → %s", inbox_id, beleg_number)
    return {"ok": True, "number": beleg_number, "fields": fields}


@router.delete("/inbox/{inbox_id}")
async def delete_inbox_document(inbox_id: str, db: Session = Depends(get_db)):
    """Löscht Inbox-Dokument (ablehnen/verwerfen)."""
    entry = db.query(DmsInboxEntry).filter(DmsInboxEntry.id == inbox_id).first()
    if entry:
        db.delete(entry)
        db.commit()
        logger.info("Deleted inbox document: %s", inbox_id)
    return {"ok": True, "message": "Inbox document deleted"}
