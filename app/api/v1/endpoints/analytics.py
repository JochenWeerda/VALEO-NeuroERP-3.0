"""
Analytics API v1
KPIs and dashboard metrics endpoint
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
import logging
from datetime import datetime

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.reports.services import ReportsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics", "dashboard"])


def get_reports_service(db: Session = Depends(get_db)) -> ReportsService:
    """Dependency to get ReportsService with database session"""
    return ReportsService(db_session=db)


@router.get("/kpis", summary="Kpis abrufen")
async def get_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    service: ReportsService = Depends(get_reports_service)
) -> dict:
    """
    Get key performance indicators (KPIs) for dashboard widgets
    Returns:
        dict: KPIs including revenue, orders, customers, stock, and agrar-specific metrics
    """
    try:
        # Get dashboard summary from reports service
        summary = service.get_dashboard_summary(start_date, end_date)
        
        # Calculate additional metrics based on available data
        kpis = {
            # Revenue (Total paid revenue)
            "revenue": summary.totalRevenue,
            
            # Orders (Total sales orders)
            "orders": summary.totalOrders,
            
            # Customers (Active customers)
            "customers": summary.activeCustomers,
            
            # Stock (Placeholder - would need actual inventory data)
            "inventory": 97,  # Percentage
            
            # Agrar-specific KPIs
            "contract_long_tons": 0,
            "contract_short_tons": 0,
            "weighing_today_tons": 0,
            "inventory_lots_blocked": 0
        }
        
        # Calculate agrar-specific metrics from real data if available
        try:
            db = service._get_session()
            from app.infrastructure.models import AgrarContract, WeighingTicket

            contract_query = db.query(AgrarContract)
            if start_date:
                contract_query = contract_query.filter(AgrarContract.created_at >= start_date)
            if end_date:
                contract_query = contract_query.filter(AgrarContract.created_at <= end_date)
            contracts = contract_query.all()

            for contract in contracts:
                qty = getattr(contract, "quantity", None) or getattr(contract, "allocated_quantity_kg", None)
                if qty:
                    quantity = float(qty) / 1000.0  # kg to tons if needed
                    kpis["contract_long_tons"] += quantity  # simplified: sum all

            today = datetime.now().date()
            weighings = db.query(WeighingTicket).filter(
                WeighingTicket.weighing_date >= datetime.combine(today, datetime.min.time())
            ).all()
            for weighing in weighings:
                if hasattr(weighing, "net_weight") and weighing.net_weight:
                    kpis["weighing_today_tons"] += float(weighing.net_weight)

            # Inventory lots blocked (SiloLot or similar - skip if model unavailable)
            try:
                from app.infrastructure.models import SiloLot
                blocked_lots = db.query(SiloLot).filter(SiloLot.status == "blocked").count()
                kpis["inventory_lots_blocked"] = blocked_lots
            except Exception:  # noqa: BLE001 — SiloLot-Modell nicht verfügbar; Wert wird übersprungen
                pass
        except Exception as e:
            logger.warning("Agrar KPIs skipped (models/tables may be missing): %s", e)
        
        return kpis
        
    except Exception as e:
        logger.error(f"Failed to get KPIs: {e}")
        # Return default values on error
        return {
            "revenue": 0,
            "orders": 0,
            "customers": 0,
            "inventory": 0,
            "contract_long_tons": 0,
            "contract_short_tons": 0,
            "weighing_today_tons": 0,
            "inventory_lots_blocked": 0
        }


@router.get("/trends", summary="Kpi trends abrufen")
async def get_kpi_trends(
    metric: str = Query(..., description="Metric to get trend for"),
    period: str = Query("monthly", description="Aggregation period: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    service: ReportsService = Depends(get_reports_service)
) -> dict:
    """
    Get trends for a specific KPI
    """
    try:
        trend_report = service.get_trend_analytics_report(period, start_date, end_date)
        
        trends = {}
        
        if metric == "revenue":
            trends = trend_report.revenueTrends
        elif metric == "orders":
            trends = trend_report.orderVolumeTrends
        elif metric == "customers":
            trends = trend_report.inquiryTrends
        
        return {"metric": metric, "period": period, "trends": trends}
        
    except Exception as e:
        logger.error(f"Failed to get KPI trends: {e}")
        return {"metric": metric, "period": period, "trends": {}}


# ─── Branchenbenchmark (Gap 047) ───────────────────────────────────────────
# Referenzwerte Landhandel (Platzhalter; echte Daten z.B. von Verbänden)
_BRANCH_REFERENCE = {
    "revenue_per_customer": 45000,  # €/Jahr typ. Landhandel
    "orders_per_month": 120,
    "conversion_rate": 72.0,  # %
    "avg_order_value": 3800,  # €
    "customers": 450,  # typ. aktive Kunden Genossenschaft Landhandel
}


@router.get("/benchmark", summary="Benchmark abrufen")
async def get_benchmark(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    service: ReportsService = Depends(get_reports_service),
) -> dict:
    """
    Branchenbenchmark je Genossenschaft (Gap 047).
    Liefert eigene KPIs, Branchen-Referenzwerte und Abweichung.
    """
    try:
        summary = service.get_dashboard_summary(start_date, end_date)
        own = {
            "revenue": summary.totalRevenue,
            "orders": summary.totalOrders,
            "customers": summary.activeCustomers,
            "conversion_rate": summary.conversionRate,
        }
        own["avg_order_value"] = (
            round(own["revenue"] / own["orders"], 2) if own["orders"] > 0 else 0
        )
        own["revenue_per_customer"] = (
            round(own["revenue"] / own["customers"], 2) if own["customers"] > 0 else 0
        )

        branch = dict(_BRANCH_REFERENCE)
        # Skalierung: Referenz orders_per_month → auf Periode anpassen
        months = 1.0
        if start_date and end_date:
            from datetime import datetime as dt
            try:
                d1 = dt.strptime(start_date, "%Y-%m-%d").date()
                d2 = dt.strptime(end_date, "%Y-%m-%d").date()
                months = max(0.1, (d2 - d1).days / 30.0)
                branch["orders_per_month"] = round(branch["orders_per_month"] * months)
            except ValueError:
                pass

        # Abgeleitete Referenzwerte für Vergleich
        branch["revenue"] = round(branch["revenue_per_customer"] * max(1, own["customers"]), 2)
        branch["orders"] = branch["orders_per_month"]

        comparison = {}
        for k, own_val in own.items():
            ref = branch.get(k)
            if ref is not None and ref != 0:
                pct = round((own_val - ref) / ref * 100, 1)
                comparison[k] = {"own": own_val, "branch": ref, "deviation_pct": pct}
            else:
                comparison[k] = {"own": own_val, "branch": ref, "deviation_pct": None}

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "own": own,
            "branch": branch,
            "comparison": comparison,
        }
    except Exception as e:
        logger.error("Benchmark failed: %s", e)
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "own": {},
            "branch": _BRANCH_REFERENCE,
            "comparison": {},
        }


