"""Shared execution result envelope for external integration providers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .types import (
    ExternalArtifactReference,
    IntegrationExecutionMode,
    IntegrationProviderKey,
    IntegrationResultStatus,
    IntegrationTargetKind,
)


class ExternalResultError(BaseModel):
    """Normalized external execution error entry."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class ExternalResultEnvelope(BaseModel):
    """Canonical result envelope returned by integration adapters and services."""

    provider_key: IntegrationProviderKey = "superglue"
    tenant_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    schema_version: int = Field(default=1, ge=1)
    execution_mode: IntegrationExecutionMode
    target_kind: IntegrationTargetKind
    result_status: IntegrationResultStatus
    cost_cents: int = Field(default=0, ge=0)
    idempotency_key: str | None = None
    replayed_from_correlation_id: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    artifacts: list[ExternalArtifactReference] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    errors: list[ExternalResultError] = Field(default_factory=list)
