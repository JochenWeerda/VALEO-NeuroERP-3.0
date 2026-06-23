"""DOM-PROC-004.4 — Rechnungsprüfung + ERS (Evaluated Receipt Settlement) Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

DEFAULT_SCHWELLE_PCT = 3.0


class RechnungspruefungError(Exception):
    """Raised when Rechnungsprüfung constraints are violated."""


def pruefe_rechnung(
    db: Session,
    bestellung_id: str,
    tenant_id: str,
    rechnungs_nr: str,
    rechnungs_betrag_eur: float,
    bestell_preis_eur: float,
    we_menge: float,
    schwelle_pct: float = DEFAULT_SCHWELLE_PCT,
) -> Dict[str, Any]:
    """3-Way-Match: Bestellwert vs. WE-Menge vs. Rechnungsbetrag (idempotent via bestellung_id + rechnungs_nr)."""
    if bestell_preis_eur <= 0 or we_menge <= 0:
        raise RechnungspruefungError("Bestellpreis und WE-Menge müssen positiv sein")

    # idempotency
    existing = db.execute(
        text("""
            SELECT * FROM domain_procurement.proc_rechnungspruefungen
            WHERE bestellung_id = :bid AND rechnungs_nr = :rnr AND tenant_id = :tid
        """),
        {"bid": bestellung_id, "rnr": rechnungs_nr, "tid": tenant_id},
    ).mappings().first()
    if existing:
        return {**dict(existing), "idempotent": True}

    soll_betrag = bestell_preis_eur * we_menge
    abweichung_abs = abs(rechnungs_betrag_eur - soll_betrag)
    abweichung_pct = round(abweichung_abs / soll_betrag * 100, 4) if soll_betrag > 0 else 0.0

    status = "FREIGEGEBEN" if abweichung_pct <= schwelle_pct else "GESPERRT"

    entry_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_procurement.proc_rechnungspruefungen
                (id, bestellung_id, tenant_id, rechnungs_nr, bestell_wert_eur,
                 we_menge, rechnungs_betrag_eur, abweichung_pct, status, created_at)
            VALUES (:id, :bid, :tid, :rnr, :bestell_wert, :we_menge, :rechnungs_betrag,
                    :abweichung_pct, :status, NOW())
        """),
        {
            "id": entry_id, "bid": bestellung_id, "tid": tenant_id,
            "rnr": rechnungs_nr, "bestell_wert": soll_betrag,
            "we_menge": we_menge, "rechnungs_betrag": rechnungs_betrag_eur,
            "abweichung_pct": abweichung_pct, "status": status,
        },
    )
    db.commit()
    logger.info("rechnungspruefung %s/%s: %.4f%% → %s", bestellung_id, rechnungs_nr, abweichung_pct, status)
    return {
        "id": entry_id, "bestellung_id": bestellung_id, "rechnungs_nr": rechnungs_nr,
        "soll_betrag_eur": soll_betrag, "rechnungs_betrag_eur": rechnungs_betrag_eur,
        "abweichung_pct": abweichung_pct, "status": status, "idempotent": False,
    }


def freigabe_rechnungspruefung(
    db: Session,
    pruefung_id: str,
    tenant_id: str,
    entscheidung: str,
    operator: str,
    grund: Optional[str] = None,
) -> Dict[str, Any]:
    """Gibt eine gesperrte Rechnungsprüfung manuell frei oder lehnt sie ab."""
    if entscheidung.upper() not in {"FREIGEGEBEN", "ABGELEHNT"}:
        raise RechnungspruefungError(f"Ungültige Entscheidung: {entscheidung}")

    row = db.execute(
        text("SELECT * FROM domain_procurement.proc_rechnungspruefungen WHERE id = :id"),
        {"id": pruefung_id},
    ).mappings().first()
    if not row:
        raise RechnungspruefungError(f"Rechnungsprüfung {pruefung_id} nicht gefunden")
    if row["tenant_id"] != tenant_id:
        raise RechnungspruefungError(f"Rechnungsprüfung {pruefung_id} gehört nicht zu Tenant {tenant_id}")
    if row["status"] != "GESPERRT":
        raise RechnungspruefungError(
            f"Manuelle Freigabe nur für GESPERRT möglich (aktuell: {row['status']})"
        )

    db.execute(
        text("""
            UPDATE domain_procurement.proc_rechnungspruefungen
            SET status = :status, freigabe_operator = :operator, freigabe_grund = :grund
            WHERE id = :id
        """),
        {"status": entscheidung.upper(), "operator": operator, "grund": grund, "id": pruefung_id},
    )
    db.commit()
    logger.info("rechnungspruefung %s: GESPERRT → %s von %s", pruefung_id, entscheidung, operator)
    return {**dict(row), "status": entscheidung.upper(), "freigabe_operator": operator}
