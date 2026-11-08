"""
WA-NOTIFY-001 — Ausgehende WhatsApp-Benachrichtigungen

Bereitet Nachrichten fuer WhatsApp Web / Computer Use vor:
  - Lieferankündigung: "LKW kommt in ~60 min" (getriggert von Logistik-Event)
  - Dokument-Ready: "Lieferschein/Rechnung verfügbar" mit Portal-Link

Kein automatischer Netzwerkversand. pending_browser ist ein dauerhafter Auftrag
in der bestehenden Kanaltabelle, kein Versand-/Zustellnachweis. Der Aufrufer
committet Auftrag und Audit gemeinsam; es gibt keinen Memoryfallback.

Outbox-Schema: { tenant_id: [OutboxMessage] }
"""
from __future__ import annotations

import logging
import hashlib
import json
import os
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

logger = logging.getLogger("whatsapp.notify")

# ─── Persistente Benachrichtigungsauftraege ───────────────────────────────────
_PROCESS = "whatsapp.browser.notification.v1"


class WhatsAppReplayConflict(ValueError):
    """Ein bestehender Auftrag darf nicht mit anderem Inhalt/Urheber ersetzt werden."""


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


def _message_payload(msg: OutboxMessage) -> dict:
    return {
        "msg_id": msg.msg_id,
        "phone": msg.phone,
        "kunden_nr": msg.kunden_nr,
        "notify_type": msg.notify_type,
        "text": msg.text,
        "meta_msg_id": msg.meta_msg_id,
        "status": msg.status,
        "created_at": msg.created_at,
    }


def _persist_message(msg: OutboxMessage, db: Session, actor: str, key: str) -> OutboxMessage:
    _require_tenant(msg.tenant_id)
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 120:
        raise ValueError("Urheber muss angegeben werden")
    if not isinstance(key, str) or not key.strip() or len(key) > 120:
        raise ValueError("Idempotenzschluessel muss angegeben werden")
    identity = json.dumps([msg.tenant_id, msg.notify_type.value, key], ensure_ascii=False)
    digest = hashlib.sha256(identity.encode()).hexdigest()
    msg.msg_id = "NOTIFY-" + digest
    payload = _message_payload(msg)
    material = {k: payload[k] for k in ("phone", "kunden_nr", "notify_type", "text")}
    fingerprint = hashlib.sha256(json.dumps(material, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    with db.begin_nested():
        db.execute(sql_text("SELECT pg_advisory_xact_lock(:lock)"), {"lock": int.from_bytes(bytes.fromhex(digest[:16]), "big", signed=True)})
        existing = db.execute(sql_text("""
            SELECT request_payload, employee_ref, status FROM domain_shared.channel_process_threads
            WHERE thread_id=:id AND tenant_id=:tenant AND process_definition_key=:process
        """), {"id": msg.msg_id, "tenant": msg.tenant_id, "process": _PROCESS}).mappings().first()
        if existing:
            stored = existing["request_payload"]
            if stored.get("request_hash") != fingerprint or existing["employee_ref"] != actor:
                raise WhatsAppReplayConflict("Idempotenzschluessel wurde bereits fuer einen anderen Auftrag verwendet")
            replay = dict(stored["message"])
            replay["notify_type"] = NotifyType(replay["notify_type"])
            replay["status"] = existing["status"]
            return OutboxMessage(tenant_id=msg.tenant_id, **replay)
        db.execute(sql_text("""
            INSERT INTO domain_shared.channel_process_threads
            (thread_id, kanal, tenant_id, process_definition_key, command_name,
             aggregate_type, aggregate_id, rolle, issuer_type, employee_ref,
             request_payload, status, execution, message, is_active)
            VALUES (:id, 'WHATSAPP', :tenant, :process, 'PrepareWhatsAppNotification',
                    'whatsapp_notification', :id, 'crm:write', 'employee', :actor,
                    CAST(:payload AS JSONB), 'pending_browser', '{}'::jsonb, '', TRUE)
        """), {"id": msg.msg_id, "tenant": msg.tenant_id, "process": _PROCESS,
                "actor": actor, "payload": json.dumps({"request_hash": fingerprint, "message": payload}, ensure_ascii=False)})
        db.execute(sql_text("""
            INSERT INTO domain_shared.channel_thread_audit_items
            (thread_id, tenant_id, position, audit_type, payload, recorded_at)
            VALUES (:id, :tenant, 0, 'whatsapp.notification.prepared', CAST(:payload AS JSONB), :at)
        """), {"id": msg.msg_id, "tenant": msg.tenant_id, "payload": json.dumps({"actor": actor, "request_hash": fingerprint}), "at": msg.created_at})
    return msg


def _deliver(msg: OutboxMessage, db: Session, actor: str, key: str) -> OutboxMessage:
    """Nur vorbereiten; echte Zustellung benoetigt den autorisierten Browserweg."""
    _require_tenant(msg.tenant_id)
    msg.status = "pending_browser"
    msg.meta_msg_id = None
    msg = _persist_message(msg, db, actor, key)
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
    *, db: Session, actor: str, idempotency_key: str,
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
    msg = _deliver(msg, db, actor, idempotency_key)
    return {"msg_id": msg.msg_id, "status": msg.status, "text": text}


def send_dokument_ready(
    tenant_id: str,
    phone: str,
    kunden_nr: Optional[str],
    kunden_name: Optional[str],
    doc_typ: str,
    doc_nr: str,
    portal_url: Optional[str] = None,
    *, db: Session, actor: str, idempotency_key: str,
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
    msg = _deliver(msg, db, actor, idempotency_key)
    return {"msg_id": msg.msg_id, "status": msg.status, "text": text}


def _read_outbox(tenant_id: str, db: Session, limit: int) -> list[dict]:
    rows = db.execute(sql_text("""
        SELECT request_payload, status FROM domain_shared.channel_process_threads
        WHERE tenant_id=:tenant AND process_definition_key=:process AND kanal='WHATSAPP'
        ORDER BY created_at DESC, thread_id DESC LIMIT :limit
    """), {"tenant": tenant_id, "process": _PROCESS, "limit": limit}).mappings().all()
    return [{**row["request_payload"]["message"], "status": row["status"]} for row in rows]


def get_outbox(tenant_id: str, *, db: Session, limit: int = 50) -> list[dict]:
    _require_tenant(tenant_id)
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("Limit muss zwischen 1 und 200 liegen")
    return deepcopy(_read_outbox(tenant_id, db, limit))
