"""
SSE Manager - Production-Ready
Manages Server-Sent Events with reconnection, heartbeat, and multi-channel support
"""

import asyncio
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import Request
from fastapi.responses import StreamingResponse
import json

logger = logging.getLogger(__name__)


class SSEConnection:
    """Represents a single SSE connection."""
    
    def __init__(self, channel: str, client_id: str):
        self.channel = channel
        self.client_id = client_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
    
    async def send(self, data: Any) -> None:
        """Send data to this connection."""
        await self.queue.put(data)
    
    async def get(self) -> Any:
        """Get next message from queue."""
        return await self.queue.get()


class SSEManager:
    """
    Production-ready SSE Manager with:
    - Multi-channel support
    - Automatic reconnection
    - Heartbeat/ping
    - Connection tracking
    - Graceful shutdown
    """
    
    def __init__(self, heartbeat_interval: int = 30):
        self.connections: Dict[str, Set[SSEConnection]] = {}
        self.heartbeat_interval = heartbeat_interval
        self._heartbeat_task: Optional[asyncio.Task] = None
    
    def register(self, channel: str, connection: SSEConnection) -> None:
        """Register a new SSE connection."""
        if channel not in self.connections:
            self.connections[channel] = set()
        
        self.connections[channel].add(connection)
        logger.info(
            f"SSE connection registered: channel={channel}, "
            f"client={connection.client_id}, "
            f"total={len(self.connections[channel])}"
        )
    
    def unregister(self, channel: str, connection: SSEConnection) -> None:
        """Unregister an SSE connection."""
        if channel in self.connections:
            self.connections[channel].discard(connection)
            
            if not self.connections[channel]:
                del self.connections[channel]
            
            logger.info(
                f"SSE connection unregistered: channel={channel}, "
                f"client={connection.client_id}"
            )
    
    async def broadcast(
        self,
        channel: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> int:
        """Broadcast message to all connections on a channel."""
        if channel not in self.connections:
            logger.debug(f"No connections on channel: {channel}")
            return 0
        
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        sent_count = 0
        dead_connections = []
        
        for conn in self.connections[channel]:
            try:
                await conn.send(message)
                sent_count += 1
            except Exception as e:
                logger.warning(
                    f"Failed to send to {conn.client_id}: {e}"
                )
                dead_connections.append(conn)
        
        # Clean up dead connections
        for conn in dead_connections:
            self.unregister(channel, conn)
        
        if sent_count > 0:
            logger.debug(
                f"Broadcast to {sent_count} clients on channel={channel}"
            )
        
        return sent_count
    
    async def send_to_client(
        self,
        channel: str,
        client_id: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Send message to a specific client."""
        if channel not in self.connections:
            return False
        
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for conn in self.connections[channel]:
            if conn.client_id == client_id:
                try:
                    await conn.send(message)
                    return True
                except Exception as e:
                    logger.error(f"Failed to send to {client_id}: {e}")
                    return False
        
        return False
    
    async def start_heartbeat(self) -> None:
        """Start heartbeat task to keep connections alive."""
        if self._heartbeat_task is not None:
            return
        
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("SSE heartbeat started")
    
    async def stop_heartbeat(self) -> None:
        """Stop heartbeat task."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            logger.info("SSE heartbeat stopped")
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic pings to all connections."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                for channel, connections in list(self.connections.items()):
                    for conn in list(connections):
                        try:
                            await conn.send({"event": "ping", "data": {}})
                            conn.last_ping = datetime.utcnow()
                        except Exception as e:
                            logger.warning(f"Heartbeat failed for {conn.client_id}: {e}")
                            self.unregister(channel, conn)
                
                logger.debug("Heartbeat sent to all connections")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        total_connections = sum(
            len(conns) for conns in self.connections.values()
        )
        
        channel_stats = {
            channel: len(conns)
            for channel, conns in self.connections.items()
        }
        
        return {
            "total_connections": total_connections,
            "channels": len(self.connections),
            "channel_stats": channel_stats,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
_sse_manager: Optional[SSEManager] = None


def get_sse_manager() -> SSEManager:
    """Get the global SSE manager instance."""
    global _sse_manager
    if _sse_manager is None:
        _sse_manager = SSEManager()
    return _sse_manager


# SSE Stream Generator
async def sse_event_generator(request: Request, connection: SSEConnection):
    """Generate SSE events for a connection."""
    try:
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info(f"Client disconnected: {connection.client_id}")
                break
            
            try:
                # Wait for next message with timeout
                message = await asyncio.wait_for(
                    connection.get(),
                    timeout=1.0
                )
                
                # Format SSE message
                event_type = message.get("event", "message")
                data = message.get("data", {})
                
                sse_message = f"event: {event_type}\n"
                sse_message += f"data: {json.dumps(data)}\n\n"
                
                yield sse_message
                
            except asyncio.TimeoutError:
                # No message, continue loop
                continue
            
    except asyncio.CancelledError:
        logger.info(f"SSE stream cancelled: {connection.client_id}")
    except Exception as e:
        logger.error(f"SSE stream error: {e}", exc_info=True)
    finally:
        # Cleanup connection
        manager = get_sse_manager()
        manager.unregister(connection.channel, connection)


async def create_sse_stream(
    request: Request,
    channel: str,
    client_id: Optional[str] = None
) -> StreamingResponse:
    """Create an SSE stream for a channel."""
    if client_id is None:
        import uuid
        client_id = str(uuid.uuid4())
    
    connection = SSEConnection(channel, client_id)
    
    manager = get_sse_manager()
    manager.register(channel, connection)
    
    # Send initial connection message
    await connection.send({
        "event": "connected",
        "data": {
            "channel": channel,
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    })
    
    return StreamingResponse(
        sse_event_generator(request, connection),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )

