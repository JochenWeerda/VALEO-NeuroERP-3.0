"""
WhatsApp Business API Adapter — NC-H1
Webhook-Empfang, Message-Parsing, Reply-Versand.
Integriert Consent Engine (NC-004) und Guardrails (NC-C).
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class WhatsAppMessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    LOCATION = "location"
    INTERACTIVE = "interactive"
    REACTION = "reaction"
    UNKNOWN = "unknown"


@dataclass
class WhatsAppIncoming:
    message_id: str
    from_number: str
    timestamp: str
    message_type: WhatsAppMessageType
    text: str = ""
    media_url: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "from_number": self.from_number,
            "timestamp": self.timestamp,
            "message_type": self.message_type.value,
            "text": self.text,
            "media_url": self.media_url,
            "metadata": self.metadata,
        }


@dataclass
class WhatsAppOutgoing:
    to_number: str
    text: str
    reply_to: Optional[str] = None
    template_name: Optional[str] = None
    template_params: dict[str, str] = field(default_factory=dict)


def parse_webhook(payload: dict) -> list[WhatsAppIncoming]:
    messages: list[WhatsAppIncoming] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                msg_type = msg.get("type", "unknown")
                text = ""
                media_url = None

                if msg_type == "text":
                    text = msg.get("text", {}).get("body", "")
                elif msg_type in ("image", "document"):
                    media_url = msg.get(msg_type, {}).get("id")
                    text = msg.get(msg_type, {}).get("caption", "")
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    if interactive.get("type") == "button_reply":
                        text = interactive.get("button_reply", {}).get("title", "")
                    elif interactive.get("type") == "list_reply":
                        text = interactive.get("list_reply", {}).get("title", "")

                try:
                    wa_type = WhatsAppMessageType(msg_type)
                except ValueError:
                    wa_type = WhatsAppMessageType.UNKNOWN

                messages.append(WhatsAppIncoming(
                    message_id=msg.get("id", str(uuid4())),
                    from_number=msg.get("from", ""),
                    timestamp=msg.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    message_type=wa_type,
                    text=text,
                    media_url=media_url,
                    metadata={
                        "profile_name": value.get("contacts", [{}])[0].get("profile", {}).get("name", ""),
                        "phone_number_id": value.get("metadata", {}).get("phone_number_id", ""),
                    },
                ))

    return messages


def verify_webhook_signature(payload_bytes: bytes, signature: str, app_secret: str) -> bool:
    expected = hmac.new(
        app_secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def build_text_reply(to_number: str, text: str, reply_to: Optional[str] = None) -> dict:
    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }
    if reply_to:
        body["context"] = {"message_id": reply_to}
    return body


def build_template_reply(to_number: str, template_name: str, language: str = "de", params: Optional[dict] = None) -> dict:
    components = []
    if params:
        body_params = [{"type": "text", "text": v} for v in params.values()]
        components.append({"type": "body", "parameters": body_params})

    return {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": components,
        },
    }


async def process_incoming(
    incoming: WhatsAppIncoming,
    tenant_id: str = "system",
    db=None,
) -> dict:
    if db:
        try:
            from app.services.consent_engine import check_consent
            has_consent = check_consent(db, incoming.from_number, "whatsapp_communication", tenant_id)
            if not has_consent:
                logger.info("No WhatsApp consent for %s — skipping pipeline", incoming.from_number)
                return {
                    "status": "no_consent",
                    "message": "Kein Consent fuer WhatsApp-Kommunikation vorhanden.",
                }
        except Exception:
            pass

    try:
        from app.services.guardrails import check_input
        guard_result = check_input(incoming.text)
        if guard_result.action.value == "block":
            logger.warning("WhatsApp message blocked by guardrails: %s", incoming.from_number)
            return {"status": "blocked", "message": "Nachricht durch Guardrails blockiert."}
    except Exception:
        pass

    try:
        from app.agents.neuro_pipeline import run_pipeline
        result = run_pipeline(
            user_input=incoming.text,
            context={
                "channel": "whatsapp",
                "from_number": incoming.from_number,
                "message_type": incoming.message_type.value,
                "tenant_id": tenant_id,
            },
            tenant_id=tenant_id,
            db=db,
        )
        return result
    except Exception as exc:
        logger.error("WhatsApp pipeline error: %s", exc)
        return {"status": "error", "message": str(exc)}
