"""DOM-COMPLIANCE-004.4 — Artikel-Sperre Audit-Trail Service (append-only)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

AKTION_SPERRE = "SPERRE"
AKTION_FREIGABE = "FREIGABE"
AKTION_STORNO = "STORNO"


class SperreAuditError(Exception):
    """Raised when Sperre/Freigabe constraints are violated."""


def _get_aktuelle_sperre(db: Session, artikel_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
    """Gibt die letzte Aktion für diesen Artikel zurück."""
    row = db.execute(
        text("""
            SELECT * FROM domain_compliance.compliance_artikel_sperre_audit
            WHERE artikel_id = :artikel_id AND tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"artikel_id": artikel_id, "tenant_id": tenant_id},
    ).mappings().first()
    return dict(row) if row else None


def _append_audit(
    db: Session,
    artikel_id: str,
    tenant_id: str,
    aktion: str,
    operator: str,
    grund: Optional[str],
    nachweis_ref: Optional[str],
) -> Dict[str, Any]:
    audit_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_compliance.compliance_artikel_sperre_audit
                (id, artikel_id, tenant_id, aktion, operator, grund, nachweis_ref, created_at)
            VALUES (:id, :artikel_id, :tenant_id, :aktion, :operator, :grund, :nachweis_ref, NOW())
        """),
        {
            "id": audit_id,
            "artikel_id": artikel_id,
            "tenant_id": tenant_id,
            "aktion": aktion,
            "operator": operator,
            "grund": grund,
            "nachweis_ref": nachweis_ref,
        },
    )
    return {"id": audit_id, "artikel_id": artikel_id, "tenant_id": tenant_id, "aktion": aktion}


def sperre_artikel(
    db: Session,
    artikel_id: str,
    tenant_id: str,
    grund: str,
    operator: str = "system",
    nachweis_ref: Optional[str] = None,
) -> Dict[str, Any]:
    """Setzt eine Artikelsperre und schreibt Audit-Eintrag (idempotent wenn bereits gesperrt)."""
    letzte = _get_aktuelle_sperre(db, artikel_id, tenant_id)
    if letzte and letzte["aktion"] == AKTION_SPERRE:
        logger.info("artikel %s bereits gesperrt — idempotent", artikel_id)
        return {**letzte, "idempotent": True}

    entry = _append_audit(db, artikel_id, tenant_id, AKTION_SPERRE, operator, grund, nachweis_ref)
    db.commit()
    logger.info("artikel %s gesperrt von %s: %s", artikel_id, operator, grund)
    return {**entry, "idempotent": False}


def freigabe_artikel(
    db: Session,
    artikel_id: str,
    tenant_id: str,
    operator: str = "system",
    nachweis_ref: Optional[str] = None,
    bemerkung: Optional[str] = None,
) -> Dict[str, Any]:
    """Gibt einen gesperrten Artikel frei (fail-closed wenn nicht gesperrt)."""
    letzte = _get_aktuelle_sperre(db, artikel_id, tenant_id)
    if not letzte or letzte["aktion"] != AKTION_SPERRE:
        raise SperreAuditError(
            f"Artikel {artikel_id} ist nicht gesperrt — Freigabe nicht möglich"
        )

    entry = _append_audit(db, artikel_id, tenant_id, AKTION_FREIGABE, operator, bemerkung, nachweis_ref)
    db.commit()
    logger.info("artikel %s freigegeben von %s", artikel_id, operator)
    return entry


def storno_sperre(
    db: Session,
    artikel_id: str,
    tenant_id: str,
    grund: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Storniert die letzte Sperre-Aktion (nur möglich wenn letzte Aktion = SPERRE)."""
    letzte = _get_aktuelle_sperre(db, artikel_id, tenant_id)
    if not letzte:
        raise SperreAuditError(f"Keine Sperre-Historie für Artikel {artikel_id}")
    if letzte["aktion"] != AKTION_SPERRE:
        raise SperreAuditError(
            f"Storno nur möglich wenn letzte Aktion SPERRE war (aktuell: {letzte['aktion']})"
        )

    entry = _append_audit(db, artikel_id, tenant_id, AKTION_STORNO, operator, grund, None)
    db.commit()
    logger.info("artikel %s Sperre storniert von %s", artikel_id, operator)
    return entry


def get_sperre_audit_trail(
    db: Session,
    artikel_id: str,
    tenant_id: str,
) -> List[Dict[str, Any]]:
    """Gibt vollständigen Audit-Trail für einen Artikel zurück (chronologisch aufsteigend)."""
    rows = db.execute(
        text("""
            SELECT * FROM domain_compliance.compliance_artikel_sperre_audit
            WHERE artikel_id = :artikel_id AND tenant_id = :tenant_id
            ORDER BY created_at ASC
        """),
        {"artikel_id": artikel_id, "tenant_id": tenant_id},
    ).mappings().all()
    return [dict(r) for r in rows]
