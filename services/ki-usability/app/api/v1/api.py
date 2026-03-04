"""
KI Usability API v1 router
"""

from fastapi import APIRouter

from .endpoints import actions, voice, health

api_router = APIRouter()
api_router.include_router(actions.router, prefix="/actions", tags=["actions"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
