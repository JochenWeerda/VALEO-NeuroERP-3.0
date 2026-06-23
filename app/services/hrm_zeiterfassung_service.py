"""DOM-HRM-004.2 — HRM Zeiterfassung Lifecycle (Einstempeln/Ausstempeln/Korrektur)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_ZEITBUCHUNG_TRANSITIONS = {
    ("OFFEN", "GEBUCHT"),
    ("GEBUCHT", "KORRIGIERT"),
    ("GEBUCHT", "STORNIERT"),
    ("KORRIGIERT", "GEBUCHT"),
    ("KORRIGIERT", "STORNIERT"),
}


class ZeiterfassungError(Exception):
    pass


def create_zeitbuchung(
    db: Session,
    tenant_id: str,
    mitarbeiter_id: str,
    datum: str,
    von_zeit: str,
    bis_zeit: str,
    taetigkeit: str,
    kostenstelle_id: str,
    operator: str = "system",
) -> Dict[str, Any]:
    stunden = _berechne_stunden(von_zeit, bis_zeit)
    if stunden <= 0:
        raise ZeiterfassungError(f"Ungültige Zeitspanne: {von_zeit}–{bis_zeit}")

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_hrm.hrm_zeitbuchungen
                (id, tenant_id, mitarbeiter_id, datum, von_zeit, bis_zeit,
                 stunden, taetigkeit, kostenstelle_id, status, operator, created_at)
            VALUES (:id, :tenant_id, :mitarbeiter_id, :datum, :von_zeit, :bis_zeit,
                    :stunden, :taetigkeit, :kostenstelle_id, 'OFFEN', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "mitarbeiter_id": mitarbeiter_id,
            "datum": datum,
            "von_zeit": von_zeit,
            "bis_zeit": bis_zeit,
            "stunden": stunden,
            "taetigkeit": taetigkeit,
            "kostenstelle_id": kostenstelle_id,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hrm.hrm_zeitbuchungen WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def _berechne_stunden(von: str, bis: str) -> float:
    from datetime import datetime
    fmt = "%H:%M"
    try:
        t_von = datetime.strptime(von, fmt)
        t_bis = datetime.strptime(bis, fmt)
        diff = (t_bis - t_von).total_seconds() / 3600
        return round(diff, 2)
    except ValueError:
        return -1.0


def transition_zeitbuchung(
    db: Session,
    buchung_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    korrektur_grund: str = "",
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_hrm.hrm_zeitbuchungen
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": buchung_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise ZeiterfassungError(f"Zeitbuchung {buchung_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_ZEITBUCHUNG_TRANSITIONS:
        raise ZeiterfassungError(f"Ungültiger Übergang {old_status} → {new_status}")

    db.execute(
        text("""
            UPDATE domain_hrm.hrm_zeitbuchungen
            SET status = :new_status, korrektur_grund = :grund, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        {
            "new_status": new_status,
            "grund": korrektur_grund,
            "id": buchung_id,
            "tid": tenant_id,
        },
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_hrm.hrm_zeitbuchungen WHERE id = :id"),
        {"id": buchung_id},
    ).mappings().first()
    return dict(updated)


def get_arbeitszeitkonto(
    db: Session,
    mitarbeiter_id: str,
    tenant_id: str,
    monat: str,
) -> Dict[str, Any]:
    """Berechnet Soll/Ist-Stunden-Konto für einen Monat."""
    ist_stunden = db.execute(
        text("""
            SELECT COALESCE(SUM(stunden), 0)
            FROM domain_hrm.hrm_zeitbuchungen
            WHERE mitarbeiter_id = :mid AND tenant_id = :tid
              AND datum LIKE :monat_prefix AND status = 'GEBUCHT'
        """),
        {"mid": mitarbeiter_id, "tid": tenant_id, "monat_prefix": f"{monat}%"},
    ).scalar() or 0.0

    soll_stunden = db.execute(
        text("""
            SELECT COALESCE(soll_stunden_monat, 168.0)
            FROM domain_hrm.hrm_mitarbeiter_konten
            WHERE mitarbeiter_id = :mid AND tenant_id = :tid
        """),
        {"mid": mitarbeiter_id, "tid": tenant_id},
    ).scalar() or 168.0

    return {
        "mitarbeiter_id": mitarbeiter_id,
        "monat": monat,
        "ist_stunden": ist_stunden,
        "soll_stunden": soll_stunden,
        "differenz": round(ist_stunden - soll_stunden, 2),
        "ampel": "gruen" if abs(ist_stunden - soll_stunden) <= 8 else "gelb" if abs(ist_stunden - soll_stunden) <= 20 else "rot",
    }
