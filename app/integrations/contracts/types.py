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


class SuperglueSystemBinding(BaseModel):
    system_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    credentials: dict[str, str] = Field(default_factory=dict)
    specific_instructions: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SuperglueConnectorBinding(BaseModel):
    connector_key: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    valeo_contract_id: str = Field(min_length=1)
    tool_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    target_kind: IntegrationTargetKind
    execution_modes: list[IntegrationExecutionMode] = Field(default_factory=list)
    system: SuperglueSystemBinding
    run_credentials: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExternalArtifactReference(BaseModel):
    artifact_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    storage_backend: str = Field(min_length=1)
    uri: str = Field(min_length=1)
    content_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
