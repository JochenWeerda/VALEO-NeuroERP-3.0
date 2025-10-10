"""
SSE Router
Server-Sent Events Endpoints
"""

from fastapi import APIRouter, Request
from app.core.sse import sse_stream

router = APIRouter(prefix="/api/stream", tags=["sse"])


@router.get("/{channel}")
async def stream_channel(request: Request, channel: str):
    """
    SSE-Stream für Channel
    
    Channels:
    - workflow: Workflow-Status-Änderungen
    - sales: Sales-Events
    - inventory: Inventory-Events
    - policy: Policy-Updates
    """
    return await sse_stream(request, channel)

