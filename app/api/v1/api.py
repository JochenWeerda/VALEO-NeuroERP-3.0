"""
VALEO-NeuroERP API v1 Router
Main API router that includes all domain routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    tenants,
    users,
    customers,
    leads,
    contacts,
    activities,
    farm_profiles,
    accounts,
    journal_entries,
    articles,
    warehouses,
    policies
)

# Import domain routers
from app.domains.agrar.api import psm, psm_proplanta
from app.documents.router import router as documents_router
from app.reports.router import router as reports_router

# Create main API router
api_router = APIRouter()


@api_router.get("/status", tags=["meta"])
async def api_status():
    """Lightweight status endpoint for authenticated clients."""
    return {"status": "ok"}

# Include domain routers
api_router.include_router(
    health,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    tenants,
    tags=["tenants"]
)

api_router.include_router(
    users,
    tags=["users"]
)

api_router.include_router(
    customers,
    prefix="/crm/customers",
    tags=["crm", "customers"]
)

api_router.include_router(
    leads,
    prefix="/crm/leads",
    tags=["crm", "leads"]
)

api_router.include_router(
    contacts,
    prefix="/crm/contacts",
    tags=["crm", "contacts"]
)

api_router.include_router(
    activities.router,
    prefix="/crm/activities",
    tags=["crm", "activities"]
)

api_router.include_router(
    farm_profiles.router,
    prefix="/crm/farm-profiles",
    tags=["crm", "farm-profiles"]
)

api_router.include_router(
    accounts,
    prefix="/accounts",
    tags=["finance", "accounts"]
)

api_router.include_router(
    journal_entries,
    prefix="/journal-entries",
    tags=["finance", "journal-entries"]
)

api_router.include_router(
    articles,
    prefix="/articles",
    tags=["inventory", "articles"]
)

api_router.include_router(
    warehouses,
    prefix="/warehouses",
    tags=["inventory", "warehouses"]
)

api_router.include_router(
    policies.router,
    prefix="/mcp",
    tags=["mcp", "policies"]
)

# Documents and Reports routers
api_router.include_router(
    documents_router,
    tags=["documents", "sales"]
)

api_router.include_router(
    reports_router,
    tags=["reports", "analytics", "dashboard"]
)

# Agrar domain routers
api_router.include_router(
    psm.router,
    prefix="/agrar/psm",
    tags=["agrar", "psm"]
)

api_router.include_router(
    psm_proplanta.router,
    prefix="/agrar/psm/proplanta",
    tags=["agrar", "psm", "proplanta", "integration"]
)
