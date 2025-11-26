"""API router for v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import consents

api_router = APIRouter()

api_router.include_router(consents.router, prefix="/consents", tags=["consents"])

