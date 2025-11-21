"""
API Router für Version 1 des Workflow-Services.
"""

from fastapi import APIRouter

from .endpoints import workflows, sagas


api_router = APIRouter()
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(sagas.router, prefix="/sagas", tags=["sagas"])


