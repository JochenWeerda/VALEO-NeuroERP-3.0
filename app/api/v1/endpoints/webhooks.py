"""
Webhook management endpoints (l3c-webhook)
GET/POST/DEL for webhook registrations + event areas.
"""

import ipaddress
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, HttpUrl, field_validator
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import WebhookRegistration
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID

# Pre-defined event areas matching L3-Connect
EVENT_AREAS = [
    "auftrag", "bestellung", "kunde", "artikel",
    "lieferschein", "rechnung", "inventur", "lager",
    "pickliste", "wiegeschein", "nve", "stammdaten",
]


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
    def validate_webhook_url(cls, v):
        parsed = urlparse(str(v))
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Nur HTTP/HTTPS URLs erlaubt")
        hostname = parsed.hostname or ""
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise ValueError("Interne/Private IP-Adressen nicht erlaubt")
        except ValueError as exc:
            if hostname.replace(".", "").isdigit() or ":" in hostname:
                raise exc
            # hostname is a domain, not IP — check for localhost
            if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
                raise ValueError("Localhost nicht erlaubt als Webhook-Ziel")
        return v


class EventAreaOut(BaseModel):
    name: str
    description: str


@router.get("/", response_model=PaginatedResponse[WebhookOut])
async def list_webhooks(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Webhooks"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(WebhookRegistration).filter(WebhookRegistration.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[WebhookOut](
        items=[WebhookOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.get("/areas", response_model=list[EventAreaOut])
async def list_event_areas():
    """GET Bereiche"""
    return [EventAreaOut(name=a, description=f"Events for {a}") for a in EVENT_AREAS]


@router.post("/", response_model=WebhookOut, status_code=201)
async def register_webhook(
    payload: WebhookCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Registrieren"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    if payload.event_area not in EVENT_AREAS:
        raise HTTPException(400, f"Unknown event area: {payload.event_area}")
    obj = WebhookRegistration(
        id=uuid7(),
        url=str(payload.url),
        event_area=payload.event_area,
        secret=payload.secret,
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return WebhookOut.model_validate(obj)


@router.delete("/{webhook_id}", status_code=204)
async def remove_webhook(webhook_id: str, db: Session = Depends(get_db)):
    """DEL Entfernen"""
    obj = db.query(WebhookRegistration).filter(WebhookRegistration.id == webhook_id).first()
    if not obj:
        raise HTTPException(404, "Webhook not found")
    db.delete(obj)
    db.commit()
