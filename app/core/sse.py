"""
Server-Sent Events Hub
"""

import asyncio
import json
from typing import Dict, Set
from fastapi import Request
from fastapi.responses import StreamingResponse


class SSEHub:
    """
    SSE-Hub für Broadcast-Messages
    """
    
    def __init__(self):
        self._channels: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()
    
    async def subscribe(self, channel: str) -> asyncio.Queue:
        """Subscribe to channel"""
        async with self._lock:
            if channel not in self._channels:
                self._channels[channel] = set()
            queue = asyncio.Queue(maxsize=100)
            self._channels[channel].add(queue)
            return queue
    
    async def unsubscribe(self, channel: str, queue: asyncio.Queue):
        """Unsubscribe from channel"""
        async with self._lock:
            if channel in self._channels:
                self._channels[channel].discard(queue)
                if not self._channels[channel]:
                    del self._channels[channel]
    
    async def broadcast(self, channel: str, data: dict):
        """Broadcast message to all subscribers"""
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
    
    def get_connection_count(self, channel: str) -> int:
        """Get active connection count for channel"""
        return len(self._channels.get(channel, set()))


# Global SSE-Hub
sse_hub = SSEHub()


async def sse_stream(request: Request, channel: str):
    """
    SSE-Stream-Generator
    """
    queue = await sse_hub.subscribe(channel)
    
    async def event_generator():
        try:
            # Initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'channel': channel})}\n\n"
            
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for message with timeout
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f": keepalive\n\n"
        
        finally:
            await sse_hub.unsubscribe(channel, queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
