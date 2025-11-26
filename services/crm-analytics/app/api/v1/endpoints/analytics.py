"""CRM Analytics API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.analytics import Dashboard, DashboardCreate, DashboardData, Report, ReportCreate, ReportData, Metric
from ....schemas.base import PaginatedResponse
from ....db.models import Dashboard as DashboardModel, Report as ReportModel, Metric as MetricModel

router = APIRouter()


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    tenant_id: Optional[str] = Query(None),
    dashboard_type: str = Query("executive", description="Dashboard type"),
    db: AsyncSession = get_db
):
    """Get dashboard data with metrics and charts."""
    # For now, return mock data - in production this would aggregate from all CRM services
    effective_tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    # Mock dashboard data
    dashboard_data = {
        "dashboard": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "tenant_id": effective_tenant_id,
            "name": f"{dashboard_type.title()} Dashboard",
            "description": f"Main {dashboard_type} dashboard",
            "type": dashboard_type,
            "config": {"widgets": ["kpi_cards", "sales_chart", "case_trends"]},
            "filters": {"date_range": "last_30_days"},
            "is_active": True,
            "is_default": True,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        "metrics": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_id": effective_tenant_id,
                "name": "Total Customers",
                "description": "Total active customers",
                "type": "count",
                "entity": "customers",
                "field": "id",
                "aggregation": "count",
                "filters": {"is_active": True},
                "value": 1250,
                "trend": 5.2,
                "last_calculated": "2025-11-15T10:00:00Z",
                "calculation_interval": 300,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "tenant_id": effective_tenant_id,
                "name": "Open Cases",
                "description": "Currently open support cases",
                "type": "count",
                "entity": "cases",
                "field": "id",
                "aggregation": "count",
                "filters": {"status": ["new", "assigned", "in_progress"]},
                "value": 45,
                "trend": -2.1,
                "last_calculated": "2025-11-15T10:00:00Z",
                "calculation_interval": 300,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        ],
        "charts": {
            "sales_trend": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "datasets": [{
                    "label": "Revenue",
                    "data": [12000, 19000, 15000, 25000, 22000, 30000]
                }]
            },
            "case_resolution": {
                "labels": ["Resolved", "Pending", "Escalated"],
                "datasets": [{
                    "data": [85, 12, 3],
                    "backgroundColor": ["#10B981", "#F59E0B", "#EF4444"]
                }]
            }
        },
        "last_updated": "2025-11-15T10:00:00Z"
    }

    return DashboardData(**dashboard_data)


@router.get("/reports/{report_type}", response_model=ReportData)
async def get_report_data(
    report_type: str,
    tenant_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = get_db
):
    """Get predefined report data."""
    effective_tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    # Mock report data based on type
    report_configs = {
        "sales_performance": {
            "name": "Sales Performance Report",
            "data": {
                "total_revenue": 250000,
                "total_opportunities": 150,
                "conversion_rate": 0.35,
                "average_deal_size": 8333,
                "top_performers": ["Alice Johnson", "Bob Smith", "Carol Davis"]
            }
        },
        "customer_satisfaction": {
            "name": "Customer Satisfaction Report",
            "data": {
                "average_rating": 4.2,
                "total_responses": 1250,
                "satisfaction_trend": [4.1, 4.3, 4.2, 4.4, 4.2],
                "top_issues": ["Response Time", "Product Quality", "Support"]
            }
        },
        "case_management": {
            "name": "Case Management Report",
            "data": {
                "total_cases": 1250,
                "average_resolution_time": 2.5,
                "sla_compliance": 0.92,
                "case_categories": {
                    "Technical": 450,
                    "Billing": 320,
                    "General": 480
                }
            }
        }
    }

    if report_type not in report_configs:
        raise HTTPException(status_code=404, detail=f"Report type '{report_type}' not found")

    config = report_configs[report_type]

    report_data = {
        "report": {
            "id": f"550e8400-e29b-41d4-a716-4466554400{hash(report_type) % 10}",
            "tenant_id": effective_tenant_id,
            "name": config["name"],
            "description": f"Generated {report_type} report",
            "type": report_type,
            "config": {"filters": {"date_range": f"{start_date or '2025-01-01'} to {end_date or '2025-11-15'}"}},
            "filters": {},
            "results": config["data"],
            "is_active": True,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-11-15T10:00:00Z"
        },
        "data": config["data"],
        "generated_at": "2025-11-15T10:00:00Z",
        "execution_time": 0.5
    }

    return ReportData(**report_data)


@router.post("/reports/custom", response_model=ReportData)
async def generate_custom_report(
    config: dict,
    tenant_id: str = Query(..., description="Tenant ID"),
    name: str = Query("Custom Report", description="Report name"),
    db: AsyncSession = get_db
):
    """Generate a custom report based on configuration."""
    # Mock custom report generation
    custom_data = {
        "report": {
            "id": "550e8400-e29b-41d4-a716-446655440099",
            "tenant_id": tenant_id,
            "name": name,
            "description": "Custom generated report",
            "type": "custom",
            "config": config,
            "filters": config.get("filters", {}),
            "results": {"custom_metric": 42, "data_points": 1000},
            "is_active": True,
            "created_at": "2025-11-15T10:00:00Z",
            "updated_at": "2025-11-15T10:00:00Z"
        },
        "data": {"custom_metric": 42, "data_points": 1000, "config_used": config},
        "generated_at": "2025-11-15T10:00:00Z",
        "execution_time": 1.2
    }

    return ReportData(**custom_data)


@router.get("/metrics/{metric_name}", response_model=Metric)
async def get_metric_value(
    metric_name: str,
    tenant_id: Optional[str] = Query(None),
    db: AsyncSession = get_db
):
    """Get current value for a specific metric."""
    effective_tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    # Mock metric data
    mock_metrics = {
        "total_customers": {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "tenant_id": effective_tenant_id,
            "name": "Total Customers",
            "description": "Total active customers",
            "type": "count",
            "entity": "customers",
            "field": "id",
            "aggregation": "count",
            "filters": {"is_active": True},
            "value": 1250,
            "trend": 5.2,
            "last_calculated": "2025-11-15T10:00:00Z",
            "calculation_interval": 300,
            "is_active": True,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-11-15T10:00:00Z"
        },
        "open_cases": {
            "id": "550e8400-e29b-41d4-a716-446655440011",
            "tenant_id": effective_tenant_id,
            "name": "Open Cases",
            "description": "Currently open support cases",
            "type": "count",
            "entity": "cases",
            "field": "id",
            "aggregation": "count",
            "filters": {"status": ["new", "assigned", "in_progress"]},
            "value": 45,
            "trend": -2.1,
            "last_calculated": "2025-11-15T10:00:00Z",
            "calculation_interval": 300,
            "is_active": True,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-11-15T10:00:00Z"
        }
    }

    if metric_name not in mock_metrics:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")

    return Metric(**mock_metrics[metric_name])


@router.get("/predictive/{model_type}", response_model=dict)
async def get_predictive_insights(
    model_type: str,
    tenant_id: Optional[str] = Query(None),
    entity_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """Get predictive analytics results."""
    effective_tenant_id = tenant_id or "00000000-0000-0000-0000-000000000001"

    # Mock predictive data
    if model_type == "lead_scoring":
        predictions = [
            {
                "entity_id": "550e8400-e29b-41d4-a716-446655440001",
                "entity_type": "lead",
                "score": 0.85,
                "confidence": 0.92,
                "prediction": "High probability to convert",
                "features": {"company_size": "large", "industry": "tech", "engagement_score": 8.5}
            },
            {
                "entity_id": "550e8400-e29b-41d4-a716-446655440002",
                "entity_type": "lead",
                "score": 0.32,
                "confidence": 0.78,
                "prediction": "Low probability to convert",
                "features": {"company_size": "small", "industry": "retail", "engagement_score": 2.1}
            }
        ]
    elif model_type == "churn_prediction":
        predictions = [
            {
                "entity_id": "550e8400-e29b-41d4-a716-446655440003",
                "entity_type": "customer",
                "score": 0.15,
                "confidence": 0.88,
                "prediction": "Low churn risk",
                "features": {"tenure_months": 24, "satisfaction_score": 4.5, "usage_frequency": "high"}
            }
        ]
    else:
        raise HTTPException(status_code=404, detail=f"Predictive model '{model_type}' not found")

    return {
        "model_type": model_type,
        "tenant_id": effective_tenant_id,
        "predictions": predictions[:limit],
        "generated_at": "2025-11-15T10:00:00Z"
    }