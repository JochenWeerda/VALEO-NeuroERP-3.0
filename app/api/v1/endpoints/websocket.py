"""
WebSocket Endpoints
Real-time bi-directional communication
"""

import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

logger = logging.getLogger(__name__)

router = APIRouter()

# Active WebSocket connections per terminal
active_terminals: Dict[str, Set[WebSocket]] = {}


@router.websocket("/ws/pos/{terminal_id}")
async def pos_websocket(websocket: WebSocket, terminal_id: str):
    """
    WebSocket for POS terminal real-time sync.
    
    POS-Terminal broadcasts cart updates to all connected CustomerDisplays.
    """
    await websocket.accept()
    
    # Register connection
    if terminal_id not in active_terminals:
        active_terminals[terminal_id] = set()
    active_terminals[terminal_id].add(websocket)
    
    logger.info(f"POS WebSocket connected: {terminal_id}")
    
    try:
        while True:
            # Receive cart update from POS-Terminal
            data = await websocket.receive_text()
            cart_data = json.loads(data)
            
            logger.debug(f"Cart update from {terminal_id}: {len(cart_data.get('cart', []))} items")
            
            # Broadcast to all connected displays for this terminal
            for client in active_terminals[terminal_id]:
                if client != websocket:  # Don't send back to sender
                    try:
                        await client.send_text(data)
                    except:
                        # Remove dead connections
                        active_terminals[terminal_id].discard(client)
    
    except WebSocketDisconnect:
        # Remove connection
        active_terminals[terminal_id].discard(websocket)
        if not active_terminals[terminal_id]:
            del active_terminals[terminal_id]
        
        logger.info(f"POS WebSocket disconnected: {terminal_id}")
    
    except Exception as e:
        logger.error(f"POS WebSocket error: {e}", exc_info=True)
        active_terminals[terminal_id].discard(websocket)


@router.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket(websocket: WebSocket, workflow_id: str):
    """
    WebSocket for workflow progress updates.
    
    Alternative to SSE for bidirectional communication.
    """
    await websocket.accept()
    
    logger.info(f"Workflow WebSocket connected: {workflow_id}")
    
    try:
        while True:
            # Receive commands (e.g., "cancel", "pause")
            data = await websocket.receive_text()
            command = json.loads(data)
            
            logger.info(f"Workflow command: {command}")
            
            # Send progress updates
            # TODO: Hook into workflow execution
            await websocket.send_json({
                "type": "progress",
                "workflow_id": workflow_id,
                "step": "analyzing",
                "message": "Analyzing stock levels..."
            })
    
    except WebSocketDisconnect:
        logger.info(f"Workflow WebSocket disconnected: {workflow_id}")
    
    except Exception as e:
        logger.error(f"Workflow WebSocket error: {e}", exc_info=True)

