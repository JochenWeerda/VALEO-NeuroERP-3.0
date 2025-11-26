"""InfraStat API Router v1."""

from fastapi import APIRouter

from .endpoints import batches, ingestion


api_router = APIRouter()
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(batches.router, prefix="/batches", tags=["batches"])

