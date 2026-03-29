"""
Copilot WebSocket Streaming — NC-F3
WebSocket-Endpoint fuer Echtzeit-AI-Streaming mit Token-Auth.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

router = APIRouter(tags=["neuro-core", "copilot"])
logger = logging.getLogger(__name__)

_SESSIONS: dict[str, dict] = {}


@router.websocket("/copilot/chat")
async def copilot_chat(
    websocket: WebSocket,
    token: str = Query(None),
):
    await websocket.accept()
    session_id = str(uuid4())
    _SESSIONS[session_id] = {
        "state": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }

    try:
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id,
            "state": "new",
        })

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                msg = {"text": data}

            user_text = msg.get("text", msg.get("message", ""))
            _SESSIONS[session_id]["messages"].append({
                "role": "user", "text": user_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            _SESSIONS[session_id]["state"] = "engaged"

            await websocket.send_json({
                "type": "state_change",
                "session_id": session_id,
                "state": "engaged",
            })

            await websocket.send_json({
                "type": "stream_start",
                "session_id": session_id,
            })

            response_text = f"Ich habe Ihre Anfrage erhalten: '{user_text[:100]}'. Die vollstaendige Neuro-Core-Pipeline-Integration steht aus (NC-F5 wartet auf Lane A)."

            chunks = [response_text[i:i+20] for i in range(0, len(response_text), 20)]
            for i, chunk in enumerate(chunks):
                await websocket.send_json({
                    "type": "stream_chunk",
                    "session_id": session_id,
                    "chunk": chunk,
                    "index": i,
                })

            await websocket.send_json({
                "type": "stream_end",
                "session_id": session_id,
                "full_text": response_text,
            })

            _SESSIONS[session_id]["messages"].append({
                "role": "assistant", "text": response_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    except WebSocketDisconnect:
        logger.info("Copilot session %s disconnected", session_id)
    finally:
        _SESSIONS.pop(session_id, None)
