"""DOM-CON-004.3 — Kontrakt Preis-Fixing Service (MATIF/Kassamarkt)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class KontraktFixingError(Exception):
    pass


def create_fixing(
    db: Session,
    kontrakt_id: str,
    tenant_id: str,
    fixing_datum: str,
    fixing_preis_eur_t: float,
    menge_t: float,
    markt: str,  # "MATIF" | "KASSA"
    referenz: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Legt einen Preis-Fixing-Eintrag für einen Kontrakt an."""
    from sqlalchemy import text

    # Summe bereits gefixte Menge prüfen
    gefixte_menge = db.execute(
        text("""
            SELECT COALESCE(SUM(menge_t), 0)
            FROM domain_kontrakte.kontrakt_fixings
            WHERE kontrakt_id = :kid AND tenant_id = :tid
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).scalar() or 0.0

    # Kontraktmenge laden
    kontrakt = db.execute(
        text("""
            SELECT menge_t FROM domain_kontrakte.kontrakt_lifecycle
            WHERE kontrakt_id = :kid AND tenant_id = :tid
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).mappings().first()
    if not kontrakt:
        raise KontraktFixingError(f"Kontrakt {kontrakt_id} nicht gefunden")
    if gefixte_menge + menge_t > kontrakt["menge_t"]:
        raise KontraktFixingError(
            f"Fixing-Menge {menge_t}t übersteigt verbleibende Restmenge "
            f"{kontrakt['menge_t'] - gefixte_menge}t"
        )

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_kontrakte.kontrakt_fixings
                (id, kontrakt_id, tenant_id, fixing_datum, fixing_preis_eur_t,
                 menge_t, markt, referenz, operator, created_at)
            VALUES (:id, :kontrakt_id, :tenant_id, :fixing_datum, :fixing_preis_eur_t,
                    :menge_t, :markt, :referenz, :operator, NOW())
        """),
        {
            "id": rec_id,
            "kontrakt_id": kontrakt_id,
            "tenant_id": tenant_id,
            "fixing_datum": fixing_datum,
            "fixing_preis_eur_t": fixing_preis_eur_t,
            "menge_t": menge_t,
            "markt": markt,
            "referenz": referenz,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_kontrakte.kontrakt_fixings WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def get_fixing_summary(
    db: Session,
    kontrakt_id: str,
    tenant_id: str,
) -> Dict[str, Any]:
    """Gibt Fixing-Zusammenfassung zurück: Gesamtmenge, Durchschnittspreis, offene Restmenge."""
    rows = db.execute(
        text("""
            SELECT fixing_preis_eur_t, menge_t
            FROM domain_kontrakte.kontrakt_fixings
            WHERE kontrakt_id = :kid AND tenant_id = :tid
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).mappings().all()

    kontrakt = db.execute(
        text("""
            SELECT menge_t FROM domain_kontrakte.kontrakt_lifecycle
            WHERE kontrakt_id = :kid AND tenant_id = :tid
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).mappings().first()

    total_menge = sum(r["menge_t"] for r in rows)
    if total_menge > 0:
        avg_preis = sum(r["fixing_preis_eur_t"] * r["menge_t"] for r in rows) / total_menge
    else:
        avg_preis = 0.0

    kontrakt_menge = kontrakt["menge_t"] if kontrakt else 0.0
    return {
        "kontrakt_id": kontrakt_id,
        "gefixte_menge_t": total_menge,
        "offene_menge_t": kontrakt_menge - total_menge,
        "avg_fixing_preis_eur_t": round(avg_preis, 4),
        "anzahl_fixings": len(rows),
        "vollstaendig_gefixt": total_menge >= kontrakt_menge,
    }
