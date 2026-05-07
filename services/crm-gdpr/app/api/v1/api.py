"""API router for v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import gdpr, privacy_erasure

api_router = APIRouter()

api_router.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])
api_router.include_router(privacy_erasure.router, prefix="/privacy")

