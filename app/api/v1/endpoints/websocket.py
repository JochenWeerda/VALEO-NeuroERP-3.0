"""
WebSocket Endpoints
Real-time bi-directional communication
"""

import logging
import json
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from typing import Dict, Set

from app.auth.jwt import decode_token
from app.core.config import settings

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()

# Active WebSocket connections per terminal
active_terminals: Dict[str, Set[WebSocket]] = {}


def _extract_websocket_token(websocket: WebSocket, query_token: str | None) -> str:
    if query_token:
        return query_token.strip()

    auth_header = (websocket.headers.get("authorization") or "").strip()
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return auth_header


def _resolve_authenticated_context(
    websocket: WebSocket,
    query_token: str | None,
    query_tenant_id: str | None,
) -> dict:
    token = _extract_websocket_token(websocket, query_token)
    if not token:
        raise ValueError("Missing bearer token")

    if settings.API_DEV_TOKEN and token == settings.API_DEV_TOKEN:
        user_id = "dev"
        roles: list[str] = ["admin"]
    else:
        claims = decode_token(token)
        user_id = (claims.get("sub") or "").strip()
        roles = claims.get("roles") or []
        if not isinstance(roles, list):
            roles = []
        if not user_id:
            raise ValueError("Invalid or expired token")

    tenant_id = (
        (query_tenant_id or "").strip()
        or (websocket.headers.get("x-tenant-id") or "").strip()
        or "system"
    )
    return {"user_id": user_id, "roles": roles, "tenant_id": tenant_id}


def _terminal_key(tenant_id: str, terminal_id: str) -> str:
    return f"{tenant_id}:{terminal_id}"


@router.websocket("/ws/pos/{terminal_id}")
async def pos_websocket(
    websocket: WebSocket,
    terminal_id: str,
    token: str | None = Query(None),
    tenant_id: str | None = Query(None),
):
    """
    WebSocket for POS terminal real-time sync.
    
    POS-Terminal broadcasts cart updates to all connected CustomerDisplays.
    """
    try:
        auth_context = _resolve_authenticated_context(websocket, token, tenant_id)
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc))
        return

    await websocket.accept()
    key = _terminal_key(auth_context["tenant_id"], terminal_id)

    # Register connection
    if key not in active_terminals:
        active_terminals[key] = set()
    active_terminals[key].add(websocket)
    
    logger.info("POS WebSocket connected: tenant=%s terminal=%s", auth_context["tenant_id"], terminal_id)
    
    try:
        while True:
            # Receive cart update from POS-Terminal
            data = await websocket.receive_text()
            cart_data = json.loads(data)
            
            logger.debug(
                "Cart update from tenant=%s terminal=%s: %s items",
                auth_context["tenant_id"],
                terminal_id,
                len(cart_data.get("cart", [])),
            )
            
            # Broadcast to all connected displays for this terminal
            for client in list(active_terminals[key]):
                if client != websocket:  # Don't send back to sender
                    try:
                        await client.send_text(data)
                    except Exception:
                        # Remove dead connections
                        active_terminals[key].discard(client)
    
    except WebSocketDisconnect:
        # Remove connection
        active_terminals[key].discard(websocket)
        if not active_terminals[key]:
            del active_terminals[key]
        
        logger.info("POS WebSocket disconnected: tenant=%s terminal=%s", auth_context["tenant_id"], terminal_id)
    
    except Exception as e:
        logger.error(f"POS WebSocket error: {e}", exc_info=True)
        active_terminals[key].discard(websocket)


@router.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket(
    websocket: WebSocket,
    workflow_id: str,
    token: str | None = Query(None),
    tenant_id: str | None = Query(None),
):
    """
    WebSocket for workflow progress updates.
    
    Alternative to SSE for bidirectional communication.
    """
    try:
        auth_context = _resolve_authenticated_context(websocket, token, tenant_id)
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc))
        return

    await websocket.accept()
    
    logger.info("Workflow WebSocket connected: tenant=%s workflow=%s", auth_context["tenant_id"], workflow_id)
    
    try:
        while True:
            # Receive commands (e.g., "cancel", "pause")
            data = await websocket.receive_text()
            command = json.loads(data)
            
            logger.info(f"Workflow command: {command}")
            
            if command.get("action") == "cancel":
                await websocket.send_json({
                    "type": "cancelled",
                    "workflow_id": workflow_id,
                    "message": "Workflow abgebrochen.",
                })
            elif command.get("action") == "status":
                from app.core.cache import cache_get_json
                cached = cache_get_json(f"workflow:{auth_context['tenant_id']}:{workflow_id}:status")
                await websocket.send_json({
                    "type": "status",
                    "workflow_id": workflow_id,
                    "tenant_id": auth_context["tenant_id"],
                    "data": cached or {"step": "unknown", "message": "Kein aktiver Lauf gefunden."},
                })
            else:
                await websocket.send_json({
                    "type": "ack",
                    "workflow_id": workflow_id,
                    "tenant_id": auth_context["tenant_id"],
                    "command": command,
                    "message": "Kommando empfangen.",
                })
    
    except WebSocketDisconnect:
        logger.info("Workflow WebSocket disconnected: tenant=%s workflow=%s", auth_context["tenant_id"], workflow_id)
    
    except Exception as e:
        logger.error(f"Workflow WebSocket error: {e}", exc_info=True)

