"""Typed additive schema proposals; no executable SQL or caller-supplied identity."""
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StudioColumnIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,47}$")
    type: Literal["text", "integer", "boolean", "date", "datetime", "decimal", "uuid"]
    nullable: bool = True


class StudioSchemaChangeIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation: Literal["create_table", "add_columns"]
    schema_name: str = Field(pattern=r"^domain_[a-z][a-z0-9_]{0,35}$")
    table: str = Field(pattern=r"^[a-z][a-z0-9_]{0,47}$")
    columns: list[StudioColumnIn] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def unique_columns(self):
        names = [column.name for column in self.columns]
        if len(names) != len(set(names)):
            raise ValueError("duplicate_columns")
        if set(names) & {"id", "tenant_id", "version", "created_by", "created_at", "updated_by", "updated_at"}:
            raise ValueError("identity_and_audit_columns_are_server_owned")
        if self.operation == "add_columns" and any(not column.nullable for column in self.columns):
            raise ValueError("required_existing_column_needs_explicit_backfill_migration")
        return self


class StudioMigrationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    definition: dict[str, Any]
    schema_changes: list[StudioSchemaChangeIn] = Field(default_factory=list, max_length=20)


class StudioMigrationOut(BaseModel):
    plan_version: Literal[1] = 1
    tenant_id: str
    actor: str
    plan_hash: str
    definition_hash: str
    catalog_hash: str
    schema_catalog_hash: str
    definition: dict[str, Any]
    bindings: list[str]
    blockers: list[str]
    migration_filename: str | None = None
    migration_source: str | None = None
    migration_hash: str | None = None
    channel_status: dict[str, Literal["not_verified"]] = Field(default_factory=lambda: {
        "human": "not_verified", "cli": "not_verified", "mcp": "not_verified"})
    required_contracts: list[str] = Field(default_factory=lambda: [
        "same_domain_commands", "verified_tenant", "tenant_isolation", "domain_roles",
        "record_permissions", "idempotency", "negative_cases", "human_cli_mcp_parity"])
    can_activate: Literal[False] = False


class StudioSavedMigrationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: UUID = Field(strict=False)
    schema_changes: list[StudioSchemaChangeIn] = Field(default_factory=list, max_length=20)


class StudioSavedMigrationOut(BaseModel):
    event_id: str
    draft_id: str
    candidate_revision: str
    candidate_definition_hash: str
    binding_hash: str
    requires_definition_update: bool
    schema_changes: list[StudioSchemaChangeIn]
    plan: StudioMigrationOut
