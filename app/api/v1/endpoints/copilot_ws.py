"""
Copilot WebSocket Streaming — NC-F3/F5
WebSocket-Endpoint fuer Echtzeit-AI-Streaming mit Neuro-Core Pipeline Integration.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.auth.jwt import decode_token
from app.core.config import settings

router = APIRouter(tags=["neuro-core", "copilot"])
logger = logging.getLogger(__name__)

_SESSIONS: dict[str, dict] = {}


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

    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
    }


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
    tenant_id: str | None = Query(None),
):
    try:
        auth_context = _resolve_authenticated_context(websocket, token, tenant_id)
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc))
        return

    await websocket.accept()
    session_id = str(uuid4())
    _SESSIONS[session_id] = {
        "state": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
        "context": {
            "tenant_id": auth_context["tenant_id"],
            "user_id": auth_context["user_id"],
            "roles": auth_context["roles"],
        },
    }

    try:
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id,
            "state": "new",
            "tenant_id": auth_context["tenant_id"],
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
                incoming_context = dict(msg["context"])
                incoming_context.pop("tenant_id", None)
                incoming_context.pop("user_id", None)
                incoming_context.pop("roles", None)
                session_ctx.update(incoming_context)

            session_ctx["tenant_id"] = auth_context["tenant_id"]
            session_ctx["user_id"] = auth_context["user_id"]
            session_ctx["roles"] = auth_context["roles"]
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
