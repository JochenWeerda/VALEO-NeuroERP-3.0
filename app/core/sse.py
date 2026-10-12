"""
Server-Sent Events Hub
"""

import asyncio
import json
import time
from typing import Dict, Set
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse


class SSEHub:
    """
    SSE-Hub für Broadcast-Messages
    """
    
    def __init__(self):
        self._channels: Dict[tuple[str, str], Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()
    
    async def subscribe(self, channel: str, *, tenant_id: str) -> asyncio.Queue:
        """Subscribe to channel"""
        channel = (tenant_id, channel)
        async with self._lock:
            if channel not in self._channels:
                self._channels[channel] = set()
            queue = asyncio.Queue(maxsize=100)
            self._channels[channel].add(queue)
            return queue
    
    async def unsubscribe(self, channel: str, queue: asyncio.Queue, *, tenant_id: str):
        """Unsubscribe from channel"""
        channel = (tenant_id, channel)
        async with self._lock:
            if channel in self._channels:
                self._channels[channel].discard(queue)
                if not self._channels[channel]:
                    del self._channels[channel]
    
    async def broadcast(self, channel: str, data: dict, *, tenant_id: str):
        """Broadcast message to all subscribers"""
        channel = (tenant_id, channel)
        async with self._lock:
            if channel not in self._channels:
                return
            
            dead_queues = set()
            for queue in self._channels[channel]:
                try:
                    queue.put_nowait(data)
                except asyncio.QueueFull:
                    dead_queues.add(queue)
            
            # Cleanup full queues
            for queue in dead_queues:
                self._channels[channel].discard(queue)
    
    def get_connection_count(self, channel: str, *, tenant_id: str) -> int:
        """Get active connection count for channel"""
        return len(self._channels.get((tenant_id, channel), set()))


# Global SSE-Hub
sse_hub = SSEHub()


async def sse_stream(request: Request, channel: str):
    """
    SSE-Stream-Generator
    """
    if not getattr(request.state, "tenant_verified", False):
        raise HTTPException(403, "Verified tenant context required")
    tenant = request.state.tenant_id
    expiry = request.state.token_claims["exp"]
    queue = await sse_hub.subscribe(channel, tenant_id=tenant)
    
    async def event_generator():
        try:
            # Initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'channel': channel})}\n\n"
            
            while time.time() < expiry:
                from app.core.identity_session import validate
                try:
                    await asyncio.to_thread(validate, request.state.token_claims, request.state.authenticated_token, touch=False)
                except HTTPException:
                    break
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for message with timeout
                    from app.core.config import settings
                    data = await asyncio.wait_for(queue.get(), timeout=min(settings.IDENTITY_REVOCATION_POLL_SECONDS, max(0.001, expiry - time.time())))
                    if time.time() < expiry:
                        try:
                            await asyncio.to_thread(validate, request.state.token_claims, request.state.authenticated_token, touch=False)
                        except HTTPException:
                            break
                        yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield ": keepalive\n\n"
        
        finally:
            await sse_hub.unsubscribe(channel, queue, tenant_id=tenant)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
