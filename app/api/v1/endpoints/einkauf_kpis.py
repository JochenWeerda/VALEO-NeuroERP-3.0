"""
Einkauf — KPIs

GET /einkauf/kpis
  Query: date_from, date_to
  Berechnet:
  - on_time_delivery_rate
  - fill_rate
  - price_variance
  - avg_lead_time_days
  - top_5_suppliers_by_spend
  - abc_analysis
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/einkauf", tags=["einkauf", "kpi"])


@router.get("/kpis")
def get_kpis(
    date_from: Optional[str] = Query(None, description="ISO-Datum, z.B. 2026-01-01"),
    date_to: Optional[str] = Query(None, description="ISO-Datum, z.B. 2026-12-31"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Einkaufs-KPIs berechnen.

    Alle Teilberechnungen per try/except abgesichert — fehlende Tabellen liefern None.
    """

    date_params: dict[str, Any] = {
        "tid": tenant_id,
        "date_from": date_from or "1900-01-01",
        "date_to": date_to or "2999-12-31",
    }

    # ── On-Time Delivery Rate ──────────────────────────────────────────────
    on_time_delivery_rate: Optional[float] = None
    try:
        row = db.execute(
            text("""
                SELECT
                    COUNT(*) FILTER (WHERE actual_delivery_date <= promised_delivery_date)::FLOAT
                        / NULLIF(COUNT(*), 0)
                FROM domain_einkauf.bestellungen
                WHERE tenant_id = :tid
                  AND bestelldatum BETWEEN :date_from::DATE AND :date_to::DATE
                  AND actual_delivery_date IS NOT NULL
            """),
            date_params,
        ).scalar()
        on_time_delivery_rate = float(row) if row is not None else None
    except Exception:
        pass

    # ── Fill Rate ─────────────────────────────────────────────────────────
    fill_rate: Optional[float] = None
    try:
        row = db.execute(
            text("""
                SELECT
                    SUM(gelieferte_menge)::FLOAT / NULLIF(SUM(bestellte_menge)::FLOAT, 0)
                FROM domain_einkauf.bestellung_positionen bp
                JOIN domain_einkauf.bestellungen b ON b.id = bp.bestellung_id
                WHERE b.tenant_id = :tid
                  AND b.bestelldatum BETWEEN :date_from::DATE AND :date_to::DATE
            """),
            date_params,
        ).scalar()
        fill_rate = float(row) if row is not None else None
    except Exception:
        pass

    # ── Price Variance ────────────────────────────────────────────────────
    price_variance: Optional[float] = None
    try:
        row = db.execute(
            text("""
                SELECT AVG((invoice_amount - po_amount) / NULLIF(po_amount, 0))
                FROM domain_einkauf.invoice_verification
                WHERE tenant_id = :tid
                  AND created_at BETWEEN :date_from::DATE AND :date_to::DATE
                  AND po_amount IS NOT NULL AND invoice_amount IS NOT NULL
            """),
            date_params,
        ).scalar()
        price_variance = float(row) if row is not None else None
    except Exception:
        pass

    # ── Avg Lead Time ─────────────────────────────────────────────────────
    avg_lead_time_days: Optional[float] = None
    try:
        row = db.execute(
            text("""
                SELECT AVG(EXTRACT(EPOCH FROM (actual_delivery_date::TIMESTAMPTZ
                           - bestelldatum::TIMESTAMPTZ)) / 86400)
                FROM domain_einkauf.bestellungen
                WHERE tenant_id = :tid
                  AND bestelldatum BETWEEN :date_from::DATE AND :date_to::DATE
                  AND actual_delivery_date IS NOT NULL
            """),
            date_params,
        ).scalar()
        avg_lead_time_days = round(float(row), 2) if row is not None else None
    except Exception:
        pass

    # ── Top-5 Suppliers by Spend ──────────────────────────────────────────
    top_5_suppliers: list[dict[str, Any]] = []
    try:
        rows = db.execute(
            text("""
                SELECT lieferant_id, SUM(gesamtbetrag) AS total_spend
                FROM domain_einkauf.bestellungen
                WHERE tenant_id = :tid
                  AND bestelldatum BETWEEN :date_from::DATE AND :date_to::DATE
                GROUP BY lieferant_id
                ORDER BY total_spend DESC
                LIMIT 5
            """),
            date_params,
        ).fetchall()
        top_5_suppliers = [
            {"supplier_id": str(r[0]), "total_spend": float(r[1])} for r in rows
        ]
    except Exception:
        pass

    # ── ABC-Analyse ───────────────────────────────────────────────────────
    abc_analysis: dict[str, Any] = {}
    try:
        rows = db.execute(
            text("""
                WITH supplier_spend AS (
                    SELECT lieferant_id, SUM(gesamtbetrag) AS spend
                    FROM domain_einkauf.bestellungen
                    WHERE tenant_id = :tid
                      AND bestelldatum BETWEEN :date_from::DATE AND :date_to::DATE
                    GROUP BY lieferant_id
                ),
                totals AS (SELECT SUM(spend) AS grand_total FROM supplier_spend),
                ranked AS (
                    SELECT lieferant_id, spend,
                           SUM(spend) OVER (ORDER BY spend DESC) AS running_total,
                           (SELECT grand_total FROM totals) AS grand_total
                    FROM supplier_spend
                ),
                classified AS (
                    SELECT lieferant_id, spend,
                           CASE
                               WHEN running_total / NULLIF(grand_total, 0) <= 0.8 THEN 'A'
                               WHEN running_total / NULLIF(grand_total, 0) <= 0.95 THEN 'B'
                               ELSE 'C'
                           END AS abc_class
                    FROM ranked
                )
                SELECT abc_class,
                       COUNT(*) AS supplier_count,
                       SUM(spend) AS class_spend,
                       (SELECT grand_total FROM totals) AS grand_total
                FROM classified
                GROUP BY abc_class
                ORDER BY abc_class
            """),
            date_params,
        ).fetchall()

        for r in rows:
            cls = r[0]
            grand = float(r[3]) if r[3] else 1.0
            abc_analysis[cls] = {
                "count": int(r[1]),
                "spend": float(r[2]) if r[2] else 0.0,
                "spend_percent": round(float(r[2]) / grand * 100, 2) if r[2] and grand else 0.0,
            }
    except Exception:
        pass

    return {
        "date_from": date_from,
        "date_to": date_to,
        "on_time_delivery_rate": on_time_delivery_rate,
        "fill_rate": fill_rate,
        "price_variance": price_variance,
        "avg_lead_time_days": avg_lead_time_days,
        "top_5_suppliers_by_spend": top_5_suppliers,
        "abc_analysis": abc_analysis,
    }
