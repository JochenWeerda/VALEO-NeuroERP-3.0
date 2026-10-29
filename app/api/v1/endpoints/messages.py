"""
Internal messaging endpoints (l3c-nachricht)
GET/POST for internal messages + health check.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.akteur import bekannter_nutzer, gepruefter_akteur_aus_request
from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....infrastructure.models import InternalMessage
from ..schemas.base import PaginatedResponse, BaseSchema
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router = APIRouter()
# Mandant aus der geprueften Anmeldung (get_tenant_id). Bis 27.10.2026 kam er aus ?tenant_id=
# mit dem Standardmandanten als Rueckfall.


class MessageOut(BaseSchema):
    id: str
    sender_id: str
    recipient_id: str
    subject: str
    body: Optional[str] = None
    is_read: bool = False


class MessageCreate(BaseModel):
    # Absender kommt aus der geprueften Anmeldung; bis 27.10.2026 stand er frei im Rumpf.
    recipient_id: str
    subject: str
    body: Optional[str] = None


@router.get("/", response_model=PaginatedResponse[MessageOut], summary="Messages auflisten")
async def list_messages(
    recipient_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Nachrichten ermitteln"""
    tid = tenant_id
    q = db.query(InternalMessage).filter(InternalMessage.tenant_id == tid)
    if recipient_id:
        q = q.filter(InternalMessage.recipient_id == recipient_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[MessageOut](
        items=[MessageOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/", response_model=MessageOut, status_code=201, summary="Message senden", dependencies=SCHREIBEN["CRM"])
async def send_message(
    request: Request,
    payload: MessageCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """POST Nachricht"""
    from app.core.uuid7 import uuid7
    tid = tenant_id
    sender_id = bekannter_nutzer(db, gepruefter_akteur_aus_request(request), tenant_id=tid)
    msg = InternalMessage(
        id=uuid7(),
        sender_id=sender_id,
        recipient_id=payload.recipient_id,
        subject=payload.subject,
        body=payload.body,
        tenant_id=tid,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return MessageOut.model_validate(msg)


@router.get("/health", summary="Health messages",
    response_model=dict[str, str]
)
async def messages_health():
    """GET Health"""
    return {"status": "ok", "service": "messages"}
