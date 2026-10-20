"""
FIBU Audit – einheitliches Schreiben von Prüfprotokoll-Einträgen in domain_shared.audit_logs.
Erforderlicher Audit-Eintrag; Fachaufrufer muessen denselben Transaktionsbesitz verwenden.
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

# Interne Systemkennung ausschliesslich fuer Aufrufe ohne HTTP-Request.
# Audit speichert die Ursprungskennung ohne Fremdschluessel auf lokale Nutzerprofile.
SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001"
SYSTEM_USER_EMAIL = "system@internal"


class AuditWriteError(RuntimeError):
    """A required finance audit could not be persisted."""


def _user_from_request(request: Optional[Any]) -> tuple[str, str]:
    """user_id, user_email aus der geprueften Anmeldung (``request.state.token_claims``), nie aus Client-Kopfzeilen.

    Bis zum 19.10.2026 kamen beide zuerst aus ``X-User-ID``/``X-User-Email``: Ein Client schrieb FiBu-Audit unter
    fremdem Namen. Ohne gepruefte Anmeldung (System, Import) steht der Systemnutzer im Eintrag.
    """
    if request is None:
        return SYSTEM_USER_ID, SYSTEM_USER_EMAIL
    state = getattr(request, "state", None)
    claims = getattr(state, "token_claims", None) if state is not None else None
    sub = claims.get("sub") if isinstance(claims, dict) else None
    if not isinstance(sub, str) or not sub.strip():
        from fastapi import HTTPException
        raise HTTPException(403, "Verified finance audit actor required")
    email = next((str(claims[k]).strip() for k in ("email", "preferred_username") if str(claims.get(k) or "").strip()),
                 f"{sub}@token")
    return sub, email


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
    *,
    commit: bool = True,
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
        user_id: Explizite interne Kennung nur ohne HTTP-Request
        user_email: Explizite interne Mail nur ohne HTTP-Request
        ip_address: Optional IP (sonst aus request)
        user_agent: Optional User-Agent (sonst aus request)
        commit: False wenn der Aufrufer die gesamte Transaktion abschliesst
    """
    uid, email = (user_id, user_email or "") if request is None and user_id else _user_from_request(request)
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
        db.flush()
        if commit:
            db.commit()
    except Exception as e:
        logger.error("Required finance audit failed (%s)", type(e).__name__)
        db.rollback()
        raise AuditWriteError("Required finance audit could not be persisted") from None
