"""DOM-COMPLIANCE-004.3 — VVVO-Prüfung + Sachkunde-Ablauf-Monitoring."""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

DEFAULT_ALARM_DAYS = 30
VVVO_PRUEF_INTERVAL_DAYS = 365


class VVVOError(Exception):
    """Raised when VVVO/Sachkunde constraints are violated."""


def list_faellige_vvvo_pruefungen(
    db: Session,
    tenant_id: str,
    within_days: int = DEFAULT_ALARM_DAYS,
) -> List[Dict[str, Any]]:
    """Listet VVVO-Betriebe, deren jährliche Prüfung innerhalb von `within_days` Tagen fällig ist."""
    cutoff = (date.today() + timedelta(days=within_days)).isoformat()
    today = date.today().isoformat()
    rows = db.execute(
        text("""
            SELECT id, tenant_id, betrieb_name, vvvo_nummer,
                   letzte_pruefung_am, naechste_pruefung_am
            FROM domain_compliance.compliance_vvvo_register
            WHERE tenant_id = :tenant_id
              AND naechste_pruefung_am <= :cutoff
              AND (naechste_pruefung_am >= :today OR naechste_pruefung_am IS NULL)
            ORDER BY naechste_pruefung_am ASC NULLS FIRST
        """),
        {"tenant_id": tenant_id, "cutoff": cutoff, "today": today},
    ).mappings().all()
    return [dict(r) for r in rows]


def berechne_naechste_vvvo_pruefung(
    db: Session,
    vvvo_id: str,
    tenant_id: str,
    pruefung_am: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Aktualisiert letzte_pruefung_am und berechnet naechste_pruefung_am (+ 365 Tage)."""
    row = db.execute(
        text("SELECT * FROM domain_compliance.compliance_vvvo_register WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": vvvo_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise VVVOError(f"VVVO-Eintrag {vvvo_id} nicht gefunden")

    pruef_date = date.fromisoformat(pruefung_am)
    naechste = pruef_date + timedelta(days=VVVO_PRUEF_INTERVAL_DAYS)

    updated = db.execute(
        text("""
            UPDATE domain_compliance.compliance_vvvo_register
            SET letzte_pruefung_am = :pruefung_am,
                naechste_pruefung_am = :naechste
            WHERE id = :id AND tenant_id = :tenant_id
            RETURNING *
        """),
        {"pruefung_am": pruefung_am, "naechste": naechste.isoformat(), "id": vvvo_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not updated:
        raise VVVOError(f"VVVO-Eintrag {vvvo_id} nicht gefunden")
    db.commit()
    logger.info("vvvo %s: Prüfung %s, nächste %s", vvvo_id, pruefung_am, naechste)
    return {
        **dict(updated),
        "letzte_pruefung_am": pruefung_am,
        "naechste_pruefung_am": naechste.isoformat(),
    }


def list_ablaufende_sachkunde(
    db: Session,
    tenant_id: str,
    within_days: int = DEFAULT_ALARM_DAYS,
) -> List[Dict[str, Any]]:
    """Listet Sachkunde-Zertifikate, die innerhalb von `within_days` Tagen ablaufen."""
    cutoff = (date.today() + timedelta(days=within_days)).isoformat()
    today = date.today().isoformat()
    rows = db.execute(
        text("""
            SELECT id, tenant_id, mitarbeiter_name, zertifikat_art,
                   zertifikat_nummer, ablauf_datum
            FROM domain_compliance.compliance_sachkunde_register
            WHERE tenant_id = :tenant_id
              AND ablauf_datum <= :cutoff
              AND ablauf_datum >= :today
            ORDER BY ablauf_datum ASC
        """),
        {"tenant_id": tenant_id, "cutoff": cutoff, "today": today},
    ).mappings().all()
    return [dict(r) for r in rows]


def get_sachkunde_status(
    db: Session,
    sachkunde_id: str,
    tenant_id: str,
) -> Dict[str, Any]:
    """Gibt Sachkunde-Status mit Gültigkeits-Flag zurück."""
    row = db.execute(
        text("SELECT * FROM domain_compliance.compliance_sachkunde_register WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": sachkunde_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise VVVOError(f"Sachkunde-Eintrag {sachkunde_id} nicht gefunden")

    ablauf = row.get("ablauf_datum")
    heute = date.today()
    gueltig = True
    tage_bis_ablauf: Optional[int] = None
    if ablauf:
        ablauf_date = date.fromisoformat(str(ablauf)) if isinstance(ablauf, str) else ablauf
        delta = (ablauf_date - heute).days
        tage_bis_ablauf = delta
        gueltig = delta >= 0

    return {
        **dict(row),
        "gueltig": gueltig,
        "tage_bis_ablauf": tage_bis_ablauf,
        "alarm": (tage_bis_ablauf is not None and 0 <= tage_bis_ablauf <= DEFAULT_ALARM_DAYS),
    }
