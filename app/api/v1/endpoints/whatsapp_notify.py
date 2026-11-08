"""WA-NOTIFY-001 — Ausgehende WhatsApp Push-Benachrichtigungen"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.deps_oidc import get_current_user

from app.auth.guards import require_scopes
from app.auth.tenant import get_verified_tenant_id

from app.services.whatsapp_notify_service import (
    get_outbox,
    send_dokument_ready,
    send_lieferankuendigung,
    WhatsAppReplayConflict,
)

router = APIRouter()


# ─── Request-Schemata ────────────────────────────────────────────────────────

class LieferankuendigungRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=120, pattern=r"\S")
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
    idempotency_key: str = Field(min_length=1, max_length=120, pattern=r"\S")
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


def _verified_actor(user: dict) -> str:
    actor = user.get("sub")
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 120:
        raise HTTPException(403, "Gueltiger Urheber aus der Anmeldung erforderlich")
    return actor

@router.post(
    "/dev/notify/lieferankuendigung",
    response_model=NotifyResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Simuliert Lieferankündigung (Push an Kunde)",
    dependencies=[Depends(require_scopes("crm:write"))],
)
def simulate_lieferankuendigung(
    body: LieferankuendigungRequest,
    tenant_id: str = Depends(get_verified_tenant_id),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotifyResponse:
    """
    Triggerbar aus Disposition/Logistik: LKW ~eta_min Minuten entfernt.
    Dauerhafter Vorbereitungsauftrag; kein automatischer Netzwerkversand.
    """
    _check_requested_tenant(body.tenant_id, tenant_id)
    try:
        result = send_lieferankuendigung(
            tenant_id=tenant_id,
            phone=body.phone,
            kunden_nr=body.kunden_nr,
            kunden_name=body.kunden_name,
            artikel=body.artikel,
            menge=body.menge,
            einheit=body.einheit,
            eta_min=body.eta_min,
            fahrer=body.fahrer,
            db=db, actor=_verified_actor(user), idempotency_key=body.idempotency_key,
        )
        db.commit()
    except WhatsAppReplayConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    return NotifyResponse(**result)


@router.post(
    "/dev/notify/dokument-ready",
    response_model=NotifyResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Simuliert Dokument-Bereitstellungs-Benachrichtigung",
    dependencies=[Depends(require_scopes("crm:write"))],
)
def simulate_dokument_ready(
    body: DokumentReadyRequest,
    tenant_id: str = Depends(get_verified_tenant_id),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotifyResponse:
    """
    Triggerbar aus Docflow nach Lieferschein-/Rechnungs-Erstellung.
    """
    _check_requested_tenant(body.tenant_id, tenant_id)
    try:
        result = send_dokument_ready(
            tenant_id=tenant_id,
            phone=body.phone,
            kunden_nr=body.kunden_nr,
            kunden_name=body.kunden_name,
            doc_typ=body.doc_typ,
            doc_nr=body.doc_nr,
            portal_url=body.portal_url,
            db=db, actor=_verified_actor(user), idempotency_key=body.idempotency_key,
        )
        db.commit()
    except WhatsAppReplayConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    return NotifyResponse(**result)


@router.get(
    "/dev/outbox",
    response_model=OutboxLogResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Alle ausgehenden WhatsApp-Nachrichten (Outbox-Log)",
    dependencies=[Depends(require_scopes("crm:read"))],
)
def get_outbox_log(
    tenant_id: Optional[str] = None,
    active_tenant: str = Depends(get_verified_tenant_id),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> OutboxLogResponse:
    _check_requested_tenant(tenant_id, active_tenant)
    return OutboxLogResponse(tenant_id=active_tenant, messages=get_outbox(active_tenant, db=db, limit=limit))
