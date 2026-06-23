"""DOM-MEL-004.2 — Meldewesen Lifecycle (Intrastat/ELSTER/ATLAS — extern gegated)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_MELDUNG_TRANSITIONS = {
    ("ENTWURF", "IN_PRUEFUNG"),
    ("ENTWURF", "STORNIERT"),
    ("IN_PRUEFUNG", "FREIGEGEBEN"),
    ("IN_PRUEFUNG", "FEHLER"),
    ("IN_PRUEFUNG", "STORNIERT"),
    ("FREIGEGEBEN", "UEBERMITTELT"),
    ("FREIGEGEBEN", "STORNIERT"),
    ("UEBERMITTELT", "BESTAETIGT"),
    ("UEBERMITTELT", "ABGELEHNT"),
    ("ABGELEHNT", "IN_PRUEFUNG"),
}

MELDUNG_TYPEN = {"INTRASTAT_EINGANG", "INTRASTAT_AUSGANG", "ELSTER_UMSATZSTEUER", "ATLAS_AUSFUHR"}


class MeldungError(Exception):
    pass


def create_meldung(
    db: Session,
    tenant_id: str,
    meldung_typ: str,
    periode: str,
    betrag_eur: float,
    waehrung: str,
    referenz_ids: List[str],
    operator: str = "system",
) -> Dict[str, Any]:
    if meldung_typ not in MELDUNG_TYPEN:
        raise MeldungError(f"Unbekannter Meldungs-Typ: {meldung_typ}")

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_meldewesen.meldungen
                (id, tenant_id, meldung_typ, periode, betrag_eur, waehrung,
                 anzahl_positionen, status, operator, created_at)
            VALUES (:id, :tenant_id, :meldung_typ, :periode, :betrag_eur, :waehrung,
                    :anzahl, 'ENTWURF', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "meldung_typ": meldung_typ,
            "periode": periode,
            "betrag_eur": betrag_eur,
            "waehrung": waehrung,
            "anzahl": len(referenz_ids),
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_meldewesen.meldungen WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_meldung(
    db: Session,
    meldung_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    fehler_grund: str = "",
    externe_referenz: str = "",
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_meldewesen.meldungen
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": meldung_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise MeldungError(f"Meldung {meldung_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_MELDUNG_TRANSITIONS:
        raise MeldungError(f"Ungültiger Übergang {old_status} → {new_status}")

    # Übermittelt → externe Bestätigung nötig (Hinweis, kein Block)
    hinweis = ""
    if new_status == "UEBERMITTELT":
        hinweis = "Externe Bestätigung durch Behörde steht aus"

    params: Dict[str, Any] = {
        "new_status": new_status,
        "id": meldung_id,
        "tid": tenant_id,
        "fehler_grund": fehler_grund,
    }
    extra = ""
    if externe_referenz:
        extra += ", externe_referenz = :ext_ref"
        params["ext_ref"] = externe_referenz

    db.execute(
        text(f"""
            UPDATE domain_meldewesen.meldungen
            SET status = :new_status, fehler_grund = :fehler_grund{extra}, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        params,
    )
    _log_meldung_event(db, meldung_id, tenant_id, old_status, new_status, operator, fehler_grund)
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_meldewesen.meldungen WHERE id = :id"),
        {"id": meldung_id},
    ).mappings().first()
    result = dict(updated)
    if hinweis:
        result["_hinweis"] = hinweis
    return result


def _log_meldung_event(
    db: Session,
    meldung_id: str,
    tenant_id: str,
    old_status: str,
    new_status: str,
    operator: str,
    fehler_grund: str = "",
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_meldewesen.meldung_log
                (id, meldung_id, tenant_id, old_status, new_status, operator, fehler_grund, created_at)
            VALUES (:id, :mid, :tid, :old, :new, :op, :fg, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "mid": meldung_id,
            "tid": tenant_id,
            "old": old_status,
            "new": new_status,
            "op": operator,
            "fg": fehler_grund,
        },
    )


def simulate_uebermittlung(
    meldung_typ: str,
    periode: str,
    betrag_eur: float,
) -> Dict[str, Any]:
    """Simulierte Übermittlung (kein echtes ELSTER/ATLAS — externes Gate)."""
    import hashlib
    ref = hashlib.sha256(f"{meldung_typ}:{periode}:{betrag_eur}".encode()).hexdigest()[:16]
    return {
        "simuliert": True,
        "externe_referenz": f"SIM-{meldung_typ[:3]}-{ref.upper()}",
        "hinweis": "Simulierte Übermittlung — keine echte Behördenbestätigung",
    }
