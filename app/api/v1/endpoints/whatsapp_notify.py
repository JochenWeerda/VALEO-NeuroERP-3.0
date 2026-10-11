"""WA-NOTIFY-001 — Ausgehende WhatsApp Push-Benachrichtigungen"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.guards import require_scopes
from app.auth.tenant import get_verified_tenant_id

from app.services.whatsapp_notify_service import (
    get_outbox,
    send_dokument_ready,
    send_lieferankuendigung,
)

router = APIRouter()


# ─── Request-Schemata ────────────────────────────────────────────────────────

class LieferankuendigungRequest(BaseModel):
    tenant_id: Optional[str] = None
    phone: str
    kunden_nr: Optional[str] = None
    kunden_name: Optional[str] = None
    artikel: str
    menge: float
    einheit: str = "t"
    eta_min: int = 60
    fahrer: Optional[str] = None


class DokumentReadyRequest(BaseModel):
    tenant_id: Optional[str] = None
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

def _check_requested_tenant(requested: Optional[str], verified: str) -> None:
    if requested is not None and requested.strip() != verified:
        raise HTTPException(403, "Mandant stimmt nicht mit der geprueften Anmeldung ueberein")

@router.post(
    "/dev/notify/lieferankuendigung",
    response_model=NotifyResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Simuliert Lieferankündigung (Push an Kunde)",
    dependencies=[Depends(require_scopes("crm:write"))],
)
async def simulate_lieferankuendigung(
    body: LieferankuendigungRequest,
    tenant_id: str = Depends(get_verified_tenant_id),
) -> NotifyResponse:
    """
    Triggerbar aus Disposition/Logistik: LKW ~eta_min Minuten entfernt.
    Nur Entwurf in der fluechtigen Outbox; kein automatischer Netzwerkversand.
    """
    _check_requested_tenant(body.tenant_id, tenant_id)
    return NotifyResponse(**send_lieferankuendigung(
        tenant_id=tenant_id,
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
    dependencies=[Depends(require_scopes("crm:write"))],
)
async def simulate_dokument_ready(
    body: DokumentReadyRequest,
    tenant_id: str = Depends(get_verified_tenant_id),
) -> NotifyResponse:
    """
    Triggerbar aus Docflow nach Lieferschein-/Rechnungs-Erstellung.
    """
    _check_requested_tenant(body.tenant_id, tenant_id)
    return NotifyResponse(**send_dokument_ready(
        tenant_id=tenant_id,
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
    dependencies=[Depends(require_scopes("crm:read"))],
)
async def get_outbox_log(
    tenant_id: Optional[str] = None,
    active_tenant: str = Depends(get_verified_tenant_id),
) -> OutboxLogResponse:
    _check_requested_tenant(tenant_id, active_tenant)
    return OutboxLogResponse(tenant_id=active_tenant, messages=get_outbox(active_tenant))
