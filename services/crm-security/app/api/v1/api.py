"""CRM Security & Compliance API v1 router."""

from fastapi import APIRouter

from .endpoints.security import router as security_router

api_router = APIRouter()
api_router.include_router(security_router, prefix="/security", tags=["security"])

# Additional routers can be added here for specific security domains
# api_router.include_router(encryption_router, prefix="/encryption", tags=["encryption"])
# api_router.include_router(compliance_router, prefix="/compliance", tags=["compliance"])
# api_router.include_router(threat_router, prefix="/threats", tags=["threats"])