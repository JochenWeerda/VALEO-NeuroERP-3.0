"""DOM-FINANCE-004.3 — Ratenzahlungsplan-Lifecycle Service."""
from __future__ import annotations

import logging
import uuid
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class RatenzahlungError(Exception):
    """Raised when Ratenzahlung constraints are violated."""


def _fetch_plan(db: Session, plan_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_finance.finance_ratenzahlungsplaene WHERE id = :id"),
        {"id": plan_id},
    ).mappings().first()
    return dict(row) if row else None


def create_ratenzahlungsplan(
    db: Session,
    tenant_id: str,
    op_id: str,
    gesamt_eur: float,
    anzahl_raten: int,
    erste_faelligkeit: str,
) -> Dict[str, Any]:
    """Erstellt einen Ratenzahlungsplan für eine offene Position (idempotent via op_id)."""
    if anzahl_raten < 2:
        raise RatenzahlungError("Mindestens 2 Raten erforderlich")
    if gesamt_eur <= 0:
        raise RatenzahlungError("Gesamtbetrag muss positiv sein")

    # idempotency check
    existing = db.execute(
        text("SELECT * FROM domain_finance.finance_ratenzahlungsplaene WHERE op_id = :op_id AND tenant_id = :tenant_id"),
        {"op_id": op_id, "tenant_id": tenant_id},
    ).mappings().first()
    if existing:
        return {**dict(existing), "idempotent": True}

    plan_id = str(uuid.uuid4())
    rate_eur = round(gesamt_eur / anzahl_raten, 2)
    # last rate adjusts for rounding
    raten_betraege = [rate_eur] * (anzahl_raten - 1)
    raten_betraege.append(round(gesamt_eur - sum(raten_betraege), 2))

    db.execute(
        text("""
            INSERT INTO domain_finance.finance_ratenzahlungsplaene
                (id, tenant_id, op_id, gesamt_eur, anzahl_raten, restbetrag_eur, status, created_at)
            VALUES (:id, :tenant_id, :op_id, :gesamt_eur, :anzahl_raten, :gesamt_eur, 'AKTIV', NOW())
        """),
        {"id": plan_id, "tenant_id": tenant_id, "op_id": op_id,
         "gesamt_eur": gesamt_eur, "anzahl_raten": anzahl_raten},
    )

    erste = date.fromisoformat(erste_faelligkeit)
    rate_ids = []
    for i, betrag in enumerate(raten_betraege):
        rate_id = str(uuid.uuid4())
        faellig = (erste + timedelta(days=30 * i)).isoformat()
        db.execute(
            text("""
                INSERT INTO domain_finance.finance_ratenzahlungsraten
                    (id, plan_id, tenant_id, rate_nr, betrag_eur, faellig_am, status)
                VALUES (:id, :plan_id, :tenant_id, :rate_nr, :betrag_eur, :faellig_am, 'OFFEN')
            """),
            {"id": rate_id, "plan_id": plan_id, "tenant_id": tenant_id,
             "rate_nr": i + 1, "betrag_eur": betrag, "faellig_am": faellig},
        )
        rate_ids.append(rate_id)

    db.commit()
    logger.info("ratenzahlungsplan created: %s, %d Raten, %.2f EUR", plan_id, anzahl_raten, gesamt_eur)
    return {
        "id": plan_id, "op_id": op_id, "gesamt_eur": gesamt_eur,
        "anzahl_raten": anzahl_raten, "restbetrag_eur": gesamt_eur,
        "status": "AKTIV", "rate_ids": rate_ids, "idempotent": False,
    }


def buche_rate(
    db: Session,
    rate_id: str,
    tenant_id: str,
    bezahlt_am: Optional[str] = None,
) -> Dict[str, Any]:
    """Bucht eine Ratenzahlungsrate als bezahlt und reduziert den Restbetrag des Plans."""
    rate = db.execute(
        text("SELECT * FROM domain_finance.finance_ratenzahlungsraten WHERE id = :id"),
        {"id": rate_id},
    ).mappings().first()
    if not rate:
        raise RatenzahlungError(f"Rate {rate_id} nicht gefunden")
    if rate["tenant_id"] != tenant_id:
        raise RatenzahlungError(f"Rate {rate_id} gehört nicht zu Tenant {tenant_id}")
    if rate["status"] == "BEZAHLT":
        return {**dict(rate), "idempotent": True}

    datum = bezahlt_am or date.today().isoformat()
    db.execute(
        text("UPDATE domain_finance.finance_ratenzahlungsraten SET status = 'BEZAHLT', bezahlt_am = :datum WHERE id = :id"),
        {"datum": datum, "id": rate_id},
    )

    plan_id = rate["plan_id"]
    plan = _fetch_plan(db, plan_id)
    if not plan:
        raise RatenzahlungError(f"Plan {plan_id} nicht gefunden")

    neuer_rest = round(float(plan["restbetrag_eur"]) - float(rate["betrag_eur"]), 2)
    if neuer_rest < 0:
        neuer_rest = 0.0

    new_plan_status = "ABGESCHLOSSEN" if neuer_rest == 0.0 else "AKTIV"
    db.execute(
        text("""
            UPDATE domain_finance.finance_ratenzahlungsplaene
            SET restbetrag_eur = :rest, status = :status
            WHERE id = :id
        """),
        {"rest": neuer_rest, "status": new_plan_status, "id": plan_id},
    )
    db.commit()
    logger.info("rate %s bezahlt, restbetrag %.2f, plan_status %s", rate_id, neuer_rest, new_plan_status)
    return {
        **dict(rate), "status": "BEZAHLT", "bezahlt_am": datum,
        "plan_restbetrag_eur": neuer_rest, "plan_status": new_plan_status, "idempotent": False,
    }
