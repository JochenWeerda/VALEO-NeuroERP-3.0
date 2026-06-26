"""
WA-NOTIFY-001 — Ausgehende WhatsApp-Benachrichtigungen

Sendet Push-Nachrichten an Kunden:
  - Lieferankündigung: "LKW kommt in ~60 min" (getriggert von Logistik-Event)
  - Dokument-Ready: "Lieferschein/Rechnung verfügbar" mit Portal-Link

In Produktion: Meta Cloud API (POST messages).
Im Simulator: In-Memory-Outbox + REST-Trigger.

Outbox-Schema: { tenant_id: [OutboxMessage] }
"""
from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger("whatsapp.notify")

# ─── In-Memory-Outbox (Simulator) ────────────────────────────────────────────
_OUTBOX: dict[str, list[dict]] = {}  # { tenant_id: [msg] }


class NotifyType(str, Enum):
    LIEFERANKUENDIGUNG = "lieferankuendigung"
    DOKUMENT_READY = "dokument_ready"
    AUFTRAG_BESTAETIGUNG = "auftrag_bestaetigung"  # Rückkanal aus WA-AGENT


@dataclass
class OutboxMessage:
    msg_id: str
    tenant_id: str
    phone: str
    kunden_nr: Optional[str]
    notify_type: NotifyType
    text: str
    meta_msg_id: Optional[str] = None   # gefüllt nach echtem API-Aufruf
    status: str = "pending"             # pending | sent | failed | simulated
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ─── Text-Templates ──────────────────────────────────────────────────────────

def _text_lieferankuendigung(
    kunden_name: Optional[str],
    artikel: str,
    menge: float,
    einheit: str,
    eta_min: int = 60,
    fahrer: Optional[str] = None,
) -> str:
    name_part = f" {kunden_name}" if kunden_name else ""
    fahrer_part = f" (Fahrer: {fahrer})" if fahrer else ""
    return (
        f"Hallo{name_part}! 🚛 Ihr Lieferwagen{fahrer_part} ist in ca. {eta_min} Minuten "
        f"bei Ihnen — {menge} {einheit} {artikel}. "
        f"Bitte Zufahrt freihalten. Bei Fragen: 0800-VALEO."
    )


def _text_dokument_ready(
    kunden_name: Optional[str],
    doc_typ: str,              # "Lieferschein" | "Rechnung"
    doc_nr: str,
    portal_url: Optional[str] = None,
) -> str:
    name_part = f" {kunden_name}" if kunden_name else ""
    portal = portal_url or os.environ.get("PORTAL_BASE_URL", "https://portal.valeo-erp.de")
    link = f"{portal}/portal/dokumente/{doc_nr}"
    typ_emoji = "📦" if doc_typ == "Lieferschein" else "🧾"
    return (
        f"Hallo{name_part}! {typ_emoji} Ihr {doc_typ} {doc_nr} steht im Portal bereit: "
        f"{link}"
    )


# ─── Sende-Logik ─────────────────────────────────────────────────────────────

def _send_via_meta(phone: str, text: str, tenant_id: str) -> Optional[str]:
    """
    Sendet Nachricht über Meta Cloud API.
    Gibt Meta-Nachrichten-ID zurück oder None bei Fehler.
    Nur aktiv wenn WHATSAPP_PHONE_NUMBER_ID + WHATSAPP_ACCESS_TOKEN gesetzt.
    """
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
    if not phone_number_id or not access_token:
        return None
    try:
        import httpx
        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": phone.lstrip("+"),
            "type": "text",
            "text": {"body": text},
        }
        resp = httpx.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("messages", [{}])[0].get("id")
    except Exception as exc:
        logger.error("Meta API Sende-Fehler für %s: %s", phone, exc)
        return None


def _store_outbox(msg: OutboxMessage, tenant_id: str) -> None:
    _OUTBOX.setdefault(tenant_id, []).append({
        "msg_id": msg.msg_id,
        "phone": msg.phone,
        "kunden_nr": msg.kunden_nr,
        "notify_type": msg.notify_type,
        "text": msg.text,
        "meta_msg_id": msg.meta_msg_id,
        "status": msg.status,
        "created_at": msg.created_at,
    })


def _deliver(msg: OutboxMessage) -> OutboxMessage:
    """Versucht Zustellung via Meta; Fallback: simuliert."""
    meta_id = _send_via_meta(msg.phone, msg.text, msg.tenant_id)
    if meta_id:
        msg.meta_msg_id = meta_id
        msg.status = "sent"
        logger.info("WA-Notify gesendet: %s → %s (%s)", msg.notify_type, msg.phone, meta_id)
    else:
        msg.status = "simulated"
        logger.info("WA-Notify simuliert: %s → %s", msg.notify_type, msg.phone)
    _store_outbox(msg, msg.tenant_id)
    return msg


# ─── Öffentliche API ──────────────────────────────────────────────────────────

def send_lieferankuendigung(
    tenant_id: str,
    phone: str,
    kunden_nr: Optional[str],
    kunden_name: Optional[str],
    artikel: str,
    menge: float,
    einheit: str,
    eta_min: int = 60,
    fahrer: Optional[str] = None,
) -> dict:
    """
    Sendet Lieferankündigung an Kunden.
    Wird von Logistik-/Disposition-Service aufgerufen wenn LKW ~eta_min Minuten entfernt.
    """
    text = _text_lieferankuendigung(kunden_name, artikel, menge, einheit, eta_min, fahrer)
    msg = OutboxMessage(
        msg_id=f"NOTIFY-{uuid.uuid4().hex[:8].upper()}",
        tenant_id=tenant_id,
        phone=phone,
        kunden_nr=kunden_nr,
        notify_type=NotifyType.LIEFERANKUENDIGUNG,
        text=text,
    )
    _deliver(msg)
    return {"msg_id": msg.msg_id, "status": msg.status, "text": text}


def send_dokument_ready(
    tenant_id: str,
    phone: str,
    kunden_nr: Optional[str],
    kunden_name: Optional[str],
    doc_typ: str,
    doc_nr: str,
    portal_url: Optional[str] = None,
) -> dict:
    """
    Benachrichtigt Kunden wenn Lieferschein oder Rechnung im Portal verfügbar ist.
    Wird von Docflow-Service aufgerufen nach Dokumentenerstellung.
    """
    text = _text_dokument_ready(kunden_name, doc_typ, doc_nr, portal_url)
    msg = OutboxMessage(
        msg_id=f"NOTIFY-{uuid.uuid4().hex[:8].upper()}",
        tenant_id=tenant_id,
        phone=phone,
        kunden_nr=kunden_nr,
        notify_type=NotifyType.DOKUMENT_READY,
        text=text,
    )
    _deliver(msg)
    return {"msg_id": msg.msg_id, "status": msg.status, "text": text}


def get_outbox(tenant_id: str) -> list[dict]:
    return list(reversed(_OUTBOX.get(tenant_id, [])))
