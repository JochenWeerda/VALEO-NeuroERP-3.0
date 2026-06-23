"""DOM-CONTROLLING-004.3 — Plan/Ist-Abweichungsanalyse Service."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

AMPEL_GRUEN_PCT = 5.0
AMPEL_GELB_PCT = 15.0


def _ampel(abweichung_pct: float) -> str:
    abs_pct = abs(abweichung_pct)
    if abs_pct <= AMPEL_GRUEN_PCT:
        return "GRUEN"
    if abs_pct <= AMPEL_GELB_PCT:
        return "GELB"
    return "ROT"


def get_abweichung(
    db: Session,
    tenant_id: str,
    kostenstelle_id: str,
    periode: str,
) -> Dict[str, Any]:
    """Plan/Ist-Abweichung für eine Kostenstelle + Periode."""
    budget = db.execute(
        text("""
            SELECT plan_eur FROM domain_controlling.controlling_budgets
            WHERE tenant_id = :tid AND kostenstelle_id = :kst AND periode = :periode
              AND status IN ('AKTIV', 'ABGESCHLOSSEN')
            ORDER BY created_at DESC LIMIT 1
        """),
        {"tid": tenant_id, "kst": kostenstelle_id, "periode": periode},
    ).mappings().first()

    ist = db.execute(
        text("""
            SELECT COALESCE(SUM(ist_eur), 0) AS ist_eur
            FROM domain_controlling.controlling_ist_werte
            WHERE tenant_id = :tid AND kostenstelle_id = :kst AND periode = :periode
        """),
        {"tid": tenant_id, "kst": kostenstelle_id, "periode": periode},
    ).mappings().first()

    ist_eur = float(ist["ist_eur"]) if ist else 0.0

    if not budget:
        return {
            "kostenstelle_id": kostenstelle_id,
            "periode": periode,
            "plan_eur": None,
            "ist_eur": ist_eur,
            "abweichung_eur": None,
            "abweichung_pct": None,
            "ampel": "KEIN_PLAN",
        }

    plan_eur = float(budget["plan_eur"])
    abweichung_eur = ist_eur - plan_eur
    abweichung_pct = round(abweichung_eur / plan_eur * 100, 4) if plan_eur != 0 else 0.0

    return {
        "kostenstelle_id": kostenstelle_id,
        "periode": periode,
        "plan_eur": plan_eur,
        "ist_eur": ist_eur,
        "abweichung_eur": round(abweichung_eur, 2),
        "abweichung_pct": abweichung_pct,
        "ampel": _ampel(abweichung_pct),
    }


def buche_ist_wert(
    db: Session,
    tenant_id: str,
    kostenstelle_id: str,
    periode: str,
    ist_eur: float,
    buchungsref: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Bucht einen Ist-Wert für eine Kostenstelle (fail-closed wenn Periode abgeschlossen)."""
    import uuid
    # check if period is closed
    closed = db.execute(
        text("""
            SELECT id FROM domain_controlling.controlling_kst_abschluss
            WHERE tenant_id = :tid AND kostenstelle_id = :kst AND periode = :periode
              AND status = 'ABGESCHLOSSEN'
        """),
        {"tid": tenant_id, "kst": kostenstelle_id, "periode": periode},
    ).mappings().first()

    if closed:
        raise ValueError(
            f"Kostenstelle {kostenstelle_id} Periode {periode} ist abgeschlossen — keine neuen Ist-Buchungen"
        )

    entry_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_controlling.controlling_ist_werte
                (id, tenant_id, kostenstelle_id, periode, ist_eur, buchungsref, created_at)
            VALUES (:id, :tid, :kst, :periode, :ist_eur, :buchungsref, NOW())
        """),
        {
            "id": entry_id, "tid": tenant_id, "kst": kostenstelle_id,
            "periode": periode, "ist_eur": ist_eur, "buchungsref": buchungsref,
        },
    )
    db.commit()
    logger.info("ist_wert %s: KST=%s Periode=%s Betrag=%.2f", entry_id, kostenstelle_id, periode, ist_eur)
    return {
        "id": entry_id, "kostenstelle_id": kostenstelle_id,
        "periode": periode, "ist_eur": ist_eur, "buchungsref": buchungsref,
    }


def list_abweichungen_drill_down(
    db: Session,
    tenant_id: str,
    periode: str,
) -> List[Dict[str, Any]]:
    """Drill-Down: Abweichungsanalyse für alle Kostenstellen einer Periode."""
    budgets = db.execute(
        text("""
            SELECT DISTINCT kostenstelle_id FROM domain_controlling.controlling_budgets
            WHERE tenant_id = :tid AND periode = :periode AND status IN ('AKTIV', 'ABGESCHLOSSEN')
        """),
        {"tid": tenant_id, "periode": periode},
    ).mappings().all()

    return [
        get_abweichung(db, tenant_id, row["kostenstelle_id"], periode)
        for row in budgets
    ]
