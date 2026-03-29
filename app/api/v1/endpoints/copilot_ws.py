"""
Copilot WebSocket Streaming — NC-F3/F5
WebSocket-Endpoint fuer Echtzeit-AI-Streaming mit Neuro-Core Pipeline Integration.
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


def _run_pipeline_sync(user_text: str, session_context: dict) -> dict:
    """Fuehrt die Neuro-Core Pipeline synchron aus (NC-F5)."""
    try:
        from app.agents.neuro_pipeline import run_pipeline
        return run_pipeline(
            user_input=user_text,
            context=session_context,
            tenant_id=session_context.get("tenant_id", "system"),
            db=None,
            dry_run=False,
        )
    except Exception as exc:
        logger.warning("Pipeline execution failed: %s", exc)
        return {"status": "error", "message": str(exc)}


def _format_pipeline_response(result: dict) -> str:
    """Formatiert Pipeline-Ergebnis als lesbaren Text fuer den Chat."""
    status = result.get("status", "unknown")
    intent_data = result.get("intent", {})
    plan_data = result.get("plan")

    parts = []

    if status == "low_confidence":
        parts.append("Ich konnte Ihre Anfrage nicht eindeutig zuordnen. Bitte praezisieren Sie Ihr Anliegen.")
        return " ".join(parts)

    intent_name = intent_data.get("intent", "unknown")
    confidence = intent_data.get("confidence_score", 0)
    category = intent_data.get("category", "unknown")
    risk = intent_data.get("risk_class", "low")

    parts.append(f"Intent erkannt: **{intent_name}** (Kategorie: {category}, Confidence: {confidence:.0%}, Risiko: {risk}).")

    if plan_data:
        step_count = plan_data.get("step_count", 0)
        parts.append(f"Plan mit {step_count} Schritten generiert.")

        if status == "awaiting_approval":
            parts.append("Der Plan erfordert eine manuelle Freigabe aufgrund des Risiko-Levels.")
        elif status == "rejected":
            parts.append("Der Plan wurde von der Verification Engine abgelehnt.")
        elif status == "executed":
            parts.append("Alle Schritte wurden erfolgreich ausgefuehrt.")
        elif status == "dry_run":
            parts.append("Dry-Run — keine Ausfuehrung.")

        steps = plan_data.get("steps", [])
        if steps:
            parts.append("Schritte:")
            for s in steps[:5]:
                approval = " (Freigabe erforderlich)" if s.get("requires_approval") else ""
                parts.append(f"  {s.get('order', '?')}. {s.get('description', s.get('action', '?'))}{approval}")

    capability = intent_data.get("matched_capability")
    if capability:
        parts.append(f"Zugeordnete Capability: {capability}.")

    return " ".join(parts)


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
        "context": {"tenant_id": "system"},
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
            session_ctx = _SESSIONS[session_id].get("context", {})

            if msg.get("context"):
                session_ctx.update(msg["context"])
                _SESSIONS[session_id]["context"] = session_ctx

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

            pipeline_result = _run_pipeline_sync(user_text, session_ctx)

            await websocket.send_json({
                "type": "pipeline_result",
                "session_id": session_id,
                "result": pipeline_result,
            })

            response_text = _format_pipeline_response(pipeline_result)

            await websocket.send_json({
                "type": "stream_start",
                "session_id": session_id,
            })

            chunks = [response_text[i:i+40] for i in range(0, len(response_text), 40)]
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
                "pipeline_result": pipeline_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    except WebSocketDisconnect:
        logger.info("Copilot session %s disconnected", session_id)
    finally:
        _SESSIONS.pop(session_id, None)
