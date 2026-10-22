"""
Neuro State Graph + Confidence Ledger REST API -- Lane B

Endpoints for querying the state graph, recording transitions, and
reading the confidence ledger. Uses DB persistence when a Session is
available, with in-memory fallback for tests.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.uuid7 import uuid7
from app.core.neuro_state_graph import (
    EdgeRelation,
    StateEdge,
    StateGraphService,
    StateGraphValidationError,
    StateNode,
    StateNodeType,
    StatePhase,
    StateTransition,
)
from app.core.confidence_ledger import (
    ConfidenceLedgerEntry,
    ConfidenceLedgerService,
    ConfidenceSource,
    GENESIS_HASH,
    RiskLevel,
)
from app.infrastructure.models.neuro_state_models import (
    ConfidenceLedgerRecord,
    StateEdgeRecord,
    StateNodeRecord,
    StateTransitionRecord,
)

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class NeuroStateOut(BaseSchema):
    """Typed response schema for NeuroStateOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class CreateNodeRequest(BaseModel):
    node_type: str
    phase: str = "entwurf"
    tenant_id: str
    aggregate_id: str
    aggregate_type: str
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TransitionRequest(BaseModel):
    to_phase: str
    triggered_by: str
    reason: str = ""
    case_run_id: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)


class CreateEdgeRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    relation: str
    tenant_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecordConfidenceRequest(BaseModel):
    tenant_id: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: str
    source: str
    reason: str
    case_run_id: str | None = None
    state_node_id: str | None = None
    model_id: str = ""
    model_version: str = ""
    input_data: dict[str, Any] | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    context_data: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# In-memory stores (fallback for tests)
# ---------------------------------------------------------------------------

_nodes: dict[str, StateNode] = {}
_edges: dict[str, StateEdge] = {}
_transitions: list[StateTransition] = []
_ledger: list[ConfidenceLedgerEntry] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node_record_to_model(record: StateNodeRecord) -> StateNode:
    return StateNode(
        node_id=record.node_id,
        node_type=StateNodeType(record.node_type),
        phase=StatePhase(record.phase),
        tenant_id=record.tenant_id,
        aggregate_id=record.aggregate_id,
        aggregate_type=record.aggregate_type,
        label=record.label,
        metadata=record.metadata_ or {},
        created_at=record.created_at,
        updated_at=record.updated_at or record.created_at,
        schema_version=record.schema_version,
    )


def _edge_record_to_model(record: StateEdgeRecord) -> StateEdge:
    return StateEdge(
        edge_id=record.edge_id,
        source_node_id=record.source_node_id,
        target_node_id=record.target_node_id,
        relation=EdgeRelation(record.relation),
        tenant_id=record.tenant_id,
        metadata=record.metadata_ or {},
        created_at=record.created_at,
        schema_version=record.schema_version,
    )


def _transition_record_to_model(record: StateTransitionRecord) -> StateTransition:
    return StateTransition(
        transition_id=record.transition_id,
        node_id=record.node_id,
        from_phase=StatePhase(record.from_phase),
        to_phase=StatePhase(record.to_phase),
        tenant_id=record.tenant_id,
        triggered_by=record.triggered_by,
        reason=record.reason or "",
        case_run_id=record.case_run_id,
        evidence_refs=record.evidence_refs or [],
        context_hash=record.context_hash or "",
        recorded_at=record.recorded_at,
        schema_version=record.schema_version,
    )


def _ledger_record_to_model(record: ConfidenceLedgerRecord) -> ConfidenceLedgerEntry:
    return ConfidenceLedgerEntry(
        entry_id=record.entry_id,
        tenant_id=record.tenant_id,
        case_run_id=record.case_run_id,
        state_node_id=record.state_node_id,
        confidence_score=record.confidence_score,
        risk_level=RiskLevel(record.risk_level),
        source=ConfidenceSource(record.source),
        model_id=record.model_id,
        model_version=record.model_version,
        input_hash=record.input_hash,
        reason=record.reason,
        evidence_refs=record.evidence_refs or [],
        context_data=record.context_data or {},
        previous_hash=record.previous_hash,
        chain_hash=record.chain_hash,
        recorded_at=record.recorded_at,
        schema_version=record.schema_version,
    )


# ---------------------------------------------------------------------------
# State Graph -- Nodes
# ---------------------------------------------------------------------------

@router.post("/state-graph/nodes", tags=["neuro-state-graph"], summary="Node anlegen",
    response_model=NeuroStateOut
)
async def create_node(req: CreateNodeRequest, db: Session | None = Depends(get_db)):
    """Register a new business-object node in the state graph."""
    try:
        node_type = StateNodeType(req.node_type)
        phase = StatePhase(req.phase)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    node_id = f"sn-{uuid7()}"
    node = StateNode(
        node_id=node_id,
        node_type=node_type,
        phase=phase,
        tenant_id=req.tenant_id,
        aggregate_id=req.aggregate_id,
        aggregate_type=req.aggregate_type,
        label=req.label,
        metadata=req.metadata,
    )

    if db is None:
        _nodes[node_id] = node
        logger.info("State node created (memory): %s (%s/%s)", node_id, node_type.value, phase.value)
        return node.model_dump(mode="json")

    record = StateNodeRecord(
        node_id=node.node_id,
        node_type=node.node_type.value,
        phase=node.phase.value,
        tenant_id=node.tenant_id,
        aggregate_id=node.aggregate_id,
        aggregate_type=node.aggregate_type,
        label=node.label,
        metadata_=node.metadata,
        schema_version=node.schema_version,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("State node created: %s (%s/%s)", node_id, node_type.value, phase.value)
    return _node_record_to_model(record).model_dump(mode="json")


@router.get("/state-graph/nodes", tags=["neuro-state-graph"], summary="Nodes auflisten",
    response_model=list[NeuroStateOut]
)
async def list_nodes(
    tenant_id: str = Query(...),
    node_type: str | None = Query(None),
    phase: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session | None = Depends(get_db),
):
    """List state nodes with optional filters."""
    if db is None:
        result = [n for n in _nodes.values() if n.tenant_id == tenant_id]
        if node_type:
            result = [n for n in result if n.node_type.value == node_type]
        if phase:
            result = [n for n in result if n.phase.value == phase]
        return [n.model_dump(mode="json") for n in result[:limit]]

    query = db.query(StateNodeRecord).filter(StateNodeRecord.tenant_id == tenant_id)
    if node_type:
        query = query.filter(StateNodeRecord.node_type == node_type)
    if phase:
        query = query.filter(StateNodeRecord.phase == phase)
    records = query.order_by(StateNodeRecord.created_at.desc()).limit(limit).all()
    return [_node_record_to_model(r).model_dump(mode="json") for r in records]


@router.get("/state-graph/nodes/{node_id}", tags=["neuro-state-graph"], summary="Node abrufen",
    response_model=NeuroStateOut
)
async def get_node(node_id: str, db: Session | None = Depends(get_db)):
    """Retrieve a single state node."""
    if db is None:
        node = _nodes.get(node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        return node.model_dump(mode="json")

    record = db.query(StateNodeRecord).filter(StateNodeRecord.node_id == node_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return _node_record_to_model(record).model_dump(mode="json")


@router.get("/state-graph/nodes/{node_id}/reachable", tags=["neuro-state-graph"], summary="Phases reachable",
    response_model=NeuroStateOut
)
async def reachable_phases(node_id: str, db: Session | None = Depends(get_db)):
    """Return phases reachable from the node's current phase."""
    if db is None:
        node = _nodes.get(node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        return {
            "node_id": node_id,
            "current_phase": node.phase.value,
            "reachable": StateGraphService.reachable_phases(node.node_type, node.phase),
        }

    record = db.query(StateNodeRecord).filter(StateNodeRecord.node_id == node_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    node = _node_record_to_model(record)
    return {
        "node_id": node_id,
        "current_phase": node.phase.value,
        "reachable": StateGraphService.reachable_phases(node.node_type, node.phase),
    }


# ---------------------------------------------------------------------------
# State Graph -- Transitions
# ---------------------------------------------------------------------------

@router.post("/state-graph/nodes/{node_id}/transitions", tags=["neuro-state-graph"], summary="Node transition",
    response_model=NeuroStateOut
)
async def transition_node(
    node_id: str,
    req: TransitionRequest,
    db: Session | None = Depends(get_db),
):
    """Record a phase transition for a node. Validates against the allowed matrix."""
    if db is None:
        node = _nodes.get(node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        try:
            to_phase = StatePhase(req.to_phase)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        try:
            transition = StateGraphService.build_transition(
                transition_id=f"st-{uuid7()}",
                node=node,
                to_phase=to_phase,
                triggered_by=req.triggered_by,
                reason=req.reason,
                case_run_id=req.case_run_id,
                evidence_refs=req.evidence_refs,
            )
        except StateGraphValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        node.phase = to_phase
        node.updated_at = datetime.now(timezone.utc)
        _transitions.append(transition)
        return transition.model_dump(mode="json")

    record = db.query(StateNodeRecord).filter(StateNodeRecord.node_id == node_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    try:
        to_phase = StatePhase(req.to_phase)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    node = _node_record_to_model(record)
    try:
        transition = StateGraphService.build_transition(
            transition_id=f"st-{uuid7()}",
            node=node,
            to_phase=to_phase,
            triggered_by=req.triggered_by,
            reason=req.reason,
            case_run_id=req.case_run_id,
            evidence_refs=req.evidence_refs,
        )
    except StateGraphValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    record.phase = to_phase.value
    record.updated_at = datetime.now(timezone.utc)
    transition_record = StateTransitionRecord(
        transition_id=transition.transition_id,
        node_id=transition.node_id,
        from_phase=transition.from_phase.value,
        to_phase=transition.to_phase.value,
        tenant_id=transition.tenant_id,
        triggered_by=transition.triggered_by,
        reason=transition.reason,
        case_run_id=transition.case_run_id,
        evidence_refs=transition.evidence_refs,
        context_hash=transition.context_hash,
        recorded_at=transition.recorded_at,
        schema_version=transition.schema_version,
    )
    db.add(transition_record)
    db.commit()
    return transition.model_dump(mode="json")


@router.get("/state-graph/nodes/{node_id}/transitions", tags=["neuro-state-graph"], summary="Transitions auflisten",
    response_model=list[NeuroStateOut]
)
async def list_transitions(
    node_id: str,
    limit: int = Query(50, le=200),
    db: Session | None = Depends(get_db),
):
    """List transition history for a node (most recent first)."""
    if db is None:
        result = [t for t in _transitions if t.node_id == node_id]
        result.sort(key=lambda t: t.recorded_at, reverse=True)
        return [t.model_dump(mode="json") for t in result[:limit]]

    records = (
        db.query(StateTransitionRecord)
        .filter(StateTransitionRecord.node_id == node_id)
        .order_by(StateTransitionRecord.recorded_at.desc())
        .limit(limit)
        .all()
    )
    return [_transition_record_to_model(r).model_dump(mode="json") for r in records]


# ---------------------------------------------------------------------------
# State Graph -- Edges
# ---------------------------------------------------------------------------

@router.post("/state-graph/edges", tags=["neuro-state-graph"], summary="Edge anlegen",
    response_model=NeuroStateOut
)
async def create_edge(req: CreateEdgeRequest, db: Session | None = Depends(get_db)):
    """Create a directed edge between two state nodes."""
    if db is None:
        if req.source_node_id not in _nodes:
            raise HTTPException(status_code=404, detail=f"Source node {req.source_node_id} not found")
        if req.target_node_id not in _nodes:
            raise HTTPException(status_code=404, detail=f"Target node {req.target_node_id} not found")
        try:
            relation = EdgeRelation(req.relation)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        edge_id = f"se-{uuid7()}"
        edge = StateEdge(
            edge_id=edge_id,
            source_node_id=req.source_node_id,
            target_node_id=req.target_node_id,
            relation=relation,
            tenant_id=req.tenant_id,
            metadata=req.metadata,
        )
        _edges[edge_id] = edge
        return edge.model_dump(mode="json")

    source_exists = db.query(StateNodeRecord).filter(StateNodeRecord.node_id == req.source_node_id).first()
    target_exists = db.query(StateNodeRecord).filter(StateNodeRecord.node_id == req.target_node_id).first()
    if not source_exists:
        raise HTTPException(status_code=404, detail=f"Source node {req.source_node_id} not found")
    if not target_exists:
        raise HTTPException(status_code=404, detail=f"Target node {req.target_node_id} not found")
    try:
        relation = EdgeRelation(req.relation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    edge_id = f"se-{uuid7()}"
    record = StateEdgeRecord(
        edge_id=edge_id,
        source_node_id=req.source_node_id,
        target_node_id=req.target_node_id,
        relation=relation.value,
        tenant_id=req.tenant_id,
        metadata_=req.metadata,
        schema_version=1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _edge_record_to_model(record).model_dump(mode="json")


@router.get("/state-graph/edges", tags=["neuro-state-graph"], summary="Edges auflisten",
    response_model=list[NeuroStateOut]
)
async def list_edges(
    tenant_id: str = Query(...),
    node_id: str | None = Query(None, description="Filter edges touching this node"),
    db: Session | None = Depends(get_db),
):
    """List edges, optionally filtered by a node."""
    if db is None:
        result = [e for e in _edges.values() if e.tenant_id == tenant_id]
        if node_id:
            result = [e for e in result if e.source_node_id == node_id or e.target_node_id == node_id]
        return [e.model_dump(mode="json") for e in result]

    query = db.query(StateEdgeRecord).filter(StateEdgeRecord.tenant_id == tenant_id)
    if node_id:
        query = query.filter(
            or_(
                StateEdgeRecord.source_node_id == node_id,
                StateEdgeRecord.target_node_id == node_id,
            )
        )
    records = query.order_by(StateEdgeRecord.created_at.desc()).all()
    return [_edge_record_to_model(r).model_dump(mode="json") for r in records]


# ---------------------------------------------------------------------------
# State Graph -- Metadata
# ---------------------------------------------------------------------------

@router.get("/state-graph/meta/node-types", tags=["neuro-state-graph"], summary="Node types auflisten",
    response_model=NeuroStateOut
)
async def list_node_types():
    """Return all available node types with their allowed transitions."""
    return {
        nt.value: StateGraphService.allowed_transitions(nt)
        for nt in StateNodeType
    }


# ---------------------------------------------------------------------------
# Confidence Ledger
# ---------------------------------------------------------------------------

@router.post("/confidence-ledger/entries", tags=["confidence-ledger"], summary="Confidence record",
    response_model=NeuroStateOut
)
async def record_confidence(req: RecordConfidenceRequest, db: Session | None = Depends(get_db)):
    """Append a new entry to the confidence ledger."""
    try:
        risk_level = RiskLevel(req.risk_level)
        source = ConfidenceSource(req.source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if db is None:
        previous_hash = _ledger[-1].chain_hash if _ledger else GENESIS_HASH
        entry = ConfidenceLedgerService.build_entry(
            entry_id=f"cl-{uuid7()}",
            tenant_id=req.tenant_id,
            confidence_score=req.confidence_score,
            risk_level=risk_level,
            source=source,
            reason=req.reason,
            previous_hash=previous_hash,
            case_run_id=req.case_run_id,
            state_node_id=req.state_node_id,
            model_id=req.model_id,
            model_version=req.model_version,
            input_data=req.input_data,
            evidence_refs=req.evidence_refs,
            context_data=req.context_data,
        )
        _ledger.append(entry)
        return entry.model_dump(mode="json")

    last_entry = (
        db.query(ConfidenceLedgerRecord)
        .filter(ConfidenceLedgerRecord.tenant_id == req.tenant_id)
        .order_by(ConfidenceLedgerRecord.recorded_at.desc(), ConfidenceLedgerRecord.entry_id.desc())
        .first()
    )
    previous_hash = last_entry.chain_hash if last_entry else GENESIS_HASH

    entry = ConfidenceLedgerService.build_entry(
        entry_id=f"cl-{uuid7()}",
        tenant_id=req.tenant_id,
        confidence_score=req.confidence_score,
        risk_level=risk_level,
        source=source,
        reason=req.reason,
        previous_hash=previous_hash,
        case_run_id=req.case_run_id,
        state_node_id=req.state_node_id,
        model_id=req.model_id,
        model_version=req.model_version,
        input_data=req.input_data,
        evidence_refs=req.evidence_refs,
        context_data=req.context_data,
    )
    record = ConfidenceLedgerRecord(
        entry_id=entry.entry_id,
        tenant_id=entry.tenant_id,
        case_run_id=entry.case_run_id,
        state_node_id=entry.state_node_id,
        confidence_score=entry.confidence_score,
        risk_level=entry.risk_level.value,
        source=entry.source.value,
        model_id=entry.model_id,
        model_version=entry.model_version,
        input_hash=entry.input_hash,
        reason=entry.reason,
        evidence_refs=entry.evidence_refs,
        context_data=entry.context_data,
        previous_hash=entry.previous_hash,
        chain_hash=entry.chain_hash,
        recorded_at=entry.recorded_at,
        schema_version=entry.schema_version,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _ledger_record_to_model(record).model_dump(mode="json")


@router.get("/confidence-ledger/entries", tags=["confidence-ledger"], summary="Confidence entries auflisten",
    response_model=list[NeuroStateOut]
)
async def list_confidence_entries(
    tenant_id: str = Query(...),
    case_run_id: str | None = Query(None),
    state_node_id: str | None = Query(None),
    source: str | None = Query(None),
    risk_level: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session | None = Depends(get_db),
):
    """Query confidence ledger entries with filters."""
    if db is None:
        result = [e for e in _ledger if e.tenant_id == tenant_id]
        if case_run_id:
            result = [e for e in result if e.case_run_id == case_run_id]
        if state_node_id:
            result = [e for e in result if e.state_node_id == state_node_id]
        if source:
            result = [e for e in result if e.source.value == source]
        if risk_level:
            result = [e for e in result if e.risk_level.value == risk_level]
        result.sort(key=lambda e: e.recorded_at, reverse=True)
        return [e.model_dump(mode="json") for e in result[:limit]]

    query = db.query(ConfidenceLedgerRecord).filter(ConfidenceLedgerRecord.tenant_id == tenant_id)
    if case_run_id:
        query = query.filter(ConfidenceLedgerRecord.case_run_id == case_run_id)
    if state_node_id:
        query = query.filter(ConfidenceLedgerRecord.state_node_id == state_node_id)
    if source:
        query = query.filter(ConfidenceLedgerRecord.source == source)
    if risk_level:
        query = query.filter(ConfidenceLedgerRecord.risk_level == risk_level)
    records = query.order_by(ConfidenceLedgerRecord.recorded_at.desc()).limit(limit).all()
    return [_ledger_record_to_model(r).model_dump(mode="json") for r in records]


@router.get("/confidence-ledger/entries/{entry_id}", tags=["confidence-ledger"], summary="Confidence entry abrufen",
    response_model=NeuroStateOut
)
async def get_confidence_entry(entry_id: str, db: Session | None = Depends(get_db)):
    """Retrieve a single ledger entry."""
    if db is None:
        for entry in _ledger:
            if entry.entry_id == entry_id:
                return entry.model_dump(mode="json")
        raise HTTPException(status_code=404, detail=f"Ledger entry {entry_id} not found")

    record = db.query(ConfidenceLedgerRecord).filter(ConfidenceLedgerRecord.entry_id == entry_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Ledger entry {entry_id} not found")
    return _ledger_record_to_model(record).model_dump(mode="json")


@router.post("/confidence-ledger/verify", tags=["confidence-ledger"], summary="Chain verifizieren",
    response_model=NeuroStateOut
)
async def verify_chain(tenant_id: str = Query(...), db: Session | None = Depends(get_db)):
    """Verify the hash-chain integrity for a tenant's ledger."""
    if db is None:
        tenant_entries = [e for e in _ledger if e.tenant_id == tenant_id]
        tenant_entries.sort(key=lambda e: e.recorded_at)
        try:
            ConfidenceLedgerService.verify_chain(tenant_entries)
            return {
                "status": "intact",
                "entries_verified": len(tenant_entries),
                "head_hash": tenant_entries[-1].chain_hash if tenant_entries else GENESIS_HASH,
            }
        except Exception as exc:
            return {
                "status": "broken",
                "entries_verified": len(tenant_entries),
                "error": str(exc),
            }

    records = (
        db.query(ConfidenceLedgerRecord)
        .filter(ConfidenceLedgerRecord.tenant_id == tenant_id)
        .order_by(ConfidenceLedgerRecord.recorded_at.asc(), ConfidenceLedgerRecord.entry_id.asc())
        .all()
    )
    entries = [_ledger_record_to_model(r) for r in records]
    try:
        ConfidenceLedgerService.verify_chain(entries)
        return {
            "status": "intact",
            "entries_verified": len(entries),
            "head_hash": entries[-1].chain_hash if entries else GENESIS_HASH,
        }
    except Exception as exc:
        return {
            "status": "broken",
            "entries_verified": len(entries),
            "error": str(exc),
        }


@router.get("/confidence-ledger/summary", tags=["confidence-ledger"], summary="Summary confidence",
    response_model=NeuroStateOut
)
async def confidence_summary(
    tenant_id: str = Query(...),
    case_run_id: str | None = Query(None),
    state_node_id: str | None = Query(None),
    db: Session | None = Depends(get_db),
):
    """Aggregated risk/confidence statistics."""
    if db is None:
        result = [e for e in _ledger if e.tenant_id == tenant_id]
        if case_run_id:
            result = [e for e in result if e.case_run_id == case_run_id]
        if state_node_id:
            result = [e for e in result if e.state_node_id == state_node_id]
        return ConfidenceLedgerService.risk_summary(result)

    query = db.query(ConfidenceLedgerRecord).filter(ConfidenceLedgerRecord.tenant_id == tenant_id)
    if case_run_id:
        query = query.filter(ConfidenceLedgerRecord.case_run_id == case_run_id)
    if state_node_id:
        query = query.filter(ConfidenceLedgerRecord.state_node_id == state_node_id)
    records = query.order_by(ConfidenceLedgerRecord.recorded_at.desc()).all()
    entries = [_ledger_record_to_model(r) for r in records]
    return ConfidenceLedgerService.risk_summary(entries)
