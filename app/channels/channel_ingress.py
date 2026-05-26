"""
Channel Ingress Router — NC-H4
Einheitlicher Eingang fuer alle Kanaele (WhatsApp, E-Mail, Chat, Voice).
Routet eingehende Nachrichten ueber die Neuro-Core Pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ChannelType(str, Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    CHAT = "chat"
    VOICE = "voice"
    API = "api"


@dataclass
class ChannelMessage:
    channel: ChannelType
    sender_id: str
    text: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    tenant_id: str = "system"
    reply_to: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "channel": self.channel.value,
            "sender_id": self.sender_id,
            "text": self.text,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "tenant_id": self.tenant_id,
        }


@dataclass
class ChannelResponse:
    channel: ChannelType
    recipient_id: str
    text: str
    pipeline_result: Optional[dict] = None
    message_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        return {
            "channel": self.channel.value,
            "recipient_id": self.recipient_id,
            "text": self.text,
            "message_id": self.message_id,
            "has_pipeline_result": self.pipeline_result is not None,
        }


async def route_message(
    message: ChannelMessage,
    db=None,
) -> ChannelResponse:
    logger.info(
        "Channel ingress: %s from %s (%d chars)",
        message.channel.value, message.sender_id, len(message.text),
    )

    if db:
        try:
            from app.middleware.neuro_audit_middleware import record_channel_event
            record_channel_event(
                db=db,
                tenant_id=message.tenant_id,
                channel=message.channel.value,
                event_type="incoming",
                payload=message.to_dict(),
            )
        except Exception:  # noqa: BLE001 — Audit-Log fehlgeschlagen; Verarbeitung wird fortgesetzt
            pass

    try:
        from app.services.guardrails import check_input
        guard_result = check_input(message.text)
        if guard_result.action.value == "block":
            return ChannelResponse(
                channel=message.channel,
                recipient_id=message.sender_id,
                text="Ihre Nachricht konnte nicht verarbeitet werden.",
            )
    except Exception:  # noqa: BLE001 — Fehler-Antwort an Nutzer konnte nicht gesendet werden; wird ignoriert
        pass

    try:
        from app.agents.neuro_pipeline import run_pipeline
        result = run_pipeline(
            user_input=message.text,
            context={
                "channel": message.channel.value,
                "sender_id": message.sender_id,
                "tenant_id": message.tenant_id,
                **message.metadata,
            },
            tenant_id=message.tenant_id,
            db=db,
        )
    except Exception as exc:
        logger.error("Pipeline error for channel %s: %s", message.channel.value, exc)
        result = {"status": "error", "message": str(exc)}

    response_text = _format_response(result, message.channel)

    if db:
        try:
            from app.middleware.neuro_audit_middleware import record_pipeline_audit
            record_pipeline_audit(
                db=db,
                tenant_id=message.tenant_id,
                pipeline_result=result,
                user_id=message.sender_id,
                channel=message.channel.value,
            )
        except Exception:  # noqa: BLE001 — Audit-Log fehlgeschlagen; Verarbeitung wird fortgesetzt
            pass

    return ChannelResponse(
        channel=message.channel,
        recipient_id=message.sender_id,
        text=response_text,
        pipeline_result=result,
    )


def _format_response(result: dict, channel: ChannelType) -> str:
    status = result.get("status", "unknown")
    intent = result.get("intent", {})

    if status == "low_confidence":
        return "Ich konnte Ihre Anfrage nicht eindeutig zuordnen. Bitte praezisieren Sie Ihr Anliegen."

    if status == "error":
        return f"Bei der Verarbeitung ist ein Fehler aufgetreten: {result.get('message', 'Unbekannt')}"

    if status == "blocked":
        return "Ihre Nachricht konnte nicht verarbeitet werden."

    intent_name = intent.get("intent", "unknown")
    plan = result.get("plan", {})
    step_count = plan.get("step_count", 0) if plan else 0

    if channel == ChannelType.WHATSAPP:
        if status == "awaiting_approval":
            return f"Aktion '{intent_name}' erkannt ({step_count} Schritte). Freigabe erforderlich — bitte im System bestaetigen."
        return f"Verstanden: {intent_name} ({step_count} Schritte). Wird verarbeitet."

    if status == "awaiting_approval":
        return f"Intent: {intent_name}. Plan mit {step_count} Schritten generiert. Manuelle Freigabe erforderlich."
    if status == "executed":
        return f"Intent: {intent_name}. {step_count} Schritte erfolgreich ausgefuehrt."
    if status == "rejected":
        return f"Intent: {intent_name}. Plan wurde von der Verification Engine abgelehnt."

    return f"Verarbeitet: {intent_name} (Status: {status})"
