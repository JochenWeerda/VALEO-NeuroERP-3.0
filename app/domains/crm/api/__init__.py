"""CRM API routers."""

from fastapi import APIRouter
from .customers import router as customers_router
from .leads import router as leads_router

# Main CRM router
router = APIRouter()
router.include_router(customers_router, prefix="/customers", tags=["customers"])
router.include_router(leads_router, prefix="/leads", tags=["leads"])

__all__ = ['router']
