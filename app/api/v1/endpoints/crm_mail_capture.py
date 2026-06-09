"""KIM E-Mail-Connector — ein-/ausgehende Mails als Kontakt erfassen.

Zwei Eingangswege auf denselben Endpoint:
  1. Geparste Felder (fromAddr/toAddr/subject/text/messageId/direction) — so liefern
     es OSS-Webhooks wie IMAP-API (ewildgoose/imap-api), MXHook oder ein eigener
     Poller (tools/mail-connector/mail_connector.py).
  2. Rohe RFC822-Mail im Feld `raw` — wird hier per stdlib `email` geparst.

Daraus wird `peer` (Gegenseite) und `direction` abgeleitet und an den
universellen Auto-Capture (channel='email') übergeben. Idempotenz über die
Message-ID (`verweis`). Nicht zuordenbare Mails landen in der Klärfall-Inbox.
"""

from __future__ import annotations

from email import message_from_string
from email.utils import getaddresses, parseaddr
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_auto_capture_service import CrmAutoCaptureService

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


class MailCaptureIn(BaseModel):
    raw: Optional[str] = None              # vollständige RFC822-Mail (alternativ zu Einzelfeldern)
    fromAddr: Optional[str] = None
    toAddr: Optional[str] = None
    subject: Optional[str] = None
    text: Optional[str] = None
    messageId: Optional[str] = None        # → verweis (Idempotenz)
    direction: Optional[str] = None        # incoming | outgoing (falls bekannt)
    ownAddresses: list[str] = []           # eigene Postfach-Adressen → Richtungserkennung
    kundenNr: Optional[str] = None


def _plain_text(msg) -> str:
    """Extrahiert den Klartext-Body aus einer email.message.Message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(
                part.get("Content-Disposition", "")
            ):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8", "replace")
        return ""
    payload = msg.get_payload(decode=True)
    if payload:
        return payload.decode(msg.get_content_charset() or "utf-8", "replace")
    return str(msg.get_payload() or "")


def _parse_raw(raw: str) -> dict:
    msg = message_from_string(raw)
    return {
        "from": parseaddr(msg.get("From", ""))[1],
        "to": [a for _, a in getaddresses(msg.get_all("To", []))],
        "subject": str(msg.get("Subject", "")),
        "text": _plain_text(msg),
        "message_id": (msg.get("Message-ID", "") or "").strip("<>") or None,
    }


def _resolve_direction(declared: Optional[str], from_addr: str, own: list[str]) -> tuple[str, str]:
    """Liefert (direction_for_capture, peer). Eigene Adresse als Absender ⇒ ausgehend."""
    own_lc = {a.strip().lower() for a in own if a}
    if declared:
        direction = "outgoing" if declared.lower().startswith("out") else "incoming"
    elif from_addr and from_addr.lower() in own_lc:
        direction = "outgoing"
    else:
        direction = "incoming"
    return direction, from_addr


@router.post("/mail-capture", summary="E-Mail als Kontakt erfassen (geparst oder roh)")
def mail_capture(
    body: MailCaptureIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    if body.raw:
        parsed = _parse_raw(body.raw)
        from_addr = parsed["from"]
        to_list = parsed["to"]
        subject = parsed["subject"] or body.subject
        content = parsed["text"]
        message_id = parsed["message_id"] or body.messageId
    else:
        from_addr = (body.fromAddr or "").strip()
        to_list = [body.toAddr] if body.toAddr else []
        subject = body.subject
        content = body.text or ""
        message_id = body.messageId

    direction, from_peer = _resolve_direction(body.direction, from_addr, body.ownAddresses)
    # Gegenseite = Absender bei eingehend, erster Empfänger bei ausgehend.
    peer = from_peer if direction == "incoming" else (to_list[0] if to_list else from_peer)

    body_text = (subject or "")
    if content:
        body_text = f"{subject}\n\n{content}" if subject else content

    return CrmAutoCaptureService(db, tenant_id).capture(
        channel="email",
        direction=direction,
        peer=peer,
        content=body_text,
        kunden_nr=body.kundenNr,
        betreff=subject or None,
        verweis=message_id,
        bediener="AUTO",
    )
