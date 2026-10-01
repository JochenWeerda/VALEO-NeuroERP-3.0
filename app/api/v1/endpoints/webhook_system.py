"""
Outbound Webhook Registration
Analog externe Agrar-ERP-Plattform Webhook-Modul

Duenner Router. Die Anbindungen liegen in
``domain_shared.webhook_registrations``, die Zustellversuche in
``domain_shared.webhook_deliveries``, und die ganze Logik in
``app/services/webhook_service.py`` — dieselbe, die ``webhooks.py`` benutzt.
Bis zum 01.10.2026 hatten beide Module ihre eigene Tabelle, ihre eigene
Bereichsliste und ihre eigene Vorstellung davon, woher der Mandant kommt.
Siehe ``docs/quality-assurance/webhook-mandant-20261001.md``.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.outbound_security import OutboundTargetPolicyError
from ....core.tenant import get_tenant_id
from ....services import webhook_service as dienst

from app.api.v1.schemas.base import BaseSchema


router = APIRouter()
logger = logging.getLogger(__name__)

#: Weiterhin unter dem alten Namen erreichbar, damit Aufrufer nichts aendern
#: muessen; die Wahrheit steht im Dienst.
SIGNATUR_KOPF = dienst.SIGNATUR_KOPF
VALID_BEREICHE = dienst.BEREICHE

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class WebhookCreate(BaseModel):
    url: str
    bereich: str
    beschreibung: Optional[str] = None
    secret: Optional[str] = None
    is_active: bool = True

    @field_validator("url")
    @classmethod
    def url_must_be_https(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("URL muss mit https:// beginnen")
        return v

    @field_validator("bereich")
    @classmethod
    def bereich_must_be_valid(cls, v: str) -> str:
        return dienst.kanonischer_bereich(v)


class WebhookOut(BaseModel):
    id: str
    nr: int
    url: str
    bereich: str
    beschreibung: Optional[str] = None
    is_active: bool
    erstellt_am: Optional[str] = None
    letzte_auslosung_am: Optional[str] = None
    fehler_count: int = 0
    #: Ob ein Geheimnis hinterlegt ist — **nicht** das Geheimnis selbst.
    signiert: bool = False


class ZustellversuchOut(BaseSchema):
    versucht_am: Optional[str] = None
    erfolgreich: bool
    status_code: Optional[int] = None
    dauer_ms: Optional[int] = None
    fehler: Optional[str] = None


def _hinaus(anbindung: dienst.Anbindung, beschreibung: Optional[str] = None) -> WebhookOut:
    return WebhookOut(
        id=anbindung.id,
        nr=anbindung.nr,
        url=anbindung.url,
        bereich=anbindung.bereich,
        beschreibung=beschreibung,
        is_active=anbindung.is_active,
        erstellt_am=anbindung.erstellt_am,
        letzte_auslosung_am=anbindung.letzte_auslosung_am,
        fehler_count=anbindung.fehler_count,
        signiert=anbindung.signiert,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=list[WebhookOut], tags=["webhooks"], summary="Webhooks auflisten")
def list_webhooks(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[WebhookOut]:
    """Die Webhooks des eigenen Hauses."""
    try:
        return [_hinaus(a) for a in dienst.auflisten(db, tenant_id)]
    except dienst.NichtLesbar as fehler:
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler


@router.get("/bereiche", response_model=list[str], tags=["webhooks"], summary="Bereiche auflisten")
def list_bereiche() -> list[str]:
    """Das kanonische Bereichsvokabular."""
    return dienst.BEREICHE


@router.post("/bereiche/{bereich}", response_model=WebhookOut, status_code=201, tags=["webhooks"], summary="Webhook registrieren")
def register_webhook(
    bereich: str,
    payload: WebhookCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> WebhookOut:
    """Register a new outbound webhook for a given event area."""
    try:
        # Der Bereich kommt aus dem Pfad; der Rumpf darf ihn nicht widersprechen.
        kanonisch = dienst.kanonischer_bereich(bereich)
    except dienst.UnbekannterBereich as fehler:
        raise HTTPException(status_code=422, detail=str(fehler)) from fehler
    if not payload.url.startswith("https://"):
        raise HTTPException(status_code=422, detail="URL muss mit https:// beginnen")

    try:
        anbindung = dienst.registrieren(
            db,
            tenant_id,
            url=payload.url,
            bereich=kanonisch,
            secret=payload.secret,
            is_active=payload.is_active,
        )
    except OutboundTargetPolicyError as fehler:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(fehler)) from fehler
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler
    return _hinaus(anbindung, payload.beschreibung)


@router.get("/{webhook_id}/zustellversuche", response_model=list[ZustellversuchOut], tags=["webhooks"], summary="Zustellversuche abrufen")
def list_zustellversuche(
    webhook_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[ZustellversuchOut]:
    """Die letzten Zustellversuche einer Anbindung des eigenen Hauses.

    Der Nachweis zu ``fehler_count`` und ``letzte_auslosung_am``: Beide Felder
    waren vorher Behauptungen ohne Beleg.
    """
    try:
        return [ZustellversuchOut(**z) for z in dienst.zustellversuche(db, tenant_id, webhook_id)]
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler


@router.delete("/abmelden/{nr}", status_code=204, response_class=Response, tags=["webhooks"], response_model=None, summary="Webhook abmelden")
def unregister_webhook(
    nr: int,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    """Meldet den Webhook mit dieser laufenden Nummer im eigenen Haus ab.

    Der Weg hiess vorher ``DELETE /webhooks/{nr}`` und war **unerreichbar**:
    Unter demselben Prefix haengt ``webhooks.py`` mit ``DELETE /{webhook_id}``
    und ist zuerst eingebunden, also traf jede Abmeldung dort eine Kennung, die
    keine laufende Nummer ist.
    """
    try:
        dienst.abmelden_nach_nummer(db, tenant_id, nr)
    except dienst.NichtGefunden as fehler:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(fehler)) from fehler
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Internal helper (not exposed as endpoint)
# ---------------------------------------------------------------------------

async def _trigger_webhook(
    bereich: str,
    payload: dict,
    db: Session,
    tenant_id: str,
) -> None:
    """Weiterleitung auf ``webhook_service.trigger`` — alter Aufrufname."""
    await dienst.trigger(db, tenant_id, bereich, payload)
