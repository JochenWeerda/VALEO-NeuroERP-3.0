"""KIM-AUTOCAPTURE — automatische Kontakt-Erfassung (Telefon/E-Mail/WhatsApp).

Eigener Router (prefix /crm/kim), separat von crm_kim.py. Wird von TAPI-Bridge
(Anrufende mit Transkript), Mail-Connector und WhatsApp-Intake aufgerufen, um
Kommunikation automatisch als Kontakt zu protokollieren.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_auto_capture_service import CrmAutoCaptureService

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


class AutoCaptureIn(BaseModel):
    channel: str                       # telefon | email | whatsapp | persoenlich | brief | fax
    direction: str = "incoming"        # incoming | outgoing
    peer: Optional[str] = None         # Telefonnummer oder E-Mail der Gegenseite
    content: str = ""                  # Transkript / Mailtext / WhatsApp-Text
    kundenNr: Optional[str] = None     # falls bekannt (überspringt Auflösung)
    betreff: Optional[str] = None      # optionaler fester Betreff (sonst LLM)
    verweis: Optional[str] = None      # externe Referenz (Call-/Message-ID) für Idempotenz
    bediener: Optional[str] = None     # Default 'AUTO'


@router.post("/auto-capture", response_model=dict, summary="Kontakt automatisch erfassen (Telefon/E-Mail/WhatsApp)")
def auto_capture(
    body: AutoCaptureIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmAutoCaptureService(db, tenant_id).capture(
        channel=body.channel,
        direction=body.direction,
        peer=body.peer,
        content=body.content,
        kunden_nr=body.kundenNr,
        betreff=body.betreff,
        verweis=body.verweis,
        bediener=body.bediener or "AUTO",
    )
