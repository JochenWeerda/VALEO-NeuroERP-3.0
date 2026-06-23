"""DOM-CON-004.4 — Kontrakt Settlement Service (Abrechnung + Storno)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_SETTLEMENT_TRANSITIONS = {
    ("OFFEN", "IN_ABRECHNUNG"),
    ("IN_ABRECHNUNG", "ABGERECHNET"),
    ("IN_ABRECHNUNG", "STORNIERT"),
    ("ABGERECHNET", "STORNIERT"),
}


class KontraktSettlementError(Exception):
    pass


def create_settlement(
    db: Session,
    kontrakt_id: str,
    tenant_id: str,
    lieferung_datum: str,
    gelieferte_menge_t: float,
    abrechnungspreis_eur_t: float,
    referenz: str,
    operator: str = "system",
) -> Dict[str, Any]:
    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_kontrakte.kontrakt_settlements
                (id, kontrakt_id, tenant_id, lieferung_datum, gelieferte_menge_t,
                 abrechnungspreis_eur_t, netto_eur, referenz, status, operator, created_at)
            VALUES (:id, :kontrakt_id, :tenant_id, :lieferung_datum, :gelieferte_menge_t,
                    :abrechnungspreis_eur_t, :netto_eur, :referenz, 'OFFEN', :operator, NOW())
        """),
        {
            "id": rec_id,
            "kontrakt_id": kontrakt_id,
            "tenant_id": tenant_id,
            "lieferung_datum": lieferung_datum,
            "gelieferte_menge_t": gelieferte_menge_t,
            "abrechnungspreis_eur_t": abrechnungspreis_eur_t,
            "netto_eur": round(gelieferte_menge_t * abrechnungspreis_eur_t, 2),
            "referenz": referenz,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_kontrakte.kontrakt_settlements WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_settlement(
    db: Session,
    settlement_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    storno_grund: str = "",
) -> Dict[str, Any]:
    row = db.execute(
        text("""
            SELECT * FROM domain_kontrakte.kontrakt_settlements
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": settlement_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise KontraktSettlementError(f"Settlement {settlement_id} nicht gefunden")
    old_status = row["status"]
    if (old_status, new_status) not in VALID_SETTLEMENT_TRANSITIONS:
        raise KontraktSettlementError(f"Ungültiger Übergang {old_status} → {new_status}")

    db.execute(
        text("""
            UPDATE domain_kontrakte.kontrakt_settlements
            SET status = :new_status, storno_grund = :storno_grund, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        {
            "new_status": new_status,
            "storno_grund": storno_grund,
            "id": settlement_id,
            "tid": tenant_id,
        },
    )
    # Update Kontrakt-Status wenn vollständig abgerechnet
    if new_status == "ABGERECHNET":
        _update_kontrakt_erfuellungsgrad(db, row["kontrakt_id"], tenant_id)
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_kontrakte.kontrakt_settlements WHERE id = :id"),
        {"id": settlement_id},
    ).mappings().first()
    return dict(updated)


def _update_kontrakt_erfuellungsgrad(
    db: Session, kontrakt_id: str, tenant_id: str
) -> None:
    """Prüft ob Kontrakt vollständig erfüllt ist und setzt Status."""
    kontrakt = db.execute(
        text("""
            SELECT menge_t FROM domain_kontrakte.kontrakt_lifecycle
            WHERE kontrakt_id = :kid AND tenant_id = :tid
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).mappings().first()
    if not kontrakt:
        return
    abgerechnet = db.execute(
        text("""
            SELECT COALESCE(SUM(gelieferte_menge_t), 0)
            FROM domain_kontrakte.kontrakt_settlements
            WHERE kontrakt_id = :kid AND tenant_id = :tid AND status = 'ABGERECHNET'
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).scalar() or 0.0

    neue_status = "TEIL_ERFUELLT" if abgerechnet < kontrakt["menge_t"] else "ERFUELLT"
    current = db.execute(
        text("""
            SELECT status FROM domain_kontrakte.kontrakt_lifecycle
            WHERE kontrakt_id = :kid AND tenant_id = :tid
        """),
        {"kid": kontrakt_id, "tid": tenant_id},
    ).scalar()
    if current == "AKTIV" or (current == "TEIL_ERFUELLT" and neue_status == "ERFUELLT"):
        db.execute(
            text("""
                UPDATE domain_kontrakte.kontrakt_lifecycle
                SET status = :s, updated_at = NOW()
                WHERE kontrakt_id = :kid AND tenant_id = :tid
            """),
            {"s": neue_status, "kid": kontrakt_id, "tid": tenant_id},
        )
