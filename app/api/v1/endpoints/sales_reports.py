"""
Sales Reports and Dashboards endpoints.
SALES-REP-01: Sales Reports und Dashboards
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/sales/reports", tags=["sales", "reports"])


class SalesSummary(BaseModel):
    period: str
    total_orders: int
    total_revenue: Decimal
    total_deliveries: int
    total_invoiced: Decimal
    total_credit_notes: Decimal
    net_revenue: Decimal
    average_order_value: Decimal


class TopCustomer(BaseModel):
    customer_id: str
    customer_name: Optional[str]
    order_count: int
    total_revenue: Decimal


class TopArticle(BaseModel):
    article_number: str
    article_name: Optional[str]
    total_quantity: Decimal
    total_revenue: Decimal


class SalesPipelineKPI(BaseModel):
    open_orders: int
    open_order_value: Decimal
    open_offers: int
    open_offer_value: Decimal
    conversion_rate: Optional[float] = None


@router.get("/summary", response_model=SalesSummary, summary="Sales summary abrufen")
async def get_sales_summary(
    period_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    period_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Sales summary for a period."""
    try:
        orders = db.execute(
            text("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM domain_crm.sales_orders
                WHERE tenant_id = :tid AND created_at >= :from AND created_at <= :to
            """),
            {"tid": tenant_id, "from": period_from, "to": period_to},
        ).fetchone()

        deliveries = db.execute(
            text("""
                SELECT COUNT(*)
                FROM domain_sales.delivery_notes
                WHERE tenant_id = :tid AND lieferdatum >= :from AND lieferdatum <= :to
            """),
            {"tid": tenant_id, "from": period_from, "to": period_to},
        ).fetchone()

        total_orders = orders[0] if orders else 0
        total_revenue = Decimal(str(orders[1])) if orders else Decimal("0")
        total_deliveries = deliveries[0] if deliveries else 0
        avg = total_revenue / total_orders if total_orders > 0 else Decimal("0")

        return SalesSummary(
            period=f"{period_from} bis {period_to}",
            total_orders=total_orders,
            total_revenue=total_revenue,
            total_deliveries=total_deliveries,
            total_invoiced=total_revenue,
            total_credit_notes=Decimal("0"),
            net_revenue=total_revenue,
            average_order_value=avg.quantize(Decimal("0.01")),
        )
    except Exception as e:
        logger.warning("Sales summary query failed (tables may not exist): %s", e)
        return SalesSummary(
            period=f"{period_from} bis {period_to}",
            total_orders=0, total_revenue=Decimal("0"),
            total_deliveries=0, total_invoiced=Decimal("0"),
            total_credit_notes=Decimal("0"), net_revenue=Decimal("0"),
            average_order_value=Decimal("0"),
        )


@router.get("/top-customers", response_model=List[TopCustomer], summary="Top customers abrufen")
async def get_top_customers(
    period_from: date = Query(...),
    period_to: date = Query(...),
    limit: int = Query(10, ge=1, le=50),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Top customers by revenue in a period."""
    try:
        rows = db.execute(
            text("""
                SELECT so.customer_id, MAX(so.subject) AS customer_name,
                       COUNT(*) AS order_count, COALESCE(SUM(so.total_amount), 0) AS total
                FROM domain_crm.sales_orders so
                WHERE so.tenant_id = :tid AND so.created_at >= :from AND so.created_at <= :to
                GROUP BY so.customer_id
                ORDER BY total DESC
                LIMIT :lim
            """),
            {"tid": tenant_id, "from": period_from, "to": period_to, "lim": limit},
        ).fetchall()
        return [
            TopCustomer(
                customer_id=r[0], customer_name=r[1],
                order_count=r[2], total_revenue=Decimal(str(r[3])),
            )
            for r in rows
        ]
    except Exception:
        return []


@router.get("/top-articles", response_model=List[TopArticle], summary="Top articles abrufen")
async def get_top_articles(
    period_from: date = Query(...),
    period_to: date = Query(...),
    limit: int = Query(10, ge=1, le=50),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Top articles by revenue in a period."""
    try:
        rows = db.execute(
            text("""
                SELECT soi.article_number, MAX(soi.description) AS article_name,
                       SUM(soi.quantity) AS total_qty,
                       SUM(soi.quantity * soi.unit_price * (1 - soi.discount_percent / 100)) AS total_rev
                FROM domain_crm.sales_order_items soi
                JOIN domain_crm.sales_orders so ON so.id = soi.order_id
                WHERE so.tenant_id = :tid AND so.created_at >= :from AND so.created_at <= :to
                GROUP BY soi.article_number
                ORDER BY total_rev DESC
                LIMIT :lim
            """),
            {"tid": tenant_id, "from": period_from, "to": period_to, "lim": limit},
        ).fetchall()
        return [
            TopArticle(
                article_number=r[0], article_name=r[1],
                total_quantity=Decimal(str(r[2])),
                total_revenue=Decimal(str(r[3])),
            )
            for r in rows
        ]
    except Exception:
        return []


class MonthlyRevenue(BaseModel):
    month: str
    revenue: Decimal
    order_count: int


@router.get("/monthly-revenue", response_model=List[MonthlyRevenue], summary="Monthly revenue abrufen")
async def get_monthly_revenue(
    period_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    period_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Monatliche Umsaetze fuer Dashboard-Charts."""
    try:
        rows = db.execute(
            text("""
                SELECT TO_CHAR(created_at, 'YYYY-MM') AS month,
                       COUNT(*) AS order_count,
                       COALESCE(SUM(total_amount), 0) AS revenue
                FROM domain_crm.sales_orders
                WHERE tenant_id = :tid
                  AND created_at >= :from AND created_at <= :to
                GROUP BY TO_CHAR(created_at, 'YYYY-MM')
                ORDER BY month
            """),
            {"tid": tenant_id, "from": period_from, "to": period_to},
        ).fetchall()
        return [
            MonthlyRevenue(
                month=r.month,
                revenue=Decimal(str(r.revenue)),
                order_count=r.order_count,
            )
            for r in rows
        ]
    except Exception as e:
        logger.warning("Monthly revenue query failed: %s", e)
        return []


@router.get("/pipeline", response_model=SalesPipelineKPI, summary="Sales pipeline kpi abrufen")
async def get_sales_pipeline_kpi(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Sales pipeline KPIs: open orders, offers, conversion rate."""
    try:
        orders = db.execute(
            text("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM domain_crm.sales_orders
                WHERE tenant_id = :tid AND status = 'open'
            """),
            {"tid": tenant_id},
        ).fetchone()

        offers = db.execute(
            text("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM domain_crm.sales_offers
                WHERE tenant_id = :tid AND status = 'offen'
            """),
            {"tid": tenant_id},
        ).fetchone()

        total_offers = db.execute(
            text("SELECT COUNT(*) FROM domain_crm.sales_offers WHERE tenant_id = :tid"),
            {"tid": tenant_id},
        ).scalar() or 0

        won_offers = db.execute(
            text("SELECT COUNT(*) FROM domain_crm.sales_offers WHERE tenant_id = :tid AND status = 'converted'"),
            {"tid": tenant_id},
        ).scalar() or 0

        conversion = (won_offers / total_offers * 100) if total_offers > 0 else None

        return SalesPipelineKPI(
            open_orders=orders[0] if orders else 0,
            open_order_value=Decimal(str(orders[1])) if orders else Decimal("0"),
            open_offers=offers[0] if offers else 0,
            open_offer_value=Decimal(str(offers[1])) if offers else Decimal("0"),
            conversion_rate=round(conversion, 1) if conversion is not None else None,
        )
    except Exception as e:
        logger.warning("Pipeline KPI query failed: %s", e)
        return SalesPipelineKPI(
            open_orders=0, open_order_value=Decimal("0"),
            open_offers=0, open_offer_value=Decimal("0"),
        )
