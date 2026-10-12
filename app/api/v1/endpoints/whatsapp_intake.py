"""WhatsApp Bestell-Inbox — eingehende Freitext-Bestellungen erfassen & bestätigen."""

from __future__ import annotations

from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.v1.schemas.crm_channel_bundle_schemas import WhatsAppInboxOut
from app.core.database import get_db
from app.auth.deps_oidc import get_current_user
from app.auth.guards import require_scopes
from app.auth.tenant import get_verified_tenant_id
from app.services.whatsapp_intake_service import WhatsAppIntakeService, WhatsAppReferenceError

router = APIRouter(prefix="/crm/bestell-inbox", tags=["crm", "bestell-inbox"])


class IntakeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_text: str
    absender: Optional[str] = None
    quelle: str = "whatsapp"


class BestaetigenIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kunden_nr: Optional[str] = None
    beleg_typ: Literal["angebot", "auftrag", "lieferschein", "rechnung"] = "auftrag"
    parsed: Optional[dict] = None


@router.post("", response_model=WhatsAppInboxOut, summary="Bestellnachricht erfassen & per AI extrahieren", dependencies=[Depends(require_scopes("crm:write"))])
def create(body: IntakeIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)) -> dict[str, Any]:
    if not body.raw_text.strip():
        raise HTTPException(status_code=422, detail="raw_text darf nicht leer sein")
    try:
        return WhatsAppIntakeService(db, tenant_id).create_inbox(body.raw_text, body.absender, body.quelle)
    except WhatsAppReferenceError as exc:
        raise HTTPException(status_code=422, detail="Bestellpositionen muessen geprueft werden") from exc


@router.get("", response_model=list[WhatsAppInboxOut], summary="Posteingang auflisten", dependencies=[Depends(require_scopes("crm:read"))])
def list_inbox(
    status: Optional[str] = Query(None, description="neu|geparst|bestaetigt|verworfen"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_verified_tenant_id),
) -> list[dict[str, Any]]:
    return WhatsAppIntakeService(db, tenant_id).list_inbox(status)


@router.get("/{inbox_id}", response_model=WhatsAppInboxOut, summary="Eintrag abrufen", dependencies=[Depends(require_scopes("crm:read"))])
def get_one(inbox_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)) -> dict[str, Any]:
    item = WhatsAppIntakeService(db, tenant_id).get(inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return item


@router.post("/{inbox_id}/bestaetigen", response_model=WhatsAppInboxOut, summary="Bestätigen → Kontakt + Beleg-Vorbelegung", dependencies=[Depends(require_scopes("crm:write"))])
def bestaetigen(
    inbox_id: str,
    body: BestaetigenIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_verified_tenant_id),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    actor = user.get("sub")
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 120:
        raise HTTPException(status_code=403, detail="Gepruefter Urheber erforderlich")
    try:
        item = WhatsAppIntakeService(db, tenant_id).bestaetigen(inbox_id, body.kunden_nr, body.beleg_typ, body.parsed, actor=actor)
    except WhatsAppReferenceError as exc:
        raise HTTPException(status_code=422, detail="Kunden- oder Artikelreferenz im Mandanten nicht eindeutig verfuegbar") from exc
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return item


@router.post("/{inbox_id}/verwerfen", response_model=WhatsAppInboxOut, summary="Verwerfen", dependencies=[Depends(require_scopes("crm:write"))])
def verwerfen(inbox_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)) -> dict[str, Any]:
    item = WhatsAppIntakeService(db, tenant_id).verwerfen(inbox_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return item
