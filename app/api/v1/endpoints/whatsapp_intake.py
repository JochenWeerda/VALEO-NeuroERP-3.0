"""WhatsApp Bestell-Inbox — eingehende Freitext-Bestellungen erfassen & bestätigen."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.whatsapp_intake_service import WhatsAppIntakeService

router = APIRouter(prefix="/crm/bestell-inbox", tags=["crm", "bestell-inbox"])


class IntakeIn(BaseModel):
    raw_text: str
    absender: Optional[str] = None
    quelle: str = "whatsapp"


class BestaetigenIn(BaseModel):
    kunden_nr: Optional[str] = None
    beleg_typ: str = "auftrag"  # angebot|auftrag|lieferschein|rechnung
    parsed: Optional[dict] = None


@router.post("", response_model=dict[str, Any], summary="Bestellnachricht erfassen & per AI extrahieren")
def create(body: IntakeIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    if not body.raw_text.strip():
        raise HTTPException(status_code=422, detail="raw_text darf nicht leer sein")
    return WhatsAppIntakeService(db, tenant_id).create_inbox(body.raw_text, body.absender, body.quelle)


@router.get("", response_model=dict[str, Any], summary="Posteingang auflisten")
def list_inbox(
    status: Optional[str] = Query(None, description="neu|geparst|bestaetigt|verworfen"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return WhatsAppIntakeService(db, tenant_id).list_inbox(status)


@router.get("/{inbox_id}", response_model=dict[str, Any], summary="Eintrag abrufen")
def get_one(inbox_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    item = WhatsAppIntakeService(db, tenant_id).get(inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return item


@router.post("/{inbox_id}/bestaetigen", response_model=dict[str, Any], summary="Bestätigen → Kontakt + Beleg-Vorbelegung")
def bestaetigen(
    inbox_id: str,
    body: BestaetigenIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    item = WhatsAppIntakeService(db, tenant_id).bestaetigen(inbox_id, body.kunden_nr, body.beleg_typ, body.parsed)
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return item


@router.post("/{inbox_id}/verwerfen", response_model=dict[str, Any], summary="Verwerfen")
def verwerfen(inbox_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return WhatsAppIntakeService(db, tenant_id).verwerfen(inbox_id)
