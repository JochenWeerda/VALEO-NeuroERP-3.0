"""CRM 360°-Kundensicht — aggregiert Daten aus mehreren Domänen.

Jeder Query-Block ist in try/except eingebettet: fehlende Tabellen liefern null,
kein 500-Fehler.  Alle SQL-Abfragen verwenden sqlalchemy.text() (thin-router-Muster).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.crm_360_schemas import Crm360Out


router = APIRouter()


def _safe_query(db: Session, sql: str, params: dict, many: bool = True) -> Any:
    """Execute a text query and return rows or None on error."""
    try:
        result = db.execute(text(sql), params)
        return result.fetchall() if many else result.fetchone()
    except Exception:
        db.rollback()
        return None


@router.get("/{customer_id}/360", response_model=Crm360Out, tags=["crm", "customers"], summary="Customer 360 abrufen")
async def get_customer_360(
    customer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """360°-Kundensicht: aggregiert Aufträge, Rechnungen, Zahlungen, Kontrakte,
    Aktivitäten, Reklamationen, Wareneingänge und Kreditlimit-Status."""

    # -------------------------------------------------------------------------
    # 1. Letzte 10 Aufträge
    # -------------------------------------------------------------------------
    orders_rows = _safe_query(
        db,
        """
        SELECT id, order_number, status, total_amount, created_at
        FROM sales_orders
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
        ORDER BY created_at DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    orders = None
    if orders_rows is not None:
        orders = [
            {
                "id": str(r[0]),
                "order_number": r[1],
                "status": r[2],
                "total_amount": float(r[3]) if r[3] is not None else None,
                "created_at": str(r[4]) if r[4] else None,
            }
            for r in orders_rows
        ]

    # -------------------------------------------------------------------------
    # 2. Offene Rechnungen
    # -------------------------------------------------------------------------
    invoices_rows = _safe_query(
        db,
        """
        SELECT id, invoice_number, status, total_amount, due_date
        FROM finance_invoices
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
          AND status NOT IN ('PAID', 'CANCELLED')
        ORDER BY due_date ASC
        LIMIT 20
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    open_invoices = None
    if invoices_rows is not None:
        open_invoices = [
            {
                "id": str(r[0]),
                "invoice_number": r[1],
                "status": r[2],
                "total_amount": float(r[3]) if r[3] is not None else None,
                "due_date": str(r[4]) if r[4] else None,
            }
            for r in invoices_rows
        ]

    # -------------------------------------------------------------------------
    # 3. Offene Zahlungen (Betrag + Alter in Tagen)
    # -------------------------------------------------------------------------
    payments_rows = _safe_query(
        db,
        """
        SELECT id, amount, due_date,
               (CURRENT_DATE - due_date::date) AS days_overdue
        FROM open_items
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
          AND status = 'OPEN'
        ORDER BY due_date ASC
        LIMIT 20
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    open_payments = None
    if payments_rows is not None:
        open_payments = [
            {
                "id": str(r[0]),
                "amount": float(r[1]) if r[1] is not None else None,
                "due_date": str(r[2]) if r[2] else None,
                "days_overdue": int(r[3]) if r[3] is not None else 0,
            }
            for r in payments_rows
        ]

    # -------------------------------------------------------------------------
    # 4. Aktive Kontrakte
    # -------------------------------------------------------------------------
    contracts_rows = _safe_query(
        db,
        """
        SELECT id, contract_number, status, start_date, end_date, total_value
        FROM kontrakte
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
          AND status = 'AKTIV'
        ORDER BY start_date DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    active_contracts = None
    if contracts_rows is not None:
        active_contracts = [
            {
                "id": str(r[0]),
                "contract_number": r[1],
                "status": r[2],
                "start_date": str(r[3]) if r[3] else None,
                "end_date": str(r[4]) if r[4] else None,
                "total_value": float(r[5]) if r[5] is not None else None,
            }
            for r in contracts_rows
        ]

    # -------------------------------------------------------------------------
    # 5. Letzte 5 Aktivitäten
    # -------------------------------------------------------------------------
    activities_rows = _safe_query(
        db,
        """
        SELECT id, activity_type, subject, created_at, assigned_to
        FROM activities
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
        ORDER BY created_at DESC
        LIMIT 5
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    recent_activities = None
    if activities_rows is not None:
        recent_activities = [
            {
                "id": str(r[0]),
                "activity_type": r[1],
                "subject": r[2],
                "created_at": str(r[3]) if r[3] else None,
                "assigned_to": r[4],
            }
            for r in activities_rows
        ]

    # -------------------------------------------------------------------------
    # 6. Offene Reklamationen
    # -------------------------------------------------------------------------
    complaints_rows = _safe_query(
        db,
        """
        SELECT id, complaint_number, status, subject, created_at
        FROM reklamationen
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
          AND status NOT IN ('GESCHLOSSEN', 'ABGELEHNT')
        ORDER BY created_at DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    open_complaints = None
    if complaints_rows is not None:
        open_complaints = [
            {
                "id": str(r[0]),
                "complaint_number": r[1],
                "status": r[2],
                "subject": r[3],
                "created_at": str(r[4]) if r[4] else None,
            }
            for r in complaints_rows
        ]

    # -------------------------------------------------------------------------
    # 7. Letzter Wareneingang (harvest_acceptances → inventory_stock_movements)
    # -------------------------------------------------------------------------
    last_receipt = _safe_query(
        db,
        """
        SELECT id, acceptance_number, accepted_at, net_weight, product_id
        FROM harvest_acceptances
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
        ORDER BY accepted_at DESC
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
        many=False,
    )
    last_goods_receipt = None
    if last_receipt is not None:
        last_goods_receipt = {
            "id": str(last_receipt[0]),
            "reference_number": last_receipt[1],
            "received_at": str(last_receipt[2]) if last_receipt[2] else None,
            "quantity": float(last_receipt[3]) if last_receipt[3] is not None else None,
            "product_id": str(last_receipt[4]) if last_receipt[4] else None,
            "source": "harvest_acceptances",
        }
    else:
        # Fallback: inventory_stock_movements
        sm_row = _safe_query(
            db,
            """
            SELECT id, movement_type, quantity, moved_at, article_id
            FROM inventory_stock_movements
            WHERE customer_id = :cid
              AND (:tid IS NULL OR tenant_id = :tid)
            ORDER BY moved_at DESC
            LIMIT 1
            """,
            {"cid": customer_id, "tid": tenant_id},
            many=False,
        )
        if sm_row is not None:
            last_goods_receipt = {
                "id": str(sm_row[0]),
                "reference_number": None,
                "received_at": str(sm_row[3]) if sm_row[3] else None,
                "quantity": float(sm_row[2]) if sm_row[2] is not None else None,
                "article_id": str(sm_row[4]) if sm_row[4] else None,
                "source": "inventory_stock_movements",
            }

    # -------------------------------------------------------------------------
    # 8. Kreditlimit-Status
    # -------------------------------------------------------------------------
    credit_row = _safe_query(
        db,
        """
        SELECT credit_limit, credit_used, credit_available, credit_status
        FROM customer_credit_limits
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
        many=False,
    )
    credit_limit_status = None
    if credit_row is not None:
        credit_limit_status = {
            "credit_limit": float(credit_row[0]) if credit_row[0] is not None else None,
            "credit_used": float(credit_row[1]) if credit_row[1] is not None else None,
            "credit_available": float(credit_row[2]) if credit_row[2] is not None else None,
            "credit_status": credit_row[3],
        }

    # -------------------------------------------------------------------------
    # Verify customer exists (basic check)
    # -------------------------------------------------------------------------
    customer_exists = _safe_query(
        db,
        "SELECT id FROM customers WHERE id = :cid LIMIT 1",
        {"cid": customer_id},
        many=False,
    )
    # Accept also from business_partners if customers table is missing
    if customer_exists is None:
        customer_exists = _safe_query(
            db,
            "SELECT id FROM business_partners WHERE id = :cid LIMIT 1",
            {"cid": customer_id},
            many=False,
        )

    return {
        "customer_id": customer_id,
        "tenant_id": tenant_id,
        "recent_orders": orders,
        "open_invoices": open_invoices,
        "open_payments": open_payments,
        "active_contracts": active_contracts,
        "recent_activities": recent_activities,
        "open_complaints": open_complaints,
        "last_goods_receipt": last_goods_receipt,
        "credit_limit_status": credit_limit_status,
    }
