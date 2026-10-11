"""
WA-NOTIFY-001 — Ausgehende WhatsApp-Benachrichtigungen

Bereitet Nachrichten fuer WhatsApp Web / Computer Use vor:
  - Lieferankündigung: "LKW kommt in ~60 min" (getriggert von Logistik-Event)
  - Dokument-Ready: "Lieferschein/Rechnung verfügbar" mit Portal-Link

Kein automatischer Netzwerkversand. pending_browser ist ein Entwurf,
kein Versand-/Zustellnachweis. Die Outbox ist noch fluechtig; dauerhafte
Auftraege und verifizierte Browserkonten sind vor Betriebsfreigabe erforderlich.

Outbox-Schema: { tenant_id: [OutboxMessage] }
"""
from __future__ import annotations

import logging
import os
import uuid
from copy import deepcopy
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
    meta_msg_id: Optional[str] = None   # bestehendes Antwortfeld; kein Meta-Versand
    status: str = "pending_browser"
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

def _require_tenant(tenant_id: str) -> None:
    """Kein globaler Entwurfsspeicher bei fehlendem Fachkontext.

    Die Mitgliedschaft muss der Aufrufer pruefen; dies validiert nur den Wert.
    """
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("Mandant muss angegeben werden")


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
    """Nur vorbereiten; echte Zustellung benoetigt den autorisierten Browserweg."""
    _require_tenant(msg.tenant_id)
    msg.status = "pending_browser"
    msg.meta_msg_id = None
    _store_outbox(msg, msg.tenant_id)
    logger.info("WA-Notify fuer Browserversand vorbereitet")
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
    Bereitet Lieferankuendigung fuer Browserversand vor.
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
    Bereitet Nachricht vor, wenn Lieferschein oder Rechnung im Portal verfuegbar ist.
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
    _require_tenant(tenant_id)
    return deepcopy(list(reversed(_OUTBOX.get(tenant_id, []))))
