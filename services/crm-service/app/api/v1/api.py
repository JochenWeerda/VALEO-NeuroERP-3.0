"""CRM Service API v1 router."""

from fastapi import APIRouter

from .endpoints.cases import router as cases_router

api_router = APIRouter()
api_router.include_router(cases_router, prefix="/cases", tags=["cases"])

# TODO: Add knowledge-base and categories routers when implemented
# api_router.include_router(knowledge_base_router, prefix="/knowledge-base", tags=["knowledge-base"])
# api_router.include_router(categories_router, prefix="/categories", tags=["categories"])