"""DOM-AGRAR-004.2 — Partie-Aggregations-Service (Ernteannahmen → Partie)."""
from __future__ import annotations

import logging
import uuid
from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

DEFAULT_PARTIE_PREFIX = "P"


class PartieError(Exception):
    """Raised when partie business rules are violated."""


def _generate_partie_number(db: Session, tenant_id: str) -> str:
    today = date.today().strftime("%Y%m%d")
    prefix = f"{DEFAULT_PARTIE_PREFIX}-{today}-"
    row = db.execute(
        text(
            "SELECT COUNT(*)::int AS cnt FROM domain_agrar.agrar_partien "
            "WHERE tenant_id = :tid AND partie_number LIKE :prefix"
        ),
        {"tid": tenant_id, "prefix": f"{prefix}%"},
    ).mappings().first()
    seq = int((row or {}).get("cnt") or 0) + 1
    return f"{prefix}{seq:03d}"


def _fetch_acceptance(db: Session, acceptance_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text(
            "SELECT id, tenant_id, gross_weight_kg, net_weight_kg, "
            "moisture_content_pct, impurity_pct, article_id "
            "FROM domain_agrar.harvest_acceptances WHERE id = :id"
        ),
        {"id": acceptance_id},
    ).mappings().first()
    return dict(row) if row else None


def create_partie(
    db: Session,
    tenant_id: str,
    acceptance_ids: List[str],
    campaign_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Aggregate multiple harvest acceptances into a Partie.

    Raises PartieError for: missing acceptance, cross-tenant, already-linked.
    """
    if not acceptance_ids:
        raise PartieError("Mindestens eine Annahme-ID erforderlich")

    acceptances: List[Dict[str, Any]] = []
    for aid in acceptance_ids:
        acc = _fetch_acceptance(db, aid, tenant_id)
        if not acc:
            raise PartieError(f"Ernteannahme {aid} nicht gefunden")
        if acc.get("tenant_id") and acc["tenant_id"] != tenant_id:
            raise PartieError(f"Annahme {aid} gehört nicht zu Tenant {tenant_id} (cross-tenant)")
        acceptances.append(acc)

    # duplicate guard: check if any acceptance already linked
    for aid in acceptance_ids:
        existing = db.execute(
            text(
                "SELECT partie_id FROM domain_agrar.agrar_partie_links "
                "WHERE acceptance_id = :aid AND tenant_id = :tid LIMIT 1"
            ),
            {"aid": aid, "tid": tenant_id},
        ).mappings().first()
        if existing:
            raise PartieError(
                f"Annahme {aid} ist bereits in Partie {existing['partie_id']} enthalten"
            )

    # aggregate
    total_gross_kg = sum(float(a.get("gross_weight_kg") or 0) for a in acceptances)
    total_net_kg = sum(float(a.get("net_weight_kg") or 0) for a in acceptances)

    # weighted average moisture
    moisture_sum = sum(
        float(a.get("moisture_content_pct") or 0) * float(a.get("gross_weight_kg") or 0)
        for a in acceptances
    )
    impurity_sum = sum(
        float(a.get("impurity_pct") or 0) * float(a.get("gross_weight_kg") or 0)
        for a in acceptances
    )
    avg_moisture = round(moisture_sum / total_gross_kg, 3) if total_gross_kg > 0 else 0.0
    avg_impurity = round(impurity_sum / total_gross_kg, 3) if total_gross_kg > 0 else 0.0

    # infer article_id from first acceptance
    article_id = acceptances[0].get("article_id") if acceptances else None

    partie_id = str(uuid.uuid4())
    partie_number = _generate_partie_number(db, tenant_id)

    db.execute(
        text("""
            INSERT INTO domain_agrar.agrar_partien
                (id, tenant_id, partie_number, article_id, campaign_id,
                 total_gross_kg, total_net_kg, avg_moisture_pct, avg_impurity_pct, status)
            VALUES (:id, :tenant_id, :partie_number, :article_id, :campaign_id,
                    :total_gross_kg, :total_net_kg, :avg_moisture_pct, :avg_impurity_pct, 'OFFEN')
        """),
        {
            "id": partie_id,
            "tenant_id": tenant_id,
            "partie_number": partie_number,
            "article_id": article_id,
            "campaign_id": campaign_id,
            "total_gross_kg": round(total_gross_kg, 3),
            "total_net_kg": round(total_net_kg, 3),
            "avg_moisture_pct": avg_moisture,
            "avg_impurity_pct": avg_impurity,
        },
    )
    for acc in acceptances:
        db.execute(
            text("""
                INSERT INTO domain_agrar.agrar_partie_links
                    (id, partie_id, acceptance_id, gross_kg, net_kg, tenant_id)
                VALUES (:id, :partie_id, :acceptance_id, :gross_kg, :net_kg, :tenant_id)
            """),
            {
                "id": str(uuid.uuid4()),
                "partie_id": partie_id,
                "acceptance_id": str(acc["id"]),
                "gross_kg": float(acc.get("gross_weight_kg") or 0),
                "net_kg": float(acc.get("net_weight_kg") or 0),
                "tenant_id": tenant_id,
            },
        )
    db.commit()
    logger.info("partie: created %s with %d acceptances", partie_number, len(acceptances))
    return {
        "id": partie_id,
        "partie_number": partie_number,
        "tenant_id": tenant_id,
        "article_id": article_id,
        "campaign_id": campaign_id,
        "total_gross_kg": round(total_gross_kg, 3),
        "total_net_kg": round(total_net_kg, 3),
        "avg_moisture_pct": avg_moisture,
        "avg_impurity_pct": avg_impurity,
        "status": "OFFEN",
        "acceptance_count": len(acceptances),
    }


def get_partie(db: Session, partie_id: str, tenant_id: str) -> Dict[str, Any]:
    """Fetch a Partie with its linked acceptances."""
    row = db.execute(
        text("SELECT * FROM domain_agrar.agrar_partien WHERE id = :id"),
        {"id": partie_id},
    ).mappings().first()
    if not row:
        raise PartieError(f"Partie {partie_id} nicht gefunden")
    partie = dict(row)
    if partie.get("tenant_id") and partie["tenant_id"] != tenant_id:
        raise PartieError(f"Partie {partie_id} gehört nicht zu Tenant {tenant_id}")
    links = db.execute(
        text("SELECT * FROM domain_agrar.agrar_partie_links WHERE partie_id = :pid"),
        {"pid": partie_id},
    ).mappings().all()
    partie["links"] = [dict(lnk) for lnk in links]
    return partie
