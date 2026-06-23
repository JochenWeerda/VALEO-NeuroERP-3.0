"""DOM-FEED-PROD-004.3 — Rezeptur-Verwaltung (Freigabe + Versionierung)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_REZEPTUR_TRANSITIONS = {
    ("ENTWURF", "FREIGEGEBEN"),
    ("ENTWURF", "ARCHIVIERT"),
    ("FREIGEGEBEN", "ARCHIVIERT"),
    ("FREIGEGEBEN", "GESPERRT"),
    ("GESPERRT", "FREIGEGEBEN"),
    ("GESPERRT", "ARCHIVIERT"),
}


class RezepturError(Exception):
    pass


def create_rezeptur(
    db: Session,
    tenant_id: str,
    rezeptur_nr: str,
    artikel_id: str,
    bezeichnung: str,
    positionen: List[Dict[str, Any]],
    operator: str = "system",
) -> Dict[str, Any]:
    existing = db.execute(
        text("""
            SELECT * FROM domain_futtermittel.feed_rezepturen
            WHERE rezeptur_nr = :rnr AND tenant_id = :tid AND status != 'ARCHIVIERT'
        """),
        {"rnr": rezeptur_nr, "tid": tenant_id},
    ).mappings().first()
    if existing:
        return dict(existing)

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_futtermittel.feed_rezepturen
                (id, tenant_id, rezeptur_nr, artikel_id, bezeichnung,
                 version, status, operator, created_at)
            VALUES (:id, :tenant_id, :rezeptur_nr, :artikel_id, :bezeichnung,
                    1, 'ENTWURF', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "rezeptur_nr": rezeptur_nr,
            "artikel_id": artikel_id,
            "bezeichnung": bezeichnung,
            "operator": operator,
        },
    )
    for pos in positionen:
        db.execute(
            text("""
                INSERT INTO domain_futtermittel.feed_rezeptur_positionen
                    (id, rezeptur_id, tenant_id, rohware_id, anteil_pct, created_at)
                VALUES (:id, :rid, :tid, :rohware_id, :anteil_pct, NOW())
            """),
            {
                "id": str(uuid.uuid4()),
                "rid": rec_id,
                "tid": tenant_id,
                "rohware_id": pos["rohware_id"],
                "anteil_pct": pos["anteil_pct"],
            },
        )
    db.commit()
    return _fetch_rezeptur(db, rec_id)


def _fetch_rezeptur(db: Session, rezeptur_id: str) -> Dict[str, Any]:
    row = db.execute(
        text("SELECT * FROM domain_futtermittel.feed_rezepturen WHERE id = :id"),
        {"id": rezeptur_id},
    ).mappings().first()
    if not row:
        raise RezepturError(f"Rezeptur {rezeptur_id} nicht gefunden")
    result = dict(row)
    positionen = db.execute(
        text("""
            SELECT * FROM domain_futtermittel.feed_rezeptur_positionen
            WHERE rezeptur_id = :rid
        """),
        {"rid": rezeptur_id},
    ).mappings().all()
    result["positionen"] = [dict(p) for p in positionen]
    # Summencheck
    result["anteil_summe_pct"] = sum(p["anteil_pct"] for p in result["positionen"])
    return result


def transition_rezeptur(
    db: Session,
    rezeptur_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
) -> Dict[str, Any]:
    row = db.execute(
        text("""
            SELECT * FROM domain_futtermittel.feed_rezepturen
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": rezeptur_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise RezepturError(f"Rezeptur {rezeptur_id} nicht gefunden")
    old_status = row["status"]
    if (old_status, new_status) not in VALID_REZEPTUR_TRANSITIONS:
        raise RezepturError(f"Ungültiger Übergang {old_status} → {new_status}")

    # Freigabe: Summe muss 100% ergeben
    if new_status == "FREIGEGEBEN":
        summe = db.execute(
            text("""
                SELECT COALESCE(SUM(anteil_pct), 0)
                FROM domain_futtermittel.feed_rezeptur_positionen
                WHERE rezeptur_id = :rid
            """),
            {"rid": rezeptur_id},
        ).scalar() or 0.0
        if abs(summe - 100.0) > 0.01:
            raise RezepturError(
                f"Rezeptur-Anteile summieren sich auf {summe}% (erwartet: 100%)"
            )

    db.execute(
        text("""
            UPDATE domain_futtermittel.feed_rezepturen
            SET status = :new_status, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        {"new_status": new_status, "id": rezeptur_id, "tid": tenant_id},
    )
    db.commit()
    return _fetch_rezeptur(db, rezeptur_id)
