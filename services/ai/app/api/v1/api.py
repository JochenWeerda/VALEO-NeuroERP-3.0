"""
AI Service Main API Router
"""

from fastapi import APIRouter

from .endpoints import (
    assistants,
    classification,
    rag,
    agents,
    insights,
    mcp,
    autocomplete,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    assistants.router,
    prefix="/assistants",
    tags=["Assistants"]
)

api_router.include_router(
    classification.router,
    prefix="/classify",
    tags=["Classification"]
)

api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["RAG"]
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["Agents"]
)

api_router.include_router(
    insights.router,
    prefix="/insights",
    tags=["Insights"]
)

api_router.include_router(
    mcp.router,
    prefix="/mcp",
    tags=["MCP"]
)

api_router.include_router(
    autocomplete.router,
    prefix="/autocomplete",
    tags=["Autocomplete"]
)

