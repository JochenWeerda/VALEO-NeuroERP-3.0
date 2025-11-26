"""CRM Sales API v1 router."""

from fastapi import APIRouter

from .endpoints.opportunities import router as opportunities_router

api_router = APIRouter()
api_router.include_router(opportunities_router, prefix="/opportunities", tags=["opportunities"])

***REMOVED*** TODO: Add quotes and sales activities routers when implemented
***REMOVED*** api_router.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
***REMOVED*** api_router.include_router(sales_activities_router, prefix="/sales-activities", tags=["sales-activities"])