"""
Reports Router
API endpoints for reports and analytics dashboard
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from .services import ReportsService
from .models import ReportResponse, ReportMetadata
from ..documents.router import _DB  # Import the shared DB store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Initialize service with shared DB
reports_service = ReportsService(_DB)


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Get dashboard summary with key performance indicators
    """
    try:
        summary = reports_service.get_dashboard_summary(start_date, end_date)
        return {
            "ok": True,
            "data": summary.model_dump()
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-performance")
async def get_sales_performance_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Sales Performance Report
    - Total revenue, orders, average order value
    - Conversion rates through the sales funnel
    """
    try:
        report = reports_service.get_sales_performance_report(start_date, end_date)
        return ReportResponse(
            metadata=ReportMetadata(
                reportType="sales_performance",
                filters={"start_date": start_date, "end_date": end_date},
                dataPoints=1
            ),
            data=report.model_dump()
        ).model_dump()
    except Exception as e:
        logger.error(f"Failed to get sales performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer-analytics")
async def get_customer_analytics_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Customer Analytics Report
    - Top customers by revenue
    - Customer acquisition trends
    - Customer retention metrics
    """
    try:
        report = reports_service.get_customer_analytics_report(start_date, end_date)
        return ReportResponse(
            metadata=ReportMetadata(
                reportType="customer_analytics",
                filters={"start_date": start_date, "end_date": end_date},
                dataPoints=len(report.topCustomers)
            ),
            data=report.model_dump()
        ).model_dump()
    except Exception as e:
        logger.error(f"Failed to get customer analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product-analytics")
async def get_product_analytics_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Product Analytics Report
    - Top products by sales volume and revenue
    - Product performance trends
    """
    try:
        report = reports_service.get_product_analytics_report(start_date, end_date)
        return ReportResponse(
            metadata=ReportMetadata(
                reportType="product_analytics",
                filters={"start_date": start_date, "end_date": end_date},
                dataPoints=report.totalUniqueProducts
            ),
            data=report.model_dump()
        ).model_dump()
    except Exception as e:
        logger.error(f"Failed to get product analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financial-analytics")
async def get_financial_analytics_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Financial Analytics Report
    - Revenue breakdown (total, paid, outstanding)
    - Outstanding payments by aging buckets
    - Payment method distribution
    """
    try:
        report = reports_service.get_financial_analytics_report(start_date, end_date)
        return ReportResponse(
            metadata=ReportMetadata(
                reportType="financial_analytics",
                filters={"start_date": start_date, "end_date": end_date},
                dataPoints=len(report.paymentMethods)
            ),
            data=report.model_dump()
        ).model_dump()
    except Exception as e:
        logger.error(f"Failed to get financial analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend-analytics")
async def get_trend_analytics_report(
    period: str = Query("monthly", description="Aggregation period: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Trend Analytics Report
    - Revenue trends over time
    - Order volume trends
    - Customer acquisition trends
    """
    try:
        report = reports_service.get_trend_analytics_report(period, start_date, end_date)
        return ReportResponse(
            metadata=ReportMetadata(
                reportType="trend_analytics",
                filters={"period": period, "start_date": start_date, "end_date": end_date},
                dataPoints=len(report.revenueTrends)
            ),
            data=report.model_dump()
        ).model_dump()
    except Exception as e:
        logger.error(f"Failed to get trend analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{report_type}")
async def export_report(
    report_type: str,
    format: str = Query("json", description="Export format: json, csv"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Export report data in various formats
    """
    try:
        # Get the report data
        if report_type == "sales-performance":
            report = reports_service.get_sales_performance_report(start_date, end_date)
        elif report_type == "customer-analytics":
            report = reports_service.get_customer_analytics_report(start_date, end_date)
        elif report_type == "product-analytics":
            report = reports_service.get_product_analytics_report(start_date, end_date)
        elif report_type == "financial-analytics":
            report = reports_service.get_financial_analytics_report(start_date, end_date)
        elif report_type == "trend-analytics":
            report = reports_service.get_trend_analytics_report("monthly", start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {report_type}")

        if format == "csv":
            # Simple CSV conversion (in production, use proper CSV library)
            data = report.model_dump()
            csv_content = f"Report Type: {report_type}\n"
            csv_content += f"Generated: {ReportMetadata().generatedAt}\n\n"

            if hasattr(report, 'topCustomers'):
                csv_content += "Customer ID,Total Revenue,Order Count\n"
                for customer in data['topCustomers']:
                    csv_content += f"{customer['customerId']},{customer['totalRevenue']},{customer['orderCount']}\n"
            elif hasattr(report, 'topProductsByRevenue'):
                csv_content += "Article,Quantity,Revenue,Order Count\n"
                for product in data['topProductsByRevenue']:
                    csv_content += f"{product['article']},{product['quantity']},{product['revenue']},{product['orderCount']}\n"

            return {
                "ok": True,
                "format": "csv",
                "content": csv_content,
                "filename": f"{report_type}_report.csv"
            }

        # Default JSON response
        return ReportResponse(
            metadata=ReportMetadata(
                reportType=report_type,
                filters={"format": format, "start_date": start_date, "end_date": end_date}
            ),
            data=report.model_dump()
        ).model_dump()

    except Exception as e:
        logger.error(f"Failed to export report {report_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))