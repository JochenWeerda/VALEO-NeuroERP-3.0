"""Per-Tenant-Konfiguration der Auto-Capture-Connectoren (STT + IMAP).

Analog zum LLM-Gateway (siehe app/services/llm_gateway.py) liest/schreibt der
Administrator die Connector-Einstellungen über die Admin-Suite; gespeichert im
JSONB `domain_shared.tenants.settings` unter dem Schlüssel ``connectors``.

Precedence: Tenant-Settings > Umgebungsvariablen (Default/Fallback). So lässt sich
alles per Mandant in der UI pflegen, ohne ENV anzufassen — ENV bleibt als globaler
Default/Bootstrap gültig.

  connectors = {
    "stt":  {enabled, base_url, model, api_key, language},
    "imap": {enabled, host, port, ssl, user, password, inbox, sent,
             own_addresses, poll_seconds},
  }

Der Laufzeit-Status der IMAP-Abrufe (zuletzt gesehene UID je Ordner) liegt
getrennt unter ``connectors_state`` — damit das Speichern der Konfiguration den
State nicht überschreibt und umgekehrt.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

SETTINGS_KEY = "connectors"
STATE_KEY = "connectors_state"


# ── Tenant-Settings I/O ──────────────────────────────────────────────────────────
def _read_settings(db: Optional[Session], tenant_id: Optional[str]) -> dict:
    if db is None or not tenant_id:
        return {}
    try:
        raw = db.execute(
            text("SELECT settings FROM domain_shared.tenants WHERE id = :t"), {"t": tenant_id}
        ).scalar()
    except Exception:
        if db is not None:
            db.rollback()
        return {}
    if not raw:
        return {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return {}
    return raw or {}


def _write_settings(db: Session, tenant_id: str, settings: dict) -> None:
    db.execute(
        text("UPDATE domain_shared.tenants SET settings = :s, updated_at = NOW() WHERE id = :t"),
        {"s": json.dumps(settings), "t": tenant_id},
    )
    db.commit()


# ── STT-Konfiguration ────────────────────────────────────────────────────────────
@dataclass
class SttConfig:
    enabled: bool = True
    base_url: str = ""
    model: str = ""
    api_key: str = ""
    language: str = "de"

    def resolved_base_url(self) -> str:
        return (self.base_url or os.getenv("STT_BASE_URL", "")).rstrip("/")

    def resolved_model(self) -> str:
        return self.model or os.getenv("STT_MODEL", "whisper-1")

    def resolved_api_key(self) -> str:
        return self.api_key or os.getenv("STT_API_KEY", "")

    def resolved_language(self) -> str:
        return self.language or os.getenv("STT_LANGUAGE", "de")

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.resolved_base_url())


def load_stt_config(db: Optional[Session] = None, tenant_id: Optional[str] = None) -> SttConfig:
    stored = (_read_settings(db, tenant_id).get(SETTINGS_KEY) or {}).get("stt") or {}
    return SttConfig(
        enabled=bool(stored.get("enabled", True)),
        base_url=(stored.get("base_url") or "").strip(),
        model=(stored.get("model") or "").strip(),
        api_key=(stored.get("api_key") or "").strip(),
        language=(stored.get("language") or "").strip() or "de",
    )


# ── IMAP-Konfiguration ───────────────────────────────────────────────────────────
@dataclass
class ImapConfig:
    enabled: bool = False
    host: str = ""
    port: int = 993
    ssl: bool = True
    user: str = ""
    password: str = ""
    inbox: str = "INBOX"
    sent: str = ""
    own_addresses: list[str] = field(default_factory=list)
    poll_seconds: int = 60

    def resolved_host(self) -> str:
        return self.host or os.getenv("IMAP_HOST", "")

    def resolved_user(self) -> str:
        return self.user or os.getenv("IMAP_USER", "")

    def resolved_password(self) -> str:
        return self.password or os.getenv("IMAP_PASSWORD", "")

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.resolved_host() and self.resolved_user())


def _split_addresses(raw) -> list[str]:
    if isinstance(raw, list):
        return [str(a).strip() for a in raw if str(a).strip()]
    return [a.strip() for a in str(raw or "").split(",") if a.strip()]


def load_imap_config(db: Optional[Session] = None, tenant_id: Optional[str] = None) -> ImapConfig:
    stored = (_read_settings(db, tenant_id).get(SETTINGS_KEY) or {}).get("imap") or {}
    own = stored.get("own_addresses")
    if own is None:
        own = os.getenv("MAIL_OWN_ADDRESSES", "")
    return ImapConfig(
        enabled=bool(stored.get("enabled", False)),
        host=(stored.get("host") or "").strip(),
        port=int(stored.get("port", 993) or 993),
        ssl=bool(stored.get("ssl", True)),
        user=(stored.get("user") or "").strip(),
        password=(stored.get("password") or "").strip(),
        inbox=(stored.get("inbox") or "INBOX").strip() or "INBOX",
        sent=(stored.get("sent") or "").strip(),
        own_addresses=_split_addresses(own),
        poll_seconds=int(stored.get("poll_seconds", 60) or 60),
    )


# ── Speichern (Admin) — Secrets nur bei Angabe ersetzen ──────────────────────────
def save_connectors(
    db: Session,
    tenant_id: str,
    *,
    stt: Optional[dict] = None,
    imap: Optional[dict] = None,
) -> None:
    settings = _read_settings(db, tenant_id)
    store = settings.get(SETTINGS_KEY)
    if not isinstance(store, dict):
        store = {}

    if stt is not None:
        cur = store.get("stt") if isinstance(store.get("stt"), dict) else {}
        for k in ("enabled", "base_url", "model", "language"):
            if k in stt and stt[k] is not None:
                cur[k] = stt[k]
        if stt.get("api_key"):  # nur nicht-leeren Key überschreiben
            cur["api_key"] = stt["api_key"]
        store["stt"] = cur

    if imap is not None:
        cur = store.get("imap") if isinstance(store.get("imap"), dict) else {}
        for k in ("enabled", "host", "port", "ssl", "user", "inbox", "sent",
                  "own_addresses", "poll_seconds"):
            if k in imap and imap[k] is not None:
                cur[k] = imap[k]
        if imap.get("password"):  # nur nicht-leeres Passwort überschreiben
            cur["password"] = imap["password"]
        store["imap"] = cur

    settings[SETTINGS_KEY] = store
    _write_settings(db, tenant_id, settings)


# ── IMAP-Abruf-State (zuletzt gesehene UID je Ordner) ────────────────────────────
def load_imap_state(db: Session, tenant_id: str) -> dict[str, int]:
    state = (_read_settings(db, tenant_id).get(STATE_KEY) or {}).get("imap") or {}
    return {str(k): int(v) for k, v in state.items()} if isinstance(state, dict) else {}


def save_imap_state(db: Session, tenant_id: str, imap_state: dict[str, int]) -> None:
    settings = _read_settings(db, tenant_id)
    store = settings.get(STATE_KEY)
    if not isinstance(store, dict):
        store = {}
    store["imap"] = {str(k): int(v) for k, v in imap_state.items()}
    settings[STATE_KEY] = store
    _write_settings(db, tenant_id, settings)
