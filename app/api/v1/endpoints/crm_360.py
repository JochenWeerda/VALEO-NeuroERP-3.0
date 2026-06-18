"""CRM 360°-Kundensicht — aggregiert echte ERP-Daten aus mehreren Domänen.

CRM-360-REAL-001: Alle Queries mit schema-qualifizierten Tabellennamen.
Fehlende Tabellen → leere Liste (kein silent-null), Kunde nicht gefunden → 404.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.crm_360_schemas import Crm360Out


router = APIRouter()


def _query_many(db: Session, sql: str, params: dict) -> list[dict]:
    """Schema-qualifizierte Query; gibt leere Liste bei Fehler zurück."""
    try:
        rows = db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        db.rollback()
        return []


def _query_one(db: Session, sql: str, params: dict) -> dict | None:
    try:
        row = db.execute(text(sql), params).mappings().first()
        return dict(row) if row else None
    except Exception:
        db.rollback()
        return None


@router.get("/{customer_id}/360", response_model=Crm360Out, tags=["crm", "customers"], summary="Customer 360 abrufen")
async def get_customer_360(
    customer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """360°-Kundensicht: aggregiert Aufträge, Rechnungen, OP, Kontrakte,
    Aktivitäten, Wareneingänge und Kreditlimit aus echten ERP-Tabellen."""

    # Kunde muss existieren (domain_erp.business_partners ist kanonisch)
    customer = _query_one(
        db,
        """
        SELECT id, name, kunden_nr
        FROM domain_erp.business_partners
        WHERE id = :cid AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")

    # 1. Letzte 10 Aufträge (domain_crm.sales_orders)
    orders = _query_many(
        db,
        """
        SELECT id, order_number, status,
               COALESCE(total_amount, 0)::float AS total_amount,
               created_at::text
        FROM domain_crm.sales_orders
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY created_at DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    # 2. Jahresumsatz (aktuelle 12 Monate) — Summe abgeschlossener Aufträge
    umsatz_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(total_amount), 0)::float AS jahresumsatz
        FROM domain_crm.sales_orders
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND status IN ('GELIEFERT', 'ABGESCHLOSSEN', 'BERECHNET')
          AND created_at >= NOW() - INTERVAL '12 months'
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    jahresumsatz = umsatz_row["jahresumsatz"] if umsatz_row else 0.0

    # 3. Offene Posten (domain_erp.open_items)
    open_payments = _query_many(
        db,
        """
        SELECT id, rechnungsnr, faelligkeit::text,
               offen::float AS amount,
               GREATEST(0, (CURRENT_DATE - faelligkeit::date))::int AS days_overdue,
               op_status
        FROM domain_erp.offene_posten
        WHERE (kunden_id = :cid OR debitor_id::text = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND op_status NOT IN ('bezahlt', 'storniert')
        ORDER BY faelligkeit ASC
        LIMIT 20
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    # Summe offener OP
    op_summe = sum(r.get("amount") or 0.0 for r in open_payments)

    # 4. Aktive Kontrakte (domain_agrar.agrar_contracts)
    active_contracts = _query_many(
        db,
        """
        SELECT id, contract_number, status,
               lieferbeginn::text AS start_date,
               lieferende::text AS end_date,
               COALESCE(gesamtmenge_t * preis_eur_per_t, 0)::float AS total_value
        FROM domain_agrar.agrar_contracts
        WHERE (customer_id = :cid OR lieferant_id = :cid OR partner_id = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND status IN ('AKTIV', 'aktiv', 'OFFEN')
        ORDER BY lieferbeginn DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    # 5. Letzte 5 CRM-Aktivitäten (domain_crm.activities)
    recent_activities = _query_many(
        db,
        """
        SELECT id, activity_type, subject,
               created_at::text, assigned_to
        FROM domain_crm.activities
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY created_at DESC
        LIMIT 5
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    # 6. Letzter Wareneingang (domain_agrar.harvest_acceptances)
    last_receipt_row = _query_one(
        db,
        """
        SELECT id, acceptance_number,
               accepted_at::text, net_weight_kg::float, product_id
        FROM domain_agrar.harvest_acceptances
        WHERE (supplier_id = :cid OR customer_id = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY accepted_at DESC
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    last_goods_receipt = None
    if last_receipt_row:
        last_goods_receipt = {
            "id": str(last_receipt_row["id"]),
            "reference_number": last_receipt_row.get("acceptance_number"),
            "received_at": last_receipt_row.get("accepted_at"),
            "quantity_kg": last_receipt_row.get("net_weight_kg"),
            "product_id": str(last_receipt_row["product_id"]) if last_receipt_row.get("product_id") else None,
            "source": "harvest_acceptances",
        }
    else:
        # Fallback: letzter Warenzugang aus Lagerbewegungen
        sm_row = _query_one(
            db,
            """
            SELECT id, reference_number, movement_date::text,
                   quantity::float, article_id
            FROM domain_inventory.inventory_stock_movements
            WHERE (:tid IS NULL OR tenant_id::text = :tid)
              AND movement_type = 'in'
              AND notes ILIKE :pattern
            ORDER BY movement_date DESC
            LIMIT 1
            """,
            {"cid": customer_id, "tid": tenant_id, "pattern": f"%{customer_id[:8]}%"},
        )
        if sm_row:
            last_goods_receipt = {
                "id": str(sm_row["id"]),
                "reference_number": sm_row.get("reference_number"),
                "received_at": sm_row.get("movement_date"),
                "quantity_kg": sm_row.get("quantity"),
                "article_id": str(sm_row["article_id"]) if sm_row.get("article_id") else None,
                "source": "inventory_stock_movements",
            }

    # 7. Kreditlimit (domain_crm.credit_limits wenn vorhanden)
    credit_limit_status = _query_one(
        db,
        """
        SELECT credit_limit::float, credit_used::float,
               (credit_limit - credit_used)::float AS credit_available,
               credit_status
        FROM domain_crm.credit_limits
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    return {
        "customer_id": customer_id,
        "tenant_id": tenant_id,
        "jahresumsatz_eur": jahresumsatz,
        "offene_op_summe_eur": op_summe,
        "recent_orders": orders,
        "open_invoices": [],  # covered by open_payments (OP-basiert)
        "open_payments": open_payments,
        "active_contracts": active_contracts,
        "recent_activities": recent_activities,
        "open_complaints": [],
        "last_goods_receipt": last_goods_receipt,
        "credit_limit_status": credit_limit_status,
    }
