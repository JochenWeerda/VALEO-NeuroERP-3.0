"""Pydantic schemas for the channel work surfaces domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class ChannelWorkSurfaceOut(BaseSchema):
    """Typed response schema for ChannelWorkSurfaceOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


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

