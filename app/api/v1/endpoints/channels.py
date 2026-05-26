"""Channel Endpoints — NC-H1/H2/H4: WhatsApp Webhook, Email Ingress, Channel Router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/channels", tags=["neuro-core", "channels"])


class WhatsAppWebhookVerify(BaseModel):
    hub_mode: Optional[str] = Field(None, alias="hub.mode")
    hub_verify_token: Optional[str] = Field(None, alias="hub.verify_token")
    hub_challenge: Optional[str] = Field(None, alias="hub.challenge")


class EmailIngressRequest(BaseModel):
    from_address: str
    to_address: str = "system@valeo-erp.de"
    subject: str
    body_text: str
    body_html: Optional[str] = None
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None


class GenericMessageRequest(BaseModel):
    channel: str = Field(..., description="whatsapp | email | chat | voice | api")
    sender_id: str
    text: str
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


@router.get("/whatsapp/webhook")
async def whatsapp_verify(request: Request):
    """WhatsApp Webhook Verification (GET)."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    verify_token = settings.CHANNEL_WHATSAPP_VERIFY_TOKEN or "valeo_whatsapp_verify_2026"
    if mode == "subscribe" and token == verify_token:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """WhatsApp Business API Webhook (POST)."""
    payload = await request.json()

    from app.channels.whatsapp_adapter import parse_webhook, process_incoming

    messages = parse_webhook(payload)
    results = []
    for msg in messages:
        result = await process_incoming(msg, tenant_id, db)
        results.append({
            "message_id": msg.message_id,
            "from": msg.from_number,
            "result": result,
        })

    return {"processed": len(results), "results": results}


@router.post("/email/ingest")
async def email_ingest(
    request: EmailIngressRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """E-Mail Ingress Endpoint."""
    from app.channels.email_channel import parse_incoming, process_incoming

    email = parse_incoming(
        raw_from=request.from_address,
        raw_to=request.to_address,
        subject=request.subject,
        body_text=request.body_text,
        body_html=request.body_html,
        message_id=request.message_id,
        in_reply_to=request.in_reply_to,
    )
    result = await process_incoming(email, tenant_id, db)
    return {"email": email.to_dict(), "result": result}


@router.post("/route")
async def route_generic(
    request: GenericMessageRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Generischer Channel Ingress — routet jede Nachricht ueber die Pipeline."""
    from app.channels.channel_ingress import ChannelMessage, ChannelType, route_message

    try:
        channel_type = ChannelType(request.channel)
    except ValueError:
        channel_type = ChannelType.API

    message = ChannelMessage(
        channel=channel_type,
        sender_id=request.sender_id,
        text=request.text,
        metadata=request.metadata or {},
        tenant_id=tenant_id,
    )
    response = await route_message(message, db)
    return response.to_dict()


# ── Live-Chat (NC-12) ──────────────────────────────────────────

class ChatStartRequest(BaseModel):
    user_id: str = Field(...)
    context: Optional[dict[str, Any]] = None


class ChatMessageRequest(BaseModel):
    text: str = Field(...)
    user_id: str = Field("")


@router.post("/livechat/start")
async def livechat_start(
    request: ChatStartRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Neue Live-Chat-Session starten."""
    from app.channels.livechat_channel import create_session
    session = create_session(request.user_id, tenant_id, request.context)
    return session.to_dict()


@router.post("/livechat/{session_id}/message")
async def livechat_message(
    session_id: str,
    request: ChatMessageRequest,
):
    """Nachricht an eine Live-Chat-Session senden."""
    from app.channels.livechat_channel import process_chat_message
    result = process_chat_message(session_id, request.text, request.user_id)
    return result


@router.get("/livechat/{session_id}/history")
async def livechat_history(session_id: str, limit: int = 50):
    """Chat-Historie einer Session abrufen."""
    from app.channels.livechat_channel import get_history
    messages = get_history(session_id, limit)
    return {"count": len(messages), "messages": [m.to_dict() for m in messages]}


@router.post("/livechat/{session_id}/close")
async def livechat_close(session_id: str):
    """Live-Chat-Session schliessen."""
    from app.channels.livechat_channel import close_session
    session = close_session(session_id)
    if not session:
        return {"error": "Session nicht gefunden"}
    return session.to_dict()


@router.get("/livechat/sessions")
async def livechat_sessions(tenant_id: str = Depends(get_tenant_id)):
    """Aktive Chat-Sessions auflisten."""
    from app.channels.livechat_channel import list_active_sessions
    sessions = list_active_sessions(tenant_id)
    return {"count": len(sessions), "sessions": [s.to_dict() for s in sessions]}
