from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.channel_ingress import (
    build_slack_url_verification_response,
    dispatch_channel_ingress,
    is_slack_url_verification,
    is_slack_ignorable_event,
    maybe_post_slack_response,
    normalize_slack_event,
    normalize_teams_event,
    parse_json_body,
    verify_slack_signature,
    verify_teams_signature,
)
from app.core.channel_process_actions import (
    decide_channel_process_action,
    execute_channel_process_action,
    get_channel_process_thread_store,
)
from app.core.channel_work_surfaces import build_channel_knowledge_response
from app.core.database import get_db
from app.core.human_approval_gate import ApprovalDecision
from app.core.knowledge_core_contracts import KnowledgeChannel
from app.core.knowledge_graph import build_runtime_knowledge_graph

router = APIRouter(prefix="/channels", tags=["channels", "knowledge"])


class ChannelKnowledgeQueryRequest(BaseModel):
    rolle: str
    query: str
    tenant_id: str | None = None
    capability_key: str | None = None
    limit: int = 4


class ChannelProcessActionRequest(BaseModel):
    tenant_id: str
    process_definition_key: str
    command_name: str
    aggregate_type: str
    aggregate_id: str
    payload: dict
    issuer_role: str
    issuer_type: str = "human"
    idempotency_key: str
    employee_ref: str | None = None
    channel_user_id: str | None = None
    extra_context: dict | None = None


class ChannelApprovalDecisionRequest(BaseModel):
    decision: str
    entschieden_von: str
    approver_role: str
    begruendung: str


class KnowledgeGraphPathRequest(BaseModel):
    tenant_id: str | None = None
    source_id: str
    target_id: str


def _parse_supported_channel(channel: str) -> KnowledgeChannel:
    normalized = channel.strip().upper()
    if normalized not in {KnowledgeChannel.SLACK.value, KnowledgeChannel.TEAMS.value}:
        raise HTTPException(status_code=400, detail=f"Kanal {channel!r} wird nicht unterstuetzt")
    return KnowledgeChannel(normalized)


@router.post("/{channel}/knowledge-query")
def channel_knowledge_query(channel: str, payload: ChannelKnowledgeQueryRequest, db=Depends(get_db)):
    if not payload.rolle:
        raise HTTPException(status_code=400, detail="Feld 'rolle' ist erforderlich")
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Feld 'query' ist erforderlich")

    kanal = _parse_supported_channel(channel)
    result = build_channel_knowledge_response(
        db=db,
        kanal=kanal,
        rolle=payload.rolle,
        tenant_id=payload.tenant_id,
        query=payload.query,
        capability_key=payload.capability_key,
        limit=payload.limit,
    )
    return result.as_dict()


@router.post("/{channel}/process-actions/execute")
def channel_process_execute(channel: str, payload: ChannelProcessActionRequest, db=Depends(get_db)):
    from app.core.blockchain_anchor_runtime import anchor_channel_process_thread

    kanal = _parse_supported_channel(channel)
    thread = execute_channel_process_action(
        kanal=kanal,
        tenant_id=payload.tenant_id,
        process_definition_key=payload.process_definition_key,
        command_name=payload.command_name,
        aggregate_type=payload.aggregate_type,
        aggregate_id=payload.aggregate_id,
        payload=payload.payload,
        issuer_role=payload.issuer_role,
        issuer_type=payload.issuer_type,
        idempotency_key=payload.idempotency_key,
        employee_ref=payload.employee_ref,
        channel_user_id=payload.channel_user_id,
        extra_context=payload.extra_context,
        store=get_channel_process_thread_store(db),
    )
    anchor = anchor_channel_process_thread(db, thread=thread)
    body = thread.as_dict()
    body["blockchain_anchor"] = anchor.as_dict()
    return body


@router.get("/{channel}/process-actions/{thread_id}")
def get_channel_process_thread(channel: str, thread_id: str, db=Depends(get_db)):
    _parse_supported_channel(channel)
    thread = get_channel_process_thread_store(db).get(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread nicht gefunden")
    return thread.as_dict()


@router.get("/{channel}/process-actions")
def list_channel_process_threads(
    channel: str,
    tenant_id: str | None = None,
    status: str | None = None,
    process_definition_key: str | None = None,
    limit: int = 50,
    db=Depends(get_db),
):
    kanal = _parse_supported_channel(channel)
    threads = get_channel_process_thread_store(db).list_threads(
        kanal=kanal.value,
        tenant_id=tenant_id,
        status=status,
        process_definition_key=process_definition_key,
        limit=limit,
    )
    return {
        "items": [thread.as_dict() for thread in threads],
        "total": len(threads),
        "filters": {
            "kanal": kanal.value,
            "tenant_id": tenant_id,
            "status": status,
            "process_definition_key": process_definition_key,
            "limit": limit,
        },
    }


@router.get("/{channel}/process-actions/{thread_id}/audit")
def get_channel_process_thread_audit(channel: str, thread_id: str, db=Depends(get_db)):
    _parse_supported_channel(channel)
    store = get_channel_process_thread_store(db)
    thread = store.get(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread nicht gefunden")
    audit_trail = store.get_audit_trail(thread_id)
    return {
        "thread_id": thread_id,
        "status": thread.status,
        "audit_trail": [item.as_dict() for item in (audit_trail or [])],
        "count": len(audit_trail or []),
    }


@router.post("/{channel}/process-actions/{thread_id}/decision")
def channel_process_decision(channel: str, thread_id: str, payload: ChannelApprovalDecisionRequest, db=Depends(get_db)):
    from app.core.blockchain_anchor_runtime import anchor_channel_process_thread

    _parse_supported_channel(channel)
    try:
        decision = ApprovalDecision(payload.decision.strip().upper())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Ungueltige Freigabeentscheidung") from exc

    try:
        thread = decide_channel_process_action(
            thread_id=thread_id,
            decision=decision,
            entschieden_von=payload.entschieden_von,
            approver_role=payload.approver_role,
            begruendung=payload.begruendung,
            store=get_channel_process_thread_store(db),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    anchor = anchor_channel_process_thread(db, thread=thread)
    body = thread.as_dict()
    body["blockchain_anchor"] = anchor.as_dict()
    return body


@router.get("/knowledge-graph")
def get_knowledge_graph(tenant_id: str | None = None, db=Depends(get_db)):
    graph = build_runtime_knowledge_graph(db, tenant_id=tenant_id)
    return graph.as_dict()


@router.get("/knowledge-graph/nodes/{node_id}")
def get_knowledge_graph_node(node_id: str, tenant_id: str | None = None, db=Depends(get_db)):
    graph = build_runtime_knowledge_graph(db, tenant_id=tenant_id)
    node = graph.get_node(node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="Knoten nicht gefunden")
    return {
        "node": node.as_dict(),
        "neighbors": [neighbor.as_dict() for neighbor in graph.neighbors(node_id)],
    }


@router.post("/knowledge-graph/path")
def get_knowledge_graph_path(payload: KnowledgeGraphPathRequest, db=Depends(get_db)):
    graph = build_runtime_knowledge_graph(db, tenant_id=payload.tenant_id)
    path = graph.find_path(payload.source_id, payload.target_id)
    return {
        "source_id": payload.source_id,
        "target_id": payload.target_id,
        "path": path,
        "found": bool(path),
    }


@router.post("/slack/events")
async def slack_events(request: Request, db=Depends(get_db)):
    raw_body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    if not verify_slack_signature(raw_body, timestamp, signature):
        raise HTTPException(status_code=401, detail="Slack-Signatur ungueltig")
    payload = parse_json_body(raw_body)
    if is_slack_url_verification(payload):
        return build_slack_url_verification_response(payload)
    if is_slack_ignorable_event(payload):
        return {"ignored": True, "reason": "bot_or_non_user_event"}
    envelope = normalize_slack_event(payload)
    try:
        result = dispatch_channel_ingress(db, envelope)
        await maybe_post_slack_response(payload, result)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Pflichtfeld fehlt: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/teams/events")
async def teams_events(request: Request, db=Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("X-Teams-Signature")
    if not verify_teams_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Teams-Signatur ungueltig")
    payload = parse_json_body(raw_body)
    envelope = normalize_teams_event(payload)
    try:
        return dispatch_channel_ingress(db, envelope)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Pflichtfeld fehlt: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
