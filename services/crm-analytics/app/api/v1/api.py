"""CRM Analytics API v1 router."""

from fastapi import APIRouter

from .endpoints.analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# TODO: Add dashboards, reports, and metrics management routers when implemented
# api_router.include_router(dashboards_router, prefix="/dashboards", tags=["dashboards"])
# api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
# api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])