"""
Live-Chat / Web-Chat Channel — NC-12
WebSocket-basierter Echtzeit-Chat fuer die Web-Oberflaeche.
Ergaenzt WhatsApp und Email als dritter Eingangskanal.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ChatMessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"
    TYPING = "typing"
    FILE = "file"
    ACTION = "action"


@dataclass
class ChatMessage:
    message_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    sender_type: str = "user"
    sender_id: str = ""
    message_type: ChatMessageType = ChatMessageType.TEXT
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class ChatSession:
    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    tenant_id: str = "system"
    status: str = "active"
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    messages: list[ChatMessage] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def message_count(self) -> int:
        return len(self.messages)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "status": self.status,
            "started_at": self.started_at,
            "message_count": self.message_count,
        }


_SESSIONS: dict[str, ChatSession] = {}


def create_session(user_id: str, tenant_id: str = "system", context: Optional[dict] = None) -> ChatSession:
    session = ChatSession(user_id=user_id, tenant_id=tenant_id, context=context or {})
    _SESSIONS[session.session_id] = session
    logger.info("Chat-Session %s erstellt fuer User %s", session.session_id, user_id)
    return session


def get_session(session_id: str) -> Optional[ChatSession]:
    return _SESSIONS.get(session_id)


def close_session(session_id: str) -> Optional[ChatSession]:
    session = _SESSIONS.get(session_id)
    if session:
        session.status = "closed"
    return session


def add_message(session_id: str, message: ChatMessage) -> Optional[ChatMessage]:
    session = _SESSIONS.get(session_id)
    if not session or session.status != "active":
        return None
    message.session_id = session_id
    session.messages.append(message)
    return message


def get_history(session_id: str, limit: int = 50) -> list[ChatMessage]:
    session = _SESSIONS.get(session_id)
    if not session:
        return []
    return session.messages[-limit:]


def process_chat_message(session_id: str, user_text: str, user_id: str = "") -> dict[str, Any]:
    """
    Verarbeitet eine Chat-Nachricht: Guardrails -> Pipeline -> Antwort.
    """
    session = _SESSIONS.get(session_id)
    if not session:
        return {"error": "Session nicht gefunden", "session_id": session_id}

    user_msg = ChatMessage(
        session_id=session_id,
        sender_type="user",
        sender_id=user_id or session.user_id,
        content=user_text,
    )
    session.messages.append(user_msg)

    try:
        from app.services.guardrails import check_input
        guard_result = check_input(user_text)
        if guard_result.get("blocked"):
            system_msg = ChatMessage(
                session_id=session_id,
                sender_type="system",
                message_type=ChatMessageType.SYSTEM,
                content="Nachricht wurde durch Sicherheitsrichtlinien blockiert.",
                metadata={"blocked_reason": guard_result.get("reason", "policy")},
            )
            session.messages.append(system_msg)
            return {"status": "blocked", "message": system_msg.to_dict()}
    except Exception:
        pass

    pipeline_result = {}
    try:
        from app.agents.neuro_pipeline import run_pipeline
        pipeline_result = run_pipeline(
            user_input=user_text,
            context={
                "channel": "livechat",
                "session_id": session_id,
                "user_id": user_id or session.user_id,
                "tenant_id": session.tenant_id,
                "message_count": session.message_count,
            },
            tenant_id=session.tenant_id,
        )
    except Exception as exc:
        logger.warning("Pipeline-Aufruf fuer Live-Chat fehlgeschlagen: %s", exc)
        pipeline_result = {"status": "error", "message": str(exc)}

    response_text = _format_response(pipeline_result)
    bot_msg = ChatMessage(
        session_id=session_id,
        sender_type="bot",
        sender_id="neuro-core",
        content=response_text,
        metadata={"pipeline_status": pipeline_result.get("status", "unknown")},
    )
    session.messages.append(bot_msg)

    return {
        "status": "ok",
        "user_message": user_msg.to_dict(),
        "bot_response": bot_msg.to_dict(),
        "pipeline_result": pipeline_result,
    }


def _format_response(result: dict[str, Any]) -> str:
    if result.get("status") == "error":
        return f"Entschuldigung, ein Fehler ist aufgetreten: {result.get('message', 'Unbekannt')}"

    intent = result.get("intent", {})
    plan = result.get("plan", {})

    if isinstance(intent, dict) and intent.get("intent"):
        intent_name = intent["intent"]
        confidence = intent.get("confidence_score", 0)
        explanation = intent.get("explanation", "")
        steps = plan.get("steps", []) if isinstance(plan, dict) else []

        parts = [explanation] if explanation else [f"Erkannter Intent: {intent_name} (Konfidenz: {confidence:.0%})"]
        if steps:
            parts.append(f"Plan mit {len(steps)} Schritt(en) erstellt.")
        return " ".join(parts)

    return result.get("message", "Anfrage wurde verarbeitet.")


def list_active_sessions(tenant_id: Optional[str] = None) -> list[ChatSession]:
    sessions = [s for s in _SESSIONS.values() if s.status == "active"]
    if tenant_id:
        sessions = [s for s in sessions if s.tenant_id == tenant_id]
    return sessions
