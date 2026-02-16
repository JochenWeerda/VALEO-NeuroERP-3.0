"""
Analytics API v1
KPIs and dashboard metrics endpoint
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.reports.services import ReportsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics", "dashboard"])


def get_reports_service(db: Session = Depends(get_db)) -> ReportsService:
    """Dependency to get ReportsService with database session"""
    return ReportsService(db_session=db)


@router.get("/kpis")
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
            from app.domains.agrar.models import Contract, WeighingTicket
            from app.domains.inventory.models import InventoryLot
            
            db = next(get_reports_service()._get_session())
            
            # Get contract metrics
            contract_query = db.query(Contract)
            if start_date:
                contract_query = contract_query.filter(Contract.created_at >= start_date)
            if end_date:
                contract_query = contract_query.filter(Contract.created_at <= end_date)
            
            contracts = contract_query.all()
            
            for contract in contracts:
                # Assuming contract has quantity and unit fields
                if hasattr(contract, 'quantity') and contract.quantity:
                    quantity = float(contract.quantity)
                    if contract.unit == 'long ton' or contract.unit == 'lt':
                        kpis["contract_long_tons"] += quantity
                    elif contract.unit == 'short ton' or contract.unit == 'st':
                        kpis["contract_short_tons"] += quantity
            
            # Get weighing ticket metrics for today
            today = datetime.now().date()
            weighing_query = db.query(WeighingTicket).filter(
                WeighingTicket.created_at >= today.strftime("%Y-%m-%d")
            )
            
            weighings = weighing_query.all()
            
            for weighing in weighings:
                if hasattr(weighing, 'net_weight') and weighing.net_weight:
                    kpis["weighing_today_tons"] += float(weighing.net_weight)
            
            # Get blocked inventory lots
            blocked_lots = db.query(InventoryLot).filter(InventoryLot.status == 'BLOCKED').count()
            kpis["inventory_lots_blocked"] = blocked_lots
            
        except Exception as e:
            logger.warning(f"Failed to calculate agrar metrics: {e}")
            # Keep default values if we can't get real data
        
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


@router.get("/trends")
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
