"""WA-AGENT-001 — WhatsApp Webhook + Dev-Simulator Endpoints"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.services.whatsapp_agent_service import (
    get_conversation_state,
    get_order_log,
    process_whatsapp_message,
)

logger = logging.getLogger("whatsapp.webhook")

router = APIRouter()

# ─── Meta-Produktions-Webhook ─────────────────────────────────────────────────

@router.get("/webhook", response_class=PlainTextResponse, tags=["WhatsApp"])
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta Webhook-Verifikation (GET). Wird bei Produktion einmalig aufgerufen."""
    expected = os.environ.get("WHATSAPP_VERIFY_TOKEN", "valeo-wa-dev-token")
    if hub_mode == "subscribe" and hub_verify_token == expected:
        return hub_challenge or ""
    raise HTTPException(status_code=403, detail="Ungültiger Verify-Token")


@router.post("/webhook", status_code=200, tags=["WhatsApp"])
async def webhook_receive(request: Request, x_hub_signature_256: str = Header(None)):
    """
    Produktions-Webhook: empfängt Nachrichten von der Meta-Cloud-API.
    Validiert X-Hub-Signature-256 gegen WHATSAPP_APP_SECRET.
    """
    body = await request.body()

    app_secret = os.environ.get("WHATSAPP_APP_SECRET", "")
    if app_secret:
        expected_sig = (
            "sha256=" + hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
        )
        if not hmac.compare_digest(expected_sig, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Ungültige Signatur")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültiges JSON")

    tenant_id = request.headers.get("X-Tenant-ID", "default")
    _process_meta_payload(payload, tenant_id)
    return {"status": "ok"}


def _process_meta_payload(payload: dict, tenant_id: str) -> None:
    """Extrahiert Nachrichten aus Meta-Webhook-Payload und verarbeitet sie."""
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    if msg.get("type") == "text":
                        phone = msg["from"]
                        text = msg["text"]["body"]
                        logger.info("Meta-WA: Nachricht von %s (tenant=%s)", phone, tenant_id)
                        process_whatsapp_message(tenant_id, phone, text)
    except Exception as exc:
        logger.error("Meta-Payload-Verarbeitung fehlgeschlagen: %s", exc)


# ─── Dev-Simulator ─────────────────────────────────────────────────────────────

class SimulatorRequest(BaseModel):
    phone: str
    message: str
    tenant_id: str = "dev-tenant"


class SimulatorResponse(BaseModel):
    reply: str
    conversation: dict | None
    orders: list[dict]


@router.post(
    "/dev/simulate",
    response_model=SimulatorResponse,
    tags=["WhatsApp Dev-Simulator"],
    summary="Simuliert eine eingehende WhatsApp-Nachricht",
)
async def simulate_message(body: SimulatorRequest) -> SimulatorResponse:
    """
    Test-Endpunkt ohne Meta-Authentifizierung.
    Verarbeitet eine Nachricht und gibt Antwort + Gesprächszustand zurück.
    """
    reply = process_whatsapp_message(body.tenant_id, body.phone, body.message)
    conv = get_conversation_state(body.tenant_id, body.phone)
    orders = get_order_log(body.tenant_id)
    return SimulatorResponse(reply=reply, conversation=conv, orders=orders)


@router.get(
    "/dev/history/{phone}",
    tags=["WhatsApp Dev-Simulator"],
    summary="Gesprächsverlauf für eine Telefonnummer",
)
async def get_history(phone: str, tenant_id: str = "dev-tenant") -> dict:
    conv = get_conversation_state(tenant_id, phone)
    return {"phone": phone, "tenant_id": tenant_id, "conversation": conv}


@router.get(
    "/dev/orders",
    tags=["WhatsApp Dev-Simulator"],
    summary="Alle WhatsApp-Aufträge (In-Memory-Log)",
)
async def get_orders(tenant_id: str = "dev-tenant") -> dict:
    return {"tenant_id": tenant_id, "orders": get_order_log(tenant_id)}


@router.delete(
    "/dev/history/{phone}",
    status_code=204,
    tags=["WhatsApp Dev-Simulator"],
    summary="Gesprächsverlauf zurücksetzen",
)
async def reset_conversation(phone: str, tenant_id: str = "dev-tenant"):
    from app.services.whatsapp_agent_service import _reset_conv
    _reset_conv(tenant_id, phone)
