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

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema, TypedObjectOut
from app.api.v1.schemas.einkauf_kpis_schemas import EinkaufKpisOut


router = APIRouter(prefix="/einkauf", tags=["einkauf", "kpi"])

# Kennzahlen der Bestellung aus DocFlow, dem einzigen Belegspeicher (BELEG-052 S3).
_BESTELLUNGEN = """
    WITH po AS (
        SELECT h.id, h.supplier_id, h.total_net, h.document_date::date AS bestelldatum,
               CASE WHEN h.bausteine #>> '{lieferung,liefertermin}' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
                    THEN left(h.bausteine #>> '{lieferung,liefertermin}', 10)::date END AS zugesagt
        FROM domain_docflow.document_headers h
        WHERE h.tenant_id = :tid AND h.doc_type = 'purchase_order' AND h.deleted_at IS NULL
          AND h.status NOT IN ('draft', 'cancelled', 'reversed')
          AND h.document_date::date BETWEEN CAST(:date_from AS DATE) AND CAST(:date_to AS DATE)
    ),
    we AS (
        SELECT k.from_header_id AS po_id, MIN(z.document_date::date) AS erste_lieferung
        FROM domain_docflow.document_header_links k
        JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id
        WHERE k.tenant_id = :tid AND k.relation_type = 'order_to_receipt'
          AND k.from_header_id IN (SELECT id FROM po)
          AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed')
        GROUP BY k.from_header_id
    )
"""

_TERMIN_SQL = _BESTELLUNGEN + """
            SELECT COUNT(*) FILTER (WHERE we.erste_lieferung <= po.zugesagt)::FLOAT
                       / NULLIF(COUNT(*) FILTER (WHERE po.zugesagt IS NOT NULL), 0),
                   AVG(we.erste_lieferung - po.bestelldatum)
            FROM po JOIN we ON we.po_id = po.id
        """

_FUELLGRAD_SQL = _BESTELLUNGEN + """
            SELECT SUM(COALESCE(g.menge, 0))::FLOAT / NULLIF(SUM(i.quantity)::FLOAT, 0)
            FROM po
            JOIN domain_docflow.document_items i ON i.header_id = po.id AND i.tenant_id = :tid
            LEFT JOIN LATERAL (
                SELECT SUM(l.quantity_linked) AS menge
                FROM domain_docflow.document_links l
                JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id
                WHERE l.tenant_id = :tid AND l.from_item_id = i.id AND l.relation_type = 'order_to_receipt'
                  AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed')
            ) g ON TRUE
        """

_VOLUMEN_SQL = _BESTELLUNGEN + """
SELECT supplier_id, SUM(total_net) AS spend FROM po
WHERE supplier_id IS NOT NULL GROUP BY supplier_id ORDER BY spend DESC, supplier_id
LIMIT 10000
"""

# Offenes Bestellobligo (netto): was freigegebene Bestellungen noch an Ware erwarten, zum Bestellpreis. Stichtagswert
# ohne Zeitraum. Das Obligo ist ausserbilanziell (HGB) und wird deshalb nicht gebucht, sondern hier ausgewiesen.
_OBLIGO_SQL = """
SELECT COALESCE(SUM(GREATEST(i.quantity - COALESCE(g.menge, 0), 0) * i.unit_price
                    * (1 - COALESCE(i.discount_percent, 0) / 100)), 0)
FROM domain_docflow.document_headers h
JOIN domain_docflow.document_items i ON i.header_id = h.id AND i.tenant_id = h.tenant_id
LEFT JOIN LATERAL (
    SELECT SUM(l.quantity_linked) AS menge
    FROM domain_docflow.document_links l
    JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id
    WHERE l.tenant_id = h.tenant_id AND l.from_item_id = i.id AND l.relation_type = 'order_to_receipt'
      AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed')
) g ON TRUE
WHERE h.tenant_id = :tid AND h.doc_type = 'purchase_order' AND h.status = 'open' AND h.deleted_at IS NULL
"""


@router.get("/kpis", summary="Kpis abrufen",
    response_model=EinkaufKpisOut
)
def get_kpis(
    date_from: Optional[str] = Query(None, description="ISO-Datum, z.B. 2026-01-01"),
    date_to: Optional[str] = Query(None, description="ISO-Datum, z.B. 2026-12-31"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Einkaufs-KPIs berechnen.

    Bestellkennzahlen aus DocFlow; nur die Preisabweichung haengt an der Rechnungspruefung.
    """

    date_params: dict[str, Any] = {
        "tid": tenant_id,
        "date_from": date_from or "1900-01-01",
        "date_to": date_to or "2999-12-31",
    }

    # Quelle ist DocFlow, der einzige Belegspeicher (BELEG-052 S3). Bis 16.11.2026 fragten diese Kennzahlen
    # domain_einkauf.bestellungen nach Spalten, die es dort nie gab (actual_delivery_date, gesamtbetrag, ...): Jede
    # Abfrage scheiterte still und lieferte None.

    # ── Termintreue und Wiederbeschaffungszeit (erster Wareneingang je Bestellung) ─────────
    termin = db.execute(
        text(_TERMIN_SQL),
        date_params,
    ).one()
    on_time_delivery_rate: Optional[float] = float(termin[0]) if termin[0] is not None else None
    avg_lead_time_days: Optional[float] = round(float(termin[1]), 2) if termin[1] is not None else None

    # ── Fill Rate: in Wareneingaenge umgewandelte Menge / bestellte Menge ──────────────────
    row = db.execute(
        text(_FUELLGRAD_SQL),
        date_params,
    ).scalar()
    fill_rate: Optional[float] = float(row) if row is not None else None

    offenes_obligo = float(db.execute(text(_OBLIGO_SQL), {"tid": tenant_id}).scalar() or 0)

    # ── Price Variance ────────────────────────────────────────────────────
    price_variance: Optional[float] = None
    try:
        with db.begin_nested():
            row = db.execute(
                text("""
                    SELECT AVG((invoice_amount - po_amount) / NULLIF(po_amount, 0))
                    FROM domain_einkauf.invoice_verification
                    WHERE tenant_id = :tid
                      AND created_at BETWEEN CAST(:date_from AS DATE) AND CAST(:date_to AS DATE)
                      AND po_amount IS NOT NULL AND invoice_amount IS NOT NULL
                """),
                date_params,
            ).scalar()
        price_variance = float(row) if row is not None else None
    except Exception as e:  # noqa: BLE001 - Savepoint zurueckgerollt; die uebrigen Kennzahlen bleiben gueltig
        logger.debug("KPI-Abfrage nicht verfügbar (Tabelle fehlt oder Schema-Fehler): %s", e)

    # ── Einkaufsvolumen je Lieferant (netto): Top 5 und ABC ───────────────────────────────
    volumen = db.execute(
        text(_VOLUMEN_SQL),
        date_params,
    ).fetchmany(10000)  # je Lieferant eine Zeile, harte Obergrenze wie im SQL
    top_5_suppliers: list[dict[str, Any]] = [
        {"supplier_id": str(r[0]), "total_spend": float(r[1] or 0)} for r in volumen[:5]
    ]
    abc_analysis: dict[str, Any] = {}
    gesamt = sum(float(r[1] or 0) for r in volumen)
    laufend = 0.0
    for r in volumen:
        spend = float(r[1] or 0)
        laufend += spend
        anteil = laufend / gesamt if gesamt else 1.0
        klasse = "A" if anteil <= 0.8 else "B" if anteil <= 0.95 else "C"
        eintrag = abc_analysis.setdefault(klasse, {"count": 0, "spend": 0.0, "spend_percent": 0.0})
        eintrag["count"] += 1
        eintrag["spend"] += spend
    for eintrag in abc_analysis.values():
        eintrag["spend_percent"] = round(eintrag["spend"] / gesamt * 100, 2) if gesamt else 0.0

    return {
        "date_from": date_from,
        "date_to": date_to,
        "on_time_delivery_rate": on_time_delivery_rate,
        "fill_rate": fill_rate,
        "price_variance": price_variance,
        "avg_lead_time_days": avg_lead_time_days,
        "top_5_suppliers_by_spend": top_5_suppliers,
        "abc_analysis": abc_analysis,
        "offenes_bestellobligo_netto": offenes_obligo,
    }


@router.get("/audit-trail/{doc_type}/{doc_id}", response_model=TypedObjectOut, summary="Einkauf Audit-Trail abrufen")
async def get_einkauf_audit_trail(
    doc_type: str,
    doc_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Audit-Trail für Einkaufsdokument."""
    return {
        "doc_type": doc_type,
        "doc_id": doc_id,
        "events": [],
        "tenant_id": tenant_id,
    }
