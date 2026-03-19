"""
Signed inbound Slack/Teams event handling for channel work surfaces.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.channel_process_actions import (
    decide_channel_process_action,
    execute_channel_process_action,
)
from app.core.channel_work_surfaces import build_channel_knowledge_response
from app.core.config import settings
from app.core.human_approval_gate import ApprovalDecision
from app.core.knowledge_core_contracts import KnowledgeChannel


@dataclass
class ChannelIngressEnvelope:
    kanal: KnowledgeChannel
    intent: str
    tenant_id: str
    rolle: str
    query: str = ""
    capability_key: str | None = None
    employee_ref: str | None = None
    channel_user_id: str | None = None
    payload: dict[str, Any] | None = None


def _strip_slack_mentions(text: str) -> str:
    return re.sub(r"<@[^>]+>", "", text).strip()


def _compare(expected: str, provided: str) -> bool:
    return hmac.compare_digest(expected.encode("utf-8"), provided.encode("utf-8"))


def verify_slack_signature(raw_body: bytes, timestamp: str | None, signature: str | None) -> bool:
    secret = (settings.CHANNEL_SLACK_SIGNING_SECRET or "").strip()
    if not secret:
        return True
    if not timestamp or not signature:
        return False
    try:
        ts = int(timestamp)
    except ValueError:
        return False
    if abs(int(time.time()) - ts) > settings.CHANNEL_INGRESS_MAX_AGE_SECONDS:
        return False
    basestring = f"v0:{timestamp}:{raw_body.decode('utf-8')}"
    digest = hmac.new(secret.encode("utf-8"), basestring.encode("utf-8"), hashlib.sha256).hexdigest()
    return _compare(f"v0={digest}", signature)


def verify_teams_signature(raw_body: bytes, signature: str | None) -> bool:
    secret = (settings.CHANNEL_TEAMS_WEBHOOK_SECRET or "").strip()
    if not secret:
        return True
    if not signature:
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return _compare(digest, signature)


def parse_json_body(raw_body: bytes) -> dict[str, Any]:
    if not raw_body:
        return {}
    return json.loads(raw_body.decode("utf-8"))


def is_slack_url_verification(payload: dict[str, Any]) -> bool:
    return payload.get("type") == "url_verification" and "challenge" in payload


def build_slack_url_verification_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {"challenge": payload["challenge"]}


def is_slack_ignorable_event(payload: dict[str, Any]) -> bool:
    event = payload.get("event") or {}
    subtype = str(event.get("subtype") or "").strip().lower()
    if payload.get("type") == "event_callback" and event.get("bot_id"):
        return True
    return subtype in {"bot_message", "message_changed", "message_deleted"}


def extract_slack_reply_target(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    event = payload.get("event") or {}
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    return channel_id, thread_ts


def format_slack_dispatch_result(dispatch_result: dict[str, Any]) -> str:
    intent = str(dispatch_result.get("intent") or "")
    result = dispatch_result.get("result") or {}
    if intent == "knowledge_query":
        answer = str(result.get("answer") or "").strip()
        knowledge_ids = [str(item).strip() for item in result.get("knowledge_ids") or [] if str(item).strip()]
        if knowledge_ids:
            answer += f"\n\nQuellen: {', '.join(knowledge_ids[:4])}"
        return answer or "Die Anfrage wurde verarbeitet."

    if intent in {"process_execute", "approval_decision"}:
        message = str(result.get("message") or "").strip()
        status = str(result.get("status") or "").strip()
        thread_id = str(result.get("thread_id") or "").strip()
        parts = [part for part in [message, f"Status: {status}" if status else "", f"Thread: {thread_id}" if thread_id else ""] if part]
        return "\n".join(parts) or "Die Kanalaktion wurde verarbeitet."

    return "Die Slack-Anfrage wurde verarbeitet."


async def maybe_post_slack_response(payload: dict[str, Any], dispatch_result: dict[str, Any]) -> dict[str, Any] | None:
    token = (settings.CHANNEL_SLACK_BOT_TOKEN or "").strip()
    if not token or is_slack_ignorable_event(payload):
        return None

    channel_id, thread_ts = extract_slack_reply_target(payload)
    if not channel_id:
        return None

    text = format_slack_dispatch_result(dispatch_result)
    if not text.strip():
        return None

    request_payload: dict[str, Any] = {
        "channel": channel_id,
        "text": text,
        "unfurl_links": False,
        "unfurl_media": False,
    }
    if thread_ts:
        request_payload["thread_ts"] = thread_ts

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json=request_payload,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok", False):
            raise ValueError(f"Slack-Antwort konnte nicht zugestellt werden: {data.get('error', 'unknown_error')}")
        return data


def normalize_slack_event(payload: dict[str, Any]) -> ChannelIngressEnvelope:
    event = payload.get("event") or {}
    metadata = event.get("metadata") or payload.get("metadata") or {}
    event_type = str(event.get("type") or "").strip().lower()
    text = _strip_slack_mentions(str(event.get("text") or metadata.get("query") or "").strip())
    if event_type == "app_home_opened":
        text = text or "hilfe"
    return ChannelIngressEnvelope(
        kanal=KnowledgeChannel.SLACK,
        intent=str(metadata.get("intent") or "knowledge_query"),
        tenant_id=str(metadata.get("tenant_id") or settings.DEFAULT_TENANT_ID),
        rolle=str(metadata.get("rolle") or "support"),
        query=text,
        capability_key=metadata.get("capability_key"),
        employee_ref=metadata.get("employee_ref"),
        channel_user_id=event.get("user") or metadata.get("channel_user_id"),
        payload=dict(metadata.get("payload") or {}),
    )


def normalize_teams_event(payload: dict[str, Any]) -> ChannelIngressEnvelope:
    channel_data = payload.get("channelData") or {}
    metadata = channel_data.get("metadata") or {}
    text = str(payload.get("text") or metadata.get("query") or "").strip()
    from_block = payload.get("from") or {}
    return ChannelIngressEnvelope(
        kanal=KnowledgeChannel.TEAMS,
        intent=str(metadata.get("intent") or "knowledge_query"),
        tenant_id=str(metadata.get("tenant_id") or settings.DEFAULT_TENANT_ID),
        rolle=str(metadata.get("rolle") or "support"),
        query=text,
        capability_key=metadata.get("capability_key"),
        employee_ref=metadata.get("employee_ref"),
        channel_user_id=from_block.get("id") or metadata.get("channel_user_id"),
        payload=dict(metadata.get("payload") or {}),
    )


def dispatch_channel_ingress(db: Session, envelope: ChannelIngressEnvelope) -> dict[str, Any]:
    payload = envelope.payload or {}
    if envelope.intent == "knowledge_query":
        query = envelope.query.strip() or "hilfe"
        response = build_channel_knowledge_response(
            db=db,
            kanal=envelope.kanal,
            rolle=envelope.rolle,
            tenant_id=envelope.tenant_id,
            query=query,
            capability_key=envelope.capability_key,
            limit=int(payload.get("limit") or 4),
        )
        return {"intent": envelope.intent, "result": response.as_dict()}

    if envelope.intent == "process_execute":
        thread = execute_channel_process_action(
            kanal=envelope.kanal,
            tenant_id=envelope.tenant_id,
            process_definition_key=str(payload["process_definition_key"]),
            command_name=str(payload["command_name"]),
            aggregate_type=str(payload["aggregate_type"]),
            aggregate_id=str(payload["aggregate_id"]),
            payload=dict(payload.get("command_payload") or {}),
            issuer_role=envelope.rolle,
            issuer_type=str(payload.get("issuer_type") or "human"),
            idempotency_key=str(payload["idempotency_key"]),
            employee_ref=envelope.employee_ref,
            channel_user_id=envelope.channel_user_id,
            extra_context=dict(payload.get("extra_context") or {}),
        )
        return {"intent": envelope.intent, "result": thread.as_dict()}

    if envelope.intent == "approval_decision":
        decision = ApprovalDecision(str(payload["decision"]).strip().upper())
        thread = decide_channel_process_action(
            thread_id=str(payload["thread_id"]),
            decision=decision,
            entschieden_von=str(payload.get("entschieden_von") or envelope.channel_user_id or envelope.rolle),
            approver_role=str(payload["approver_role"]),
            begruendung=str(payload.get("begruendung") or envelope.query or "Channel approval decision"),
        )
        return {"intent": envelope.intent, "result": thread.as_dict()}

    raise ValueError(f"Unbekannter channel intent: {envelope.intent}")
