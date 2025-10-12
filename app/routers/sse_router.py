"""
SSE Router
Server-Sent Events Endpoints
"""

from fastapi import APIRouter, Query, Request

from app.core.sse import sse_stream

router = APIRouter(tags=["sse"])


@router.get("/api/stream/{channel}")
async def stream_channel(request: Request, channel: str):
    """Stream server-sent events for a specific channel."""
    return await sse_stream(request, channel)


@router.get("/api/events")
async def stream_events(request: Request, stream: str = Query("mcp")):
    """Compatibility endpoint used by the frontend SSE client."""
    channel = stream or "mcp"
    return await sse_stream(request, channel)

