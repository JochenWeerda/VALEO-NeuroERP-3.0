"""
DMS Inbox Endpoints
Zugriff auf eingehende Dokumente aus der Mayan-DMS-Inbox.
Die Einträge werden via Webhook (app/routers/dms_webhook_router.py) persistiert.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.auth.finance_roles import beleg_read
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.documents.dms_inbox_model import DmsInboxEntry, booking_not_from_inbox, verified_inbox_tenant


router = APIRouter()


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

@router.get("/inbox", response_model=InboxListResponse, tags=["dms"], summary="Inbox abrufen", dependencies=[Depends(beleg_read)])
async def get_inbox(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    """Alle ausstehenden Inbox-Dokumente (status='pending')."""
    mandant = verified_inbox_tenant(tenant_id)
    try:
        items = (
            db.query(DmsInboxEntry)
            .filter(DmsInboxEntry.tenant_id == mandant, DmsInboxEntry.status == "pending")
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
    except Exception as exc:  # noqa: BLE001 — Tabelle fehlt oder DB nicht erreichbar
        logger.warning("DMS inbox nicht verfügbar: %s", exc)
        db.rollback()
        return InboxListResponse(ok=True, items=[], count=0, message="DMS-Inbox nicht verfügbar")


@router.post("/inbox/{inbox_id}/create", response_model=CreateFromInboxResponse, tags=["dms"], summary="From inbox anlegen", dependencies=SCHREIBEN["BELEGE"])
async def create_from_inbox(
    inbox_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """OCR-Prefill is not a Beleg; submit the purchase invoice domain command."""
    mandant = verified_inbox_tenant(tenant_id)
    entry = db.query(DmsInboxEntry).filter(
        DmsInboxEntry.id == inbox_id, DmsInboxEntry.tenant_id == mandant
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox-Dokument nicht gefunden")
    raise booking_not_from_inbox(inbox_id)


@router.delete("/inbox/{inbox_id}", status_code=204, response_class=Response, response_model=None, tags=["dms"], summary="Inbox document löschen", dependencies=SCHREIBEN["BELEGE"])
async def delete_inbox_document(
    inbox_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Verwirft/löscht ein Inbox-Dokument."""
    mandant = verified_inbox_tenant(tenant_id)
    entry = db.query(DmsInboxEntry).filter(
        DmsInboxEntry.id == inbox_id, DmsInboxEntry.tenant_id == mandant
    ).first()
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
