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
    accounts,
    journal_entries,
    articles,
    warehouses,
    policies
)

# Create main API router
api_router = APIRouter()

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
    prefix="/customers",
    tags=["crm", "customers"]
)

api_router.include_router(
    leads,
    prefix="/leads",
    tags=["crm", "leads"]
)

api_router.include_router(
    contacts,
    prefix="/contacts",
    tags=["crm", "contacts"]
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