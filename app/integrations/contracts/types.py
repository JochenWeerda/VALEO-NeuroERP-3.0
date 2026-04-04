"""Source-of-truth integration types for external providers."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

IntegrationProviderKey = Literal["superglue"]
IntegrationExecutionMode = Literal["read", "suggest", "simulate", "execute"]
IntegrationTargetKind = Literal["tool", "connection", "document", "partner_adapter", "customer_profile", "external_api"]
IntegrationAuthModel = Literal["none", "bearer", "api_key", "oauth2", "superglue_token"]
IntegrationResultStatus = Literal["success", "error", "partial", "pending"]


class SuperglueToolRecord(BaseModel):
    """Normalized provider tool metadata after mapping into VALEO's integration layer."""

    provider_key: IntegrationProviderKey = "superglue"
    external_tool_id: str = Field(min_length=1)
    external_tool_version: str = Field(min_length=1)
    valeo_contract_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    execution_modes: list[IntegrationExecutionMode] = Field(default_factory=list)
    target_kind: IntegrationTargetKind
    auth_model: IntegrationAuthModel
    schema_version: int = Field(default=1, ge=1)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
