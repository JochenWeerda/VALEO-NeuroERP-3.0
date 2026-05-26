"""
Email Channel — NC-H2
IMAP-Polling/Webhook fuer eingehende E-Mails, Response via SMTP.
Integriert Guardrails (NC-C) und Neuro-Core Pipeline (NC-A).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class IncomingEmail:
    message_id: str
    from_address: str
    to_address: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
    received_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    priority: EmailPriority = EmailPriority.NORMAL
    attachments: list[dict] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)
    in_reply_to: Optional[str] = None
    thread_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "subject": self.subject,
            "body_text": self.body_text[:500],
            "received_at": self.received_at,
            "priority": self.priority.value,
            "attachment_count": len(self.attachments),
            "in_reply_to": self.in_reply_to,
            "thread_id": self.thread_id,
        }


@dataclass
class OutgoingEmail:
    to_address: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
    in_reply_to: Optional[str] = None
    cc: list[str] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)


PRIORITY_KEYWORDS = {
    EmailPriority.URGENT: ["dringend", "sofort", "urgent", "notfall", "kritisch"],
    EmailPriority.HIGH: ["wichtig", "eilig", "prioritaet", "asap", "schnellstmoeglich"],
}


def detect_priority(subject: str, body: str) -> EmailPriority:
    combined = f"{subject} {body}".lower()
    for prio, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return prio
    return EmailPriority.NORMAL


def extract_intent_text(email: IncomingEmail) -> str:
    """Extrahiert den relevanten Text fuer die Intent Engine."""
    text = email.body_text.strip()
    lines = text.split("\n")
    relevant = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">") or stripped.startswith("---") or stripped.startswith("Von:"):
            break
        if stripped:
            relevant.append(stripped)

    result = " ".join(relevant[:10])
    if email.subject and email.subject.lower() not in result.lower():
        result = f"{email.subject}: {result}"

    return result[:500]


def parse_incoming(
    raw_from: str,
    raw_to: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    message_id: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    headers: Optional[dict] = None,
) -> IncomingEmail:
    email = IncomingEmail(
        message_id=message_id or str(uuid4()),
        from_address=raw_from,
        to_address=raw_to,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        priority=detect_priority(subject, body_text),
        in_reply_to=in_reply_to,
        headers=headers or {},
    )

    if in_reply_to:
        email.thread_id = in_reply_to.split("@")[0] if "@" in in_reply_to else in_reply_to

    return email


async def process_incoming(
    email: IncomingEmail,
    tenant_id: str = "system",
    db=None,
) -> dict:
    try:
        from app.services.guardrails import check_input
        guard_result = check_input(email.body_text)
        if guard_result.action.value == "block":
            logger.warning("Email blocked by guardrails: %s", email.from_address)
            return {"status": "blocked", "message": "E-Mail durch Guardrails blockiert."}
    except Exception:  # noqa: BLE001 — Guardrail-Check fehlgeschlagen; Verarbeitung wird fortgesetzt
        pass

    intent_text = extract_intent_text(email)

    try:
        from app.agents.neuro_pipeline import run_pipeline
        result = run_pipeline(
            user_input=intent_text,
            context={
                "channel": "email",
                "from_address": email.from_address,
                "subject": email.subject,
                "priority": email.priority.value,
                "thread_id": email.thread_id,
                "tenant_id": tenant_id,
            },
            tenant_id=tenant_id,
            db=db,
        )
        return result
    except Exception as exc:
        logger.error("Email pipeline error: %s", exc)
        return {"status": "error", "message": str(exc)}


def build_reply(
    original: IncomingEmail,
    response_text: str,
    pipeline_result: Optional[dict] = None,
) -> OutgoingEmail:
    subject = original.subject
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    return OutgoingEmail(
        to_address=original.from_address,
        subject=subject,
        body_text=response_text,
        in_reply_to=original.message_id,
    )
