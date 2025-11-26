"""API router for v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import gdpr

api_router = APIRouter()

api_router.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])

