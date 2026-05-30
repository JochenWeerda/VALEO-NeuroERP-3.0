"""Pydantic schemas for the neuro state graph api domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class NeuroStateOut(BaseSchema):
    """Typed response schema for NeuroStateOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


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

