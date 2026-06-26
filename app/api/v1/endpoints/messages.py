"""
Internal messaging endpoints (l3c-nachricht)
GET/POST for internal messages + health check.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import InternalMessage
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class MessageOut(BaseSchema):
    id: str
    sender_id: str
    recipient_id: str
    subject: str
    body: Optional[str] = None
    is_read: bool = False


class MessageCreate(BaseModel):
    sender_id: str
    recipient_id: str
    subject: str
    body: Optional[str] = None


@router.get("/", response_model=PaginatedResponse[MessageOut], summary="Messages auflisten")
async def list_messages(
    recipient_id: Optional[str] = Query(None),
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Nachrichten ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
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


@router.post("/", response_model=MessageOut, status_code=201, summary="Message senden")
async def send_message(
    payload: MessageCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Nachricht"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    msg = InternalMessage(
        id=uuid7(),
        sender_id=payload.sender_id,
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
