"""WA-NOTIFY-001 — Ausgehende WhatsApp Push-Benachrichtigungen"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.whatsapp_notify_service import (
    get_outbox,
    send_dokument_ready,
    send_lieferankuendigung,
)

router = APIRouter()


# ─── Request-Schemata ────────────────────────────────────────────────────────

class LieferankuendigungRequest(BaseModel):
    tenant_id: str = "dev-tenant"
    phone: str
    kunden_nr: Optional[str] = None
    kunden_name: Optional[str] = None
    artikel: str
    menge: float
    einheit: str = "t"
    eta_min: int = 60
    fahrer: Optional[str] = None


class DokumentReadyRequest(BaseModel):
    tenant_id: str = "dev-tenant"
    phone: str
    kunden_nr: Optional[str] = None
    kunden_name: Optional[str] = None
    doc_typ: str          # "Lieferschein" | "Rechnung"
    doc_nr: str
    portal_url: Optional[str] = None


class NotifyResponse(BaseModel):
    msg_id: str
    status: str
    text: str


class OutboxMessageResponse(BaseModel):
    msg_id: str
    phone: str
    kunden_nr: Optional[str] = None
    notify_type: str
    text: str
    meta_msg_id: Optional[str] = None
    status: str
    created_at: str


class OutboxLogResponse(BaseModel):
    tenant_id: str
    messages: list[OutboxMessageResponse]


# ─── Endpunkte ───────────────────────────────────────────────────────────────

@router.post(
    "/dev/notify/lieferankuendigung",
    response_model=NotifyResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Simuliert Lieferankündigung (Push an Kunde)",
)
async def simulate_lieferankuendigung(body: LieferankuendigungRequest) -> NotifyResponse:
    """
    Triggerbar aus Disposition/Logistik: LKW ~eta_min Minuten entfernt.
    Im Simulator: Nachricht in Outbox-Log. Mit WHATSAPP_ACCESS_TOKEN: echter Meta-Aufruf.
    """
    return NotifyResponse(**send_lieferankuendigung(
        tenant_id=body.tenant_id,
        phone=body.phone,
        kunden_nr=body.kunden_nr,
        kunden_name=body.kunden_name,
        artikel=body.artikel,
        menge=body.menge,
        einheit=body.einheit,
        eta_min=body.eta_min,
        fahrer=body.fahrer,
    ))


@router.post(
    "/dev/notify/dokument-ready",
    response_model=NotifyResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Simuliert Dokument-Bereitstellungs-Benachrichtigung",
)
async def simulate_dokument_ready(body: DokumentReadyRequest) -> NotifyResponse:
    """
    Triggerbar aus Docflow nach Lieferschein-/Rechnungs-Erstellung.
    """
    return NotifyResponse(**send_dokument_ready(
        tenant_id=body.tenant_id,
        phone=body.phone,
        kunden_nr=body.kunden_nr,
        kunden_name=body.kunden_name,
        doc_typ=body.doc_typ,
        doc_nr=body.doc_nr,
        portal_url=body.portal_url,
    ))


@router.get(
    "/dev/outbox",
    response_model=OutboxLogResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Alle ausgehenden WhatsApp-Nachrichten (Outbox-Log)",
)
async def get_outbox_log(tenant_id: str = "dev-tenant") -> OutboxLogResponse:
    return OutboxLogResponse(tenant_id=tenant_id, messages=get_outbox(tenant_id))
