#!/usr/bin/env python3
"""VALEO NeuroERP — E-Mail-Connector (IMAP → Auto-Capture).

Lokaler/serverseitiger Dienst: pollt ein IMAP-Postfach (Posteingang und optional
Gesendet-Ordner) und meldet jede neue Mail an das ERP
(POST /api/v1/crm/kim/mail-capture). Daraus wird automatisch ein Kontakt in der
KIM-Kontakthistorie — nicht zuordenbare Mails landen in der Klärfall-Inbox.

Bewusst **abhängigkeitsfrei** (nur Python-Standardbibliothek: imaplib, email,
urllib), damit der Dienst ohne pip-Install auf jedem Python-3.8+-Host läuft.
Alternativ kann derselbe ERP-Endpoint direkt von OSS-Webhooks bedient werden
(IMAP-API/ewildgoose, MXHook, Mox) — dann wird dieser Poller nicht benötigt.

Idempotenz: die Message-ID jeder Mail wird als `verweis` übergeben; das ERP legt
keinen Doppel-Kontakt an. Zusätzlich merkt sich der Poller die zuletzt gesehene
IMAP-UID je Ordner (State-Datei), um nur neue Mails zu verarbeiten.

Konfiguration über Umgebungsvariablen (CLI-Argumente haben Vorrang):
  IMAP_HOST          IMAP-Server (z. B. imap.gmail.com, outlook.office365.com)
  IMAP_PORT          Default 993 (SSL)
  IMAP_USER          Postfach-Benutzer / E-Mail-Adresse
  IMAP_PASSWORD      Passwort bzw. App-Passwort
  IMAP_INBOX         Posteingang-Ordner       (Default: INBOX)
  IMAP_SENT          Gesendet-Ordner für ausgehende Mails (Default: leer = aus)
  MAIL_OWN_ADDRESSES Eigene Adressen, kommagetrennt (Richtungserkennung)
  POLL_SECONDS       Poll-Intervall in Sekunden (Default: 60)
  VALEO_API_BASE     ERP-Basis-URL            (Default: http://localhost:8000)
  VALEO_API_TOKEN    Bearer-Token             (Dev: dev-token)
  VALEO_TENANT_ID    X-Tenant-ID
  STATE_FILE         Pfad der UID-State-Datei (Default: .mail_connector_state.json)

Beispiele:
  # Dauerbetrieb Posteingang + Gesendet:
  python mail_connector.py --host imap.example.de --user crm@example.de \
      --password '***' --sent 'Sent' --own crm@example.de --api-base http://erp:8000

  # Einmal-Lauf (Cron/Task-Scheduler), nur neue Mails seit letztem Lauf:
  python mail_connector.py --once
"""

from __future__ import annotations

import argparse
import email
import imaplib
import json
import logging
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from email.utils import getaddresses, parseaddr
from typing import Optional

log = logging.getLogger("mail-connector")

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


# ── ERP-Meldung ────────────────────────────────────────────────────────────────
class ErpClient:
    def __init__(self, api_base: str, token: str, tenant_id: str, timeout: float = 15.0) -> None:
        self.url = api_base.rstrip("/") + "/api/v1/crm/kim/mail-capture"
        self.token = token
        self.tenant_id = tenant_id
        self.timeout = timeout

    def post_mail(self, payload: dict, retries: int = 2) -> bool:
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "X-Tenant-ID": self.tenant_id,
        }
        for attempt in range(retries + 1):
            req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    log.info("Mail gemeldet (%s): status=%s", payload.get("messageId"), body.get("status"))
                    return True
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:200]
                log.error("ERP HTTP %s: %s", exc.code, detail)
                if exc.code in (401, 403):
                    return False
            except (urllib.error.URLError, socket.timeout, ConnectionError) as exc:
                log.warning("ERP nicht erreichbar (%d/%d): %s", attempt + 1, retries + 1, exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
        return False


# ── Mail-Parsing ────────────────────────────────────────────────────────────────
def _plain_text(msg: email.message.Message) -> str:
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


def _decode_header(raw: str) -> str:
    parts = email.header.decode_header(raw or "")
    out = ""
    for text_part, enc in parts:
        if isinstance(text_part, bytes):
            out += text_part.decode(enc or "utf-8", "replace")
        else:
            out += text_part
    return out


def build_payload(raw_bytes: bytes, direction: str, own: list[str]) -> dict:
    msg = email.message_from_bytes(raw_bytes)
    from_addr = parseaddr(msg.get("From", ""))[1]
    to_list = [a for _, a in getaddresses(msg.get_all("To", []))]
    return {
        "fromAddr": from_addr,
        "toAddr": to_list[0] if to_list else None,
        "subject": _decode_header(msg.get("Subject", "")),
        "text": _plain_text(msg),
        "messageId": (msg.get("Message-ID", "") or "").strip("<>") or None,
        "direction": direction,
        "ownAddresses": own,
    }


# ── State (zuletzt gesehene UID je Ordner) ───────────────────────────────────────
def load_state(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(path: str, state: dict) -> None:
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
    except OSError as exc:
        log.warning("State-Datei nicht schreibbar (%s): %s", path, exc)


# ── IMAP-Abruf ───────────────────────────────────────────────────────────────────
def fetch_new(imap: imaplib.IMAP4_SSL, folder: str, last_uid: int) -> list[tuple[int, bytes]]:
    """Liefert (uid, raw_bytes) aller Mails mit UID > last_uid im Ordner."""
    status, _ = imap.select(folder, readonly=True)
    if status != "OK":
        log.warning("Ordner %s nicht wählbar", folder)
        return []
    # UID-Bereich ab last_uid+1; beim ersten Lauf (last_uid=0) nur die jüngsten 20.
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


def poll_once(client: ErpClient, args, state: dict) -> int:
    own = [a.strip() for a in (args.own or "").split(",") if a.strip()]
    processed = 0
    try:
        imap = imaplib.IMAP4_SSL(args.host, args.port)
        imap.login(args.user, args.password)
    except (imaplib.IMAP4.error, OSError) as exc:
        log.error("IMAP-Login fehlgeschlagen (%s@%s): %s", args.user, args.host, exc)
        return 0
    try:
        folders = [(args.inbox, "incoming")]
        if args.sent:
            folders.append((args.sent, "outgoing"))
        for folder, direction in folders:
            key = f"{folder}:uid"
            last_uid = int(state.get(key, 0))
            for uid_i, raw in fetch_new(imap, folder, last_uid):
                payload = build_payload(raw, direction, own)
                if client.post_mail(payload):
                    processed += 1
                state[key] = max(int(state.get(key, 0)), uid_i)
    finally:
        try:
            imap.logout()
        except Exception:
            pass
    return processed


# ── CLI ──────────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="VALEO NeuroERP E-Mail-Connector (IMAP → Auto-Capture)")
    p.add_argument("--host", default=os.getenv("IMAP_HOST", ""))
    p.add_argument("--port", type=int, default=int(os.getenv("IMAP_PORT", "993")))
    p.add_argument("--user", default=os.getenv("IMAP_USER", ""))
    p.add_argument("--password", default=os.getenv("IMAP_PASSWORD", ""))
    p.add_argument("--inbox", default=os.getenv("IMAP_INBOX", "INBOX"))
    p.add_argument("--sent", default=os.getenv("IMAP_SENT", ""), help="Gesendet-Ordner (optional)")
    p.add_argument("--own", default=os.getenv("MAIL_OWN_ADDRESSES", ""), help="Eigene Adressen, kommagetrennt")
    p.add_argument("--poll-seconds", type=int, default=int(os.getenv("POLL_SECONDS", "60")))
    p.add_argument("--once", action="store_true", help="Nur einen Durchlauf (für Cron/Task-Scheduler)")
    p.add_argument("--api-base", default=os.getenv("VALEO_API_BASE", "http://localhost:8000"))
    p.add_argument("--token", default=os.getenv("VALEO_API_TOKEN", "dev-token"))
    p.add_argument("--tenant", default=os.getenv("VALEO_TENANT_ID", DEFAULT_TENANT))
    p.add_argument("--state-file", default=os.getenv("STATE_FILE", ".mail_connector_state.json"))
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    if not args.host or not args.user:
        log.error("IMAP_HOST und IMAP_USER sind erforderlich (siehe --help).")
        return 2
    client = ErpClient(args.api_base, args.token, args.tenant)
    log.info("E-Mail-Connector → %s (Tenant %s); Postfach %s@%s", client.url, args.tenant, args.user, args.host)
    state = load_state(args.state_file)
    try:
        while True:
            n = poll_once(client, args, state)
            save_state(args.state_file, state)
            if n:
                log.info("%d neue Mail(s) verarbeitet.", n)
            if args.once:
                return 0
            time.sleep(max(10, args.poll_seconds))
    except KeyboardInterrupt:
        log.info("Beendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
