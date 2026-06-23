"""DOM-POS-004.2 — POS Tagesabschluss Lifecycle (Z-Bon, TSE-Signatur, DSFinV-K-Export)."""
from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_ABSCHLUSS_TRANSITIONS = {
    ("OFFEN", "IN_ABSCHLUSS"),
    ("IN_ABSCHLUSS", "Z_BON_ERSTELLT"),
    ("Z_BON_ERSTELLT", "TSE_SIGNIERT"),
    ("TSE_SIGNIERT", "DSFINVK_EXPORTIERT"),
    ("DSFINVK_EXPORTIERT", "ABGESCHLOSSEN"),
    ("IN_ABSCHLUSS", "FEHLER"),
    ("Z_BON_ERSTELLT", "FEHLER"),
    ("TSE_SIGNIERT", "FEHLER"),
}


class POSTagesabschlussError(Exception):
    pass


def create_tagesabschluss(
    db: Session,
    tenant_id: str,
    kasse_id: str,
    datum: str,
    operator: str = "system",
) -> Dict[str, Any]:
    existing = db.execute(
        text("""
            SELECT * FROM domain_pos.pos_tagesabschluesse
            WHERE kasse_id = :kid AND datum = :datum AND tenant_id = :tid
        """),
        {"kid": kasse_id, "datum": datum, "tid": tenant_id},
    ).mappings().first()
    if existing:
        return dict(existing)

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_pos.pos_tagesabschluesse
                (id, tenant_id, kasse_id, datum, status, operator, created_at)
            VALUES (:id, :tenant_id, :kasse_id, :datum, 'OFFEN', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "kasse_id": kasse_id,
            "datum": datum,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_pos.pos_tagesabschluesse WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_tagesabschluss(
    db: Session,
    abschluss_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_pos.pos_tagesabschluesse
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": abschluss_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise POSTagesabschlussError(f"Tagesabschluss {abschluss_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_ABSCHLUSS_TRANSITIONS:
        raise POSTagesabschlussError(f"Ungültiger Übergang {old_status} → {new_status}")

    extra_fields = ""
    params: Dict[str, Any] = {
        "new_status": new_status,
        "id": abschluss_id,
        "tid": tenant_id,
    }
    if payload:
        if "z_bon_nr" in payload:
            extra_fields += ", z_bon_nr = :z_bon_nr"
            params["z_bon_nr"] = payload["z_bon_nr"]
        if "tse_signatur" in payload:
            extra_fields += ", tse_signatur = :tse_signatur"
            params["tse_signatur"] = payload["tse_signatur"]
        if "dsfinvk_export_pfad" in payload:
            extra_fields += ", dsfinvk_export_pfad = :dsfinvk_export_pfad"
            params["dsfinvk_export_pfad"] = payload["dsfinvk_export_pfad"]
        if "umsatz_brutto_eur" in payload:
            extra_fields += ", umsatz_brutto_eur = :umsatz_brutto_eur"
            params["umsatz_brutto_eur"] = payload["umsatz_brutto_eur"]
        if "fehler_grund" in payload:
            extra_fields += ", fehler_grund = :fehler_grund"
            params["fehler_grund"] = payload["fehler_grund"]

    db.execute(
        # nosec S608 — extra_fields is assembled only from fixed code-controlled fragments; values are parameterized.
        text(f"""
            UPDATE domain_pos.pos_tagesabschluesse
            SET status = :new_status{extra_fields}, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        params,
    )
    _log_abschluss_event(db, abschluss_id, tenant_id, old_status, new_status, operator)
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_pos.pos_tagesabschluesse WHERE id = :id"),
        {"id": abschluss_id},
    ).mappings().first()
    return dict(updated)


def _log_abschluss_event(
    db: Session,
    abschluss_id: str,
    tenant_id: str,
    old_status: str,
    new_status: str,
    operator: str,
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_pos.pos_tagesabschluss_log
                (id, abschluss_id, tenant_id, old_status, new_status, operator, created_at)
            VALUES (:id, :abschluss_id, :tenant_id, :old_status, :new_status, :operator, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "abschluss_id": abschluss_id,
            "tenant_id": tenant_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
        },
    )


def simulate_tse_signatur(
    kasse_id: str,
    z_bon_nr: str,
    umsatz_brutto_eur: float,
) -> Dict[str, Any]:
    """Simulierte TSE-Signatur (kein echtes TSE-Modul — externes Gate)."""
    import hashlib
    payload = f"{kasse_id}:{z_bon_nr}:{umsatz_brutto_eur}"
    sig_hash = hashlib.sha256(payload.encode()).hexdigest()[:32]
    return {
        "tse_serial": f"SIM-TSE-{kasse_id[:8].upper()}",
        "tse_signatur": f"SIM-SIG-{sig_hash}",
        "tse_zeitpunkt": "2026-06-23T00:00:00Z",
        "hinweis": "Simulierte Signatur — keine echte TSE-Abnahme",
    }
