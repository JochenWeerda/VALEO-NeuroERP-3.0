"""CRM Communication API v1 router."""

from fastapi import APIRouter

from .endpoints.communication import router as communication_router

api_router = APIRouter()
api_router.include_router(communication_router, prefix="/communication", tags=["communication"])

***REMOVED*** TODO: Add email campaigns, templates, and analytics routers when implemented
***REMOVED*** api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
***REMOVED*** api_router.include_router(templates_router, prefix="/templates", tags=["templates"])
***REMOVED*** api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])