"""
DMS Inbox Endpoints
Zugriff auf eingehende Dokumente aus der Mayan-DMS-Inbox.
Die Einträge werden via Webhook (app/routers/dms_webhook_router.py) persistiert.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Float, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ....core.database import Base, get_db
from ....core.uuid7 import uuid7

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


# ---------------------------------------------------------------------------
# Shared ORM model (extend_existing so webhook router and this file coexist)
# ---------------------------------------------------------------------------

class DmsInboxEntry(Base):
    """Persistierter DMS-Inbox-Eintrag (domain_shared.dms_inbox)."""
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


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ParsedFields(BaseModel):
    invoice_number: Optional[str] = None
    supplier: Optional[str] = None
    date: Optional[str] = None
    total: Optional[str] = None
    supplier_id: Optional[str] = None
    domain: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class InboxDocument(BaseModel):
    id: str
    dms_document_id: int
    dms_url: Optional[str]
    ocr_text: Optional[str]
    parsed_fields: Optional[ParsedFields]
    confidence: float
    status: str


class InboxListResponse(BaseModel):
    ok: bool
    items: List[InboxDocument]
    count: int
    message: Optional[str] = None


class CreateFromInboxResponse(BaseModel):
    ok: bool
    number: Optional[str] = None
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/inbox", response_model=InboxListResponse, tags=["dms"], summary="Inbox abrufen")
async def get_inbox(db: Session = Depends(get_db)):
    """Alle ausstehenden Inbox-Dokumente (status='pending')."""
    try:
        items = (
            db.query(DmsInboxEntry)
            .filter(DmsInboxEntry.status == "pending")
            .order_by(DmsInboxEntry.created_at.desc())
            .all()
        )
        documents = [
            InboxDocument(
                id=entry.id,
                dms_document_id=entry.dms_document_id,
                dms_url=entry.dms_url,
                ocr_text=entry.ocr_text,
                parsed_fields=entry.parsed_fields,
                confidence=entry.confidence or 0.0,
                status=entry.status,
            )
            for entry in items
        ]
        return InboxListResponse(ok=True, items=documents, count=len(documents))
    except Exception as exc:
        logger.error("Failed to load DMS inbox: %s", exc)
        raise HTTPException(status_code=500, detail=f"Inbox konnte nicht geladen werden: {exc}")


@router.post("/inbox/{inbox_id}/create", response_model=CreateFromInboxResponse, tags=["dms"], summary="From inbox anlegen")
async def create_from_inbox(
    inbox_id: str,
    overrides: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db),
):
    """Erstellt einen Beleg aus einem Inbox-Dokument und markiert es als verarbeitet."""
    entry = db.query(DmsInboxEntry).filter(DmsInboxEntry.id == inbox_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox-Dokument nicht gefunden")

    fields = {**(entry.parsed_fields or {}), **overrides}
    beleg_number = fields.get("invoice_number") or fields.get("number")

    entry.status = "processed"
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Failed to commit inbox create for %s: %s", inbox_id, exc)
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {exc}")

    logger.info("Created document from inbox: %s → %s", inbox_id, beleg_number)
    return CreateFromInboxResponse(ok=True, number=beleg_number, message="Beleg erstellt")


@router.delete("/inbox/{inbox_id}", status_code=204, response_class=Response, response_model=None, tags=["dms"], summary="Inbox document löschen")
async def delete_inbox_document(
    inbox_id: str,
    db: Session = Depends(get_db),
):
    """Verwirft/löscht ein Inbox-Dokument."""
    entry = db.query(DmsInboxEntry).filter(DmsInboxEntry.id == inbox_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox-Dokument nicht gefunden")
    try:
        db.delete(entry)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Failed to delete inbox entry %s: %s", inbox_id, exc)
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {exc}")

    logger.info("Deleted inbox document: %s", inbox_id)
    return Response(status_code=204)
