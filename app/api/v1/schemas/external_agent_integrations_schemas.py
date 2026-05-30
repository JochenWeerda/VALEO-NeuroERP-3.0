"""Pydantic schemas for the external agent integrations domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class AgentIntegrationOut(BaseSchema):
    """Typed response schema for AgentIntegrationOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class SuperglueConnectorConfigRequest(BaseModel):
    system_url: str | None = None
    system_name: str | None = None
    system_instructions: str | None = None


class SupergluePolicyOverrideRequest(BaseModel):
    require_tenant_secrets: bool | None = None
    execution_enabled: bool | None = None
    alert_error_rate_pct: float | None = Field(default=None, ge=0)
    alert_open_quarantine_count: int | None = Field(default=None, ge=0)
    run_retention_days: int | None = Field(default=None, ge=1)
    artifact_retention_days: int | None = Field(default=None, ge=1)


class SuperglueWizardApplyRequest(BaseModel):
    connector_key: str | None = None
    system_url: str | None = None
    execution_enabled: bool | None = None
    require_tenant_secrets: bool | None = None
    alert_error_rate_pct: float | None = Field(default=None, ge=0)
    alert_open_quarantine_count: int | None = Field(default=None, ge=0)
    run_retention_days: int | None = Field(default=None, ge=1)
    artifact_retention_days: int | None = Field(default=None, ge=1)
    completed_step: str | None = None
    next_step: str | None = None

