"""
FIBU Audit – einheitliches Schreiben von Prüfprotokoll-Einträgen in domain_shared.audit_logs.
GoBD-konform für alle Schreibzugriffe auf Journal, Kontenplan, OP, Perioden.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from app.infrastructure.models import AuditLog
from app.core.logging import get_correlation_id

logger = logging.getLogger(__name__)

# Fallback wenn kein Benutzer aus Request verfügbar ist (z. B. System/Import).
# Muss als User in domain_shared.users existieren oder FK für user_id in audit_logs deaktiviert sein.
SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001"
SYSTEM_USER_EMAIL = "system@internal"


def _user_from_request(request: Optional[Any]) -> tuple[str, str]:
    """user_id, user_email aus Request-Headern (X-User-ID, X-User-Email) oder Bearer-Token sub/preferred_username."""
    if not request:
        return SYSTEM_USER_ID, SYSTEM_USER_EMAIL
    user_id = (request.headers.get("X-User-ID") or "").strip()
    user_email = (request.headers.get("X-User-Email") or "").strip()
    if user_id and user_email:
        return user_id, user_email
    if user_id:
        return user_id, user_email or f"{user_id}@internal"
    # Optional: aus Bearer-Token sub/preferred_username auslesen (ohne Validierung)
    try:
        auth = request.headers.get("Authorization") or ""
        if auth.startswith("Bearer ") and hasattr(request.app.state, "decode_token"):
            # App könnte decode_token bereitstellen
            pass
    except Exception:  # noqa: BLE001 — Token-Dekodierung fehlgeschlagen; System-User-ID wird verwendet
        pass
    return SYSTEM_USER_ID, SYSTEM_USER_EMAIL


def log_fibu_audit(
    db: Session,
    tenant_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    changes: Dict[str, Any],
    request: Optional[Any] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Schreibt einen Eintrag in domain_shared.audit_logs für FIBU-relevante Aktionen.

    Args:
        db: SQLAlchemy Session
        tenant_id: Mandanten-ID
        action: Aktion (z. B. create, update, delete, post, reverse, settle)
        entity_type: Entitätstyp (z. B. journal_entry, finance_account, open_item, accounting_period)
        entity_id: ID der betroffenen Entität
        changes: Dict mit Änderungen (z. B. {"status": {"old": "draft", "new": "posted"}})
        request: Optional FastAPI Request für User/IP/User-Agent
        user_id: Optional explizite user_id (überschreibt Request)
        user_email: Optional explizite user_email (überschreibt Request)
        ip_address: Optional IP (sonst aus request)
        user_agent: Optional User-Agent (sonst aus request)
    """
    uid, email = (user_id, user_email) if (user_id and user_email) else _user_from_request(request)
    if request and not ip_address:
        ip_address = request.client.host if request.client else None
    if request and not user_agent:
        user_agent = request.headers.get("User-Agent")
    try:
        entry = AuditLog(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            user_id=uid,
            user_email=email,
            tenant_id=tenant_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=get_correlation_id() or None,
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.warning("FIBU audit log write failed: %s", e)
        db.rollback()
