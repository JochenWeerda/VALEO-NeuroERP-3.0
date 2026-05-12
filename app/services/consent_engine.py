"""
Consent Engine — NC-004
DSGVO-konformes Einwilligungsmanagement mit vollstaendigem Lifecycle.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


CONSENT_TYPES = {
    "data_processing": "Allgemeine Datenverarbeitung (Art. 6(1)(a) DSGVO)",
    "marketing_email": "E-Mail-Marketing (Art. 6(1)(a) + UWG)",
    "marketing_whatsapp": "WhatsApp-Kontakt (Art. 6(1)(a) DSGVO)",
    "marketing_phone": "Telefonische Kontaktaufnahme (Art. 6(1)(a) + UWG)",
    "profiling": "Profilbildung (Art. 22 DSGVO)",
}


def check_consent(entity_id: str, consent_type: str, tenant_id: str, db: Session) -> dict:
    try:
        row = db.execute(text("""
            SELECT id, status, granted_at, revoked_at, expires_at
            FROM domain_shared.consents
            WHERE entity_id = :eid AND consent_type = :ct AND tenant_id = :tid
            ORDER BY granted_at DESC LIMIT 1
        """), {"eid": entity_id, "ct": consent_type, "tid": tenant_id}).fetchone()

        if row and row.status == "granted":
            if row.expires_at and datetime.fromisoformat(str(row.expires_at)) < datetime.now(timezone.utc):
                return {"entity_id": entity_id, "consent_type": consent_type, "status": "expired", "consent_id": row.id}
            return {"entity_id": entity_id, "consent_type": consent_type, "status": "granted", "consent_id": row.id}
    except Exception as exc:
        logger.warning("Consent check failed: %s", exc)

    return {"entity_id": entity_id, "consent_type": consent_type, "status": "not_granted"}


def grant_consent(entity_id: str, consent_type: str, purpose: str, tenant_id: str, db: Session) -> dict:
    consent_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    try:
        db.execute(text("""
            INSERT INTO domain_shared.consents
                (id, tenant_id, entity_id, consent_type, purpose, status, granted_at, created_at)
            VALUES (:id, :tid, :eid, :ct, :purpose, 'granted', :now, :now)
        """), {"id": consent_id, "tid": tenant_id, "eid": entity_id, "ct": consent_type, "purpose": purpose, "now": now})
        db.execute(text("""
            INSERT INTO domain_shared.audit_logs (id, action, actor, entity_type, entity_id, details, created_at)
            VALUES (:id, 'consent.granted', 'consent-engine', 'consent', :eid, :details, NOW())
        """), {"id": str(uuid4()), "eid": entity_id, "details": f"type={consent_type}, purpose={purpose}"})
        db.commit()
    except Exception as exc:
        logger.warning("Consent grant failed: %s", exc)
        db.rollback()
    return {"consent_id": consent_id, "entity_id": entity_id, "consent_type": consent_type, "status": "granted"}


def revoke_consent(entity_id: str, consent_type: str, tenant_id: str, db: Session) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    try:
        db.execute(text("""
            UPDATE domain_shared.consents
            SET status = 'revoked', revoked_at = :now
            WHERE entity_id = :eid AND consent_type = :ct AND tenant_id = :tid AND status = 'granted'
        """), {"eid": entity_id, "ct": consent_type, "tid": tenant_id, "now": now})
        db.execute(text("""
            INSERT INTO domain_shared.audit_logs (id, action, actor, entity_type, entity_id, details, created_at)
            VALUES (:id, 'consent.revoked', 'consent-engine', 'consent', :eid, :details, NOW())
        """), {"id": str(uuid4()), "eid": entity_id, "details": f"type={consent_type}"})
        db.commit()
    except Exception as exc:
        logger.warning("Consent revoke failed: %s", exc)
        db.rollback()
    return {"entity_id": entity_id, "consent_type": consent_type, "status": "revoked"}


def get_consent_status(entity_id: str, tenant_id: str, db: Session) -> list[dict]:
    try:
        rows = db.execute(text("""
            SELECT consent_type, status, granted_at, revoked_at, expires_at
            FROM domain_shared.consents
            WHERE entity_id = :eid AND tenant_id = :tid
            ORDER BY granted_at DESC
        """), {"eid": entity_id, "tid": tenant_id}).fetchall()
        return [
            {"consent_type": r.consent_type, "status": r.status,
             "granted_at": str(r.granted_at) if r.granted_at else None,
             "revoked_at": str(r.revoked_at) if r.revoked_at else None}
            for r in rows
        ]
    except Exception:
        return []
