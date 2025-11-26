"""CRM Communication API v1 router."""

from fastapi import APIRouter

from .endpoints.communication import router as communication_router

api_router = APIRouter()
api_router.include_router(communication_router, prefix="/communication", tags=["communication"])

# TODO: Add email campaigns, templates, and analytics routers when implemented
# api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
# api_router.include_router(templates_router, prefix="/templates", tags=["templates"])
# api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])