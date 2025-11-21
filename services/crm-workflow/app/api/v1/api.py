"""CRM Workflow API v1 router."""

from fastapi import APIRouter

from .endpoints.workflows import router as workflows_router

api_router = APIRouter()
api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])

# TODO: Add triggers, notifications, and events routers when implemented
# api_router.include_router(triggers_router, prefix="/triggers", tags=["triggers"])
# api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
# api_router.include_router(events_router, prefix="/events", tags=["events"])