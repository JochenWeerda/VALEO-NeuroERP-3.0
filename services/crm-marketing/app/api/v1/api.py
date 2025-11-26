"""API router for v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import segments, campaigns

api_router = APIRouter()

api_router.include_router(segments.router, prefix="/segments", tags=["segments"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])

