"""Server-seitiger IMAP-Mail-Ingest (per Tenant konfiguriert).

Pendant zum externen Poller (tools/mail-connector): pollt das in der Admin-Suite
hinterlegte IMAP-Postfach (ImapConfig) direkt im Backend und erfasst neue Mails
über CrmAutoCaptureService (channel='email'). So lässt sich der Abruf ohne ENV
und ohne separaten Prozess per Mandant betreiben — manuell („Jetzt abrufen") oder
über einen Scheduler.

Idempotenz: Message-ID je Mail (verweis) + zuletzt gesehene IMAP-UID je Ordner
(connectors_state). Abhängigkeitsfrei (stdlib imaplib/email).
"""

from __future__ import annotations

import email
import hashlib
import imaplib
import logging
from email.utils import getaddresses, parseaddr
from sqlalchemy.orm import Session

from app.services.connector_config import (
    ImapConfig,
    load_imap_config,
    load_imap_state,
    save_imap_state,
)
from app.services.crm_auto_capture_service import CrmAutoCaptureService
from app.services.mail_workspace_service import MailWorkspaceService

logger = logging.getLogger("mail.ingest")


def _plain_text(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(
                part.get("Content-Disposition", "")
            ):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(
                        part.get_content_charset() or "utf-8", "replace"
                    )
        return ""
    payload = msg.get_payload(decode=True)
    if payload:
        return payload.decode(msg.get_content_charset() or "utf-8", "replace")
    return str(msg.get_payload() or "")


def _decode(raw: str) -> str:
    out = ""
    for text_part, enc in email.header.decode_header(raw or ""):
        out += (
            text_part.decode(enc or "utf-8", "replace")
            if isinstance(text_part, bytes)
            else text_part
        )
    return out


class MailIngestService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def test(self) -> dict:
        """Verbindungs-/Login-Probe für die Admin-Suite (kein Abruf)."""
        cfg = load_imap_config(self.db, self.tenant_id)
        if not cfg.resolved_host() or not cfg.resolved_user():
            return {
                "ok": False,
                "detail": "Host und Benutzer sind erforderlich.",
                "host": cfg.resolved_host(),
                "folders": 0,
            }
        try:
            cfg.validate_command_values()
            imap = self._connect(cfg)
        except (ValueError, imaplib.IMAP4.error, OSError) as exc:
            return {
                "ok": False,
                "detail": f"Login fehlgeschlagen: {exc}",
                "host": cfg.resolved_host(),
                "folders": 0,
            }
        try:
            status, boxes = imap.list()
            n = len(boxes) if status == "OK" and boxes else 0
            return {
                "ok": True,
                "detail": f"Login OK · {n} Ordner sichtbar.",
                "host": cfg.resolved_host(),
                "folders": n,
            }
        finally:
            self._logout(imap)

    def poll_once(self) -> dict:
        """Holt neue Mails aus Posteingang (+ optional Gesendet) und erfasst sie."""
        cfg = load_imap_config(self.db, self.tenant_id)
        if not cfg.configured:
            return {
                "ok": False,
                "detail": "IMAP ist nicht aktiviert/konfiguriert.",
                "processed": 0,
            }
        try:
            cfg.validate_command_values()
            imap = self._connect(cfg)
        except (ValueError, imaplib.IMAP4.error, OSError) as exc:
            return {
                "ok": False,
                "detail": f"Login fehlgeschlagen: {exc}",
                "processed": 0,
            }

        state = load_imap_state(self.db, self.tenant_id)
        capture = CrmAutoCaptureService(self.db, self.tenant_id)
        processed = 0
        created = 0
        try:
            folders = [(cfg.inbox, "incoming")]
            if cfg.sent:
                folders.append((cfg.sent, "outgoing"))
            for folder, direction in folders:
                key = f"{folder}:uid"
                last_uid = int(state.get(key, 0))
                for uid_i, raw in self._fetch_new(imap, folder, last_uid):
                    res = self._ingest(capture, raw, direction, cfg.own_addresses)
                    processed += 1
                    if res.get("status") == "created":
                        created += 1
                    state[key] = max(int(state.get(key, 0)), uid_i)
        finally:
            self._logout(imap)

        save_imap_state(self.db, self.tenant_id, state)
        return {
            "ok": True,
            "processed": processed,
            "created": created,
            "detail": f"{processed} neue Mail(s) verarbeitet, {created} Kontakt(e) angelegt.",
        }

    # ── intern ────────────────────────────────────────────────────────────────
    def _connect(self, cfg: ImapConfig) -> imaplib.IMAP4:
        imap: imaplib.IMAP4
        if cfg.ssl:
            imap = imaplib.IMAP4_SSL(cfg.resolved_host(), cfg.port)
        else:
            imap = imaplib.IMAP4(cfg.resolved_host(), cfg.port)
        imap.login(cfg.resolved_user(), cfg.resolved_password())
        return imap

    @staticmethod
    def _logout(imap: imaplib.IMAP4) -> None:
        try:
            imap.logout()
        except Exception:
            pass

    @staticmethod
    def _fetch_new(
        imap: imaplib.IMAP4, folder: str, last_uid: int
    ) -> list[tuple[int, bytes]]:
        status, _ = imap.select(folder, readonly=True)
        if status != "OK":
            return []
        if last_uid <= 0:
            status, data = imap.uid("search", None, "ALL")
            uids = data[0].split()[-20:] if data and data[0] else []
        else:
            status, data = imap.uid("search", None, f"UID {last_uid + 1}:*")
            uids = data[0].split() if data and data[0] else []
        out: list[tuple[int, bytes]] = []
        for uid in uids:
            uid_i = int(uid)
            if uid_i <= last_uid:
                continue
            status, msg_data = imap.uid("fetch", uid, "(RFC822)")
            if status == "OK" and msg_data and msg_data[0]:
                out.append((uid_i, msg_data[0][1]))
        return out

    def _ingest(
        self, capture: CrmAutoCaptureService, raw: bytes, direction: str, own: list[str]
    ) -> dict:
        msg = email.message_from_bytes(raw)
        from_addr = parseaddr(msg.get("From", ""))[1]
        to_list = [a for _, a in getaddresses(msg.get_all("To", []))]
        subject = _decode(msg.get("Subject", ""))
        text_body = _plain_text(msg)
        message_id = (msg.get("Message-ID", "") or "").strip("<>") or None

        own_lc = {a.lower() for a in own}
        if from_addr and from_addr.lower() in own_lc:
            direction = "outgoing"
        peer = (
            from_addr
            if direction == "incoming"
            else (to_list[0] if to_list else from_addr)
        )
        content = (
            f"{subject}\n\n{text_body}"
            if subject and text_body
            else (text_body or subject)
        )

        result = capture.capture(
            channel="email",
            direction=direction,
            peer=peer,
            content=content,
            betreff=subject or None,
            verweis=message_id,
            bediener="AUTO",
        )
        attachments: list[dict] = []
        for part in msg.walk():
            filename = part.get_filename()
            if not filename:
                continue
            content_bytes = part.get_payload(decode=True) or b""
            attachments.append(
                {
                    "filename": _decode(filename),
                    "mime_type": part.get_content_type(),
                    "content": content_bytes,
                }
            )
        workspace_id = message_id or hashlib.sha256(raw).hexdigest()
        MailWorkspaceService(self.db, self.tenant_id).ingest(
            message_id=workspace_id,
            role_key="crm",
            direction=direction,
            from_address=from_addr,
            to_addresses=to_list,
            subject=subject or None,
            body_text=text_body,
            attachments=attachments,
        )
        return result
