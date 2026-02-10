"""
WebSocket Hub für Realtime Policy-Updates
"""

from __future__ import annotations
from typing import Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class WsHub:
    """WebSocket-Hub für Policy-Broadcasts"""

    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        """Verbindet neuen WebSocket-Client"""
        await ws.accept()
        self._clients.add(ws)
        logger.info(f"WebSocket connected. Total clients: {len(self._clients)}")

    def disconnect(self, ws: WebSocket) -> None:
        """Trennt WebSocket-Client"""
        self._clients.discard(ws)
        logger.info(f"WebSocket disconnected. Total clients: {len(self._clients)}")

    async def broadcast(self, msg: dict) -> None:
        """Sendet Message an alle verbundenen Clients"""
        if not self._clients:
            return

        dead: list[WebSocket] = []
        for ws in self._clients:
            try:
                await ws.send_json(msg)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead.append(ws)

        # Cleanup tote Connections
        for ws in dead:
            self.disconnect(ws)

        if msg:
            logger.info(
                f"Broadcasted {msg.get('type', 'unknown')} to {len(self._clients)} clients"
            )


# Global Hub Instance
hub = WsHub()

