"""API Router v1 für Zoll-Service."""

from fastapi import APIRouter

from .endpoints import permits, preference, screening

api_router = APIRouter()
api_router.include_router(screening.router, prefix="/screening", tags=["screening"])
api_router.include_router(permits.router, prefix="/permits", tags=["permits"])
api_router.include_router(preference.router, prefix="/preference", tags=["preference"])
