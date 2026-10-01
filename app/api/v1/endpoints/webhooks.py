"""
Webhook management endpoints (l3c-webhook)
GET/POST/DEL for webhook registrations + event areas.

Duenner Router. Die Logik steht in ``app/services/webhook_service.py`` —
dieselbe, die ``webhook_system.py`` benutzt. Bis zum 01.10.2026 hatte jedes der
beiden Module seine eigene Tabelle, seine eigene Bereichsliste und seine eigene
Vorstellung davon, woher der Mandant kommt; hier kam er aus dem
**Abfrageparameter** ``?tenant_id=`` mit ``DEFAULT_TENANT_ID`` als Rueckfall.
Siehe ``docs/quality-assurance/webhook-mandant-20261001.md``.
"""

import logging
from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, HttpUrl, field_validator
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....core.outbound_security import (
    OutboundTargetPolicyError,
    validate_outbound_http_target,
)
from ....core.tenant import get_tenant_id
from ....services import webhook_service as dienst
from ..schemas.base import BaseSchema, PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()

#: Nur noch Rueckfall fuer Aufrufer dieser Konstante — nicht mehr fuer die
#: Bestimmung des Hauses.
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID

#: Die alten Objektnamen dieses Moduls bleiben als Alias gueltig; das kanonische
#: Vokabular steht im Dienst.
EVENT_AREAS = sorted(dienst.ALIASSE)


def _mandant(kopf_mandant: str, abfrage_mandant: Optional[str]) -> str:
    """Das Haus kommt aus dem Kopf, nicht aus der Abfrage.

    Der Parameter ``tenant_id`` bleibt in der Schnittstelle, weil Aufrufer ihn
    senden — er wird aber **nicht mehr befolgt**: Wer ihn setzte, las und schrieb
    bis zum 01.10.2026 die Webhooks eines fremden Hauses, und ohne ihn traf es
    pauschal ``DEFAULT_TENANT_ID``. Ein abweichender Wert wird protokolliert.
    """
    if abfrage_mandant and abfrage_mandant != kopf_mandant:
        logger.warning(
            "webhooks: tenant_id=%s in der Abfrage weicht vom Kopf (%s) ab und wird ignoriert",
            abfrage_mandant,
            kopf_mandant,
        )
    return kopf_mandant


class WebhookOut(BaseSchema):
    id: str
    url: str
    event_area: str
    is_active: bool = True


class WebhookCreate(BaseModel):
    url: HttpUrl
    event_area: str
    secret: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_webhook_url(cls, v: HttpUrl) -> HttpUrl:
        validate_outbound_http_target(str(v))
        return v


class EventAreaOut(BaseModel):
    name: str
    description: str


@router.get("/", response_model=PaginatedResponse[WebhookOut], summary="Webhooks auflisten")
async def list_webhooks(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    kopf_mandant: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """GET Webhooks"""
    tid = _mandant(kopf_mandant, tenant_id)
    try:
        alle = dienst.auflisten(db, tid)
    except dienst.NichtLesbar as fehler:
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler
    total = len(alle)
    ausschnitt = alle[skip : skip + limit]
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[WebhookOut](
        items=[
            WebhookOut(id=a.id, url=a.url, event_area=a.bereich, is_active=a.is_active)
            for a in ausschnitt
        ],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/areas", response_model=list[EventAreaOut], summary="Event areas auflisten")
async def list_event_areas():
    """GET Bereiche — kanonisches Vokabular, mit den alten Objektnamen als Alias."""
    bereiche = [
        EventAreaOut(name=b, description=f"Ereignis {b}") for b in dienst.BEREICHE
    ]
    bereiche += [
        EventAreaOut(name=alias, description=f"Alias fuer {ziel}")
        for alias, ziel in sorted(dienst.ALIASSE.items())
    ]
    return bereiche


@router.post("/", response_model=WebhookOut, status_code=201, summary="Webhook registrieren")
async def register_webhook(
    payload: WebhookCreate,
    tenant_id: Optional[str] = Query(None),
    kopf_mandant: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """POST Registrieren"""
    tid = _mandant(kopf_mandant, tenant_id)
    try:
        anbindung = dienst.registrieren(
            db,
            tid,
            url=str(payload.url),
            bereich=payload.event_area,
            secret=payload.secret,
        )
    except dienst.UnbekannterBereich as fehler:
        db.rollback()
        raise HTTPException(400, str(fehler)) from fehler
    except OutboundTargetPolicyError as fehler:
        db.rollback()
        raise HTTPException(422, str(fehler)) from fehler
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(503, str(fehler)) from fehler
    return WebhookOut(
        id=anbindung.id,
        url=anbindung.url,
        event_area=anbindung.bereich,
        is_active=anbindung.is_active,
    )


@router.delete("/{webhook_id}", status_code=204, response_class=Response, response_model=None, summary="Webhook entfernen")
async def remove_webhook(
    webhook_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """DEL Entfernen

    Mit Mandantenfilter: Vorher genuegte die Kennung, und die Kennung eines
    fremden Webhooks loeschte dessen Anbindung.
    """
    try:
        dienst.abmelden_nach_kennung(db, tenant_id, webhook_id)
    except dienst.NichtGefunden as fehler:
        db.rollback()
        raise HTTPException(404, str(fehler)) from fehler
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(503, str(fehler)) from fehler
