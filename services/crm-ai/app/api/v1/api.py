"""CRM AI API v1 router."""

from fastapi import APIRouter

from .endpoints.ai import router as ai_router

api_router = APIRouter()
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])

***REMOVED*** TODO: Add model management, training, and monitoring routers when implemented
***REMOVED*** api_router.include_router(models_router, prefix="/models", tags=["models"])
***REMOVED*** api_router.include_router(training_router, prefix="/training", tags=["training"])
***REMOVED*** api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])