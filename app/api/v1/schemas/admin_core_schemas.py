"""Pydantic schemas for the admin core domain."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class AdminUserOut(BaseModel):
    id: str
    name: str
    email: str
    rolle: str
    status: str
    letzteAnmeldung: str


class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=3, max_length=100)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, max_length=120)
    rolle: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="aktiv", pattern="^(aktiv|inaktiv)$")


class AdminUserUpdate(BaseModel):
    email: str | None = Field(default=None, min_length=3, max_length=100)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, max_length=120)
    rolle: str | None = Field(default=None, min_length=1, max_length=50)
    status: str | None = Field(default=None, pattern="^(aktiv|inaktiv)$")


class AdminRoleOut(BaseModel):
    id: str
    name: str
    beschreibung: str
    benutzer: int
    rechte: int


class AdminRoleCreate(BaseModel):
    id: str | None = Field(default=None, max_length=64)
    name: str = Field(..., min_length=1, max_length=64)
    beschreibung: str | None = Field(default="", max_length=255)
    rechte_liste: list[str] = Field(default_factory=list)


class AdminRoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    beschreibung: str | None = Field(default=None, max_length=255)
    rechte_liste: list[str] | None = None


class AdminAuditOut(BaseModel):
    id: str
    zeitstempel: str
    benutzer: str
    aktion: str
    objekt: str
    status: str


class AdminApiKeyOut(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    ip_allowlist: list[str]
    rate_limit_per_minute: int | None
    expires_at: str | None
    last_used_at: str | None
    status: str
    created_at: str


class AdminApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    scopes: list[str] = Field(default_factory=list)
    ip_allowlist: list[str] = Field(default_factory=list)
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=20000)
    expires_at: datetime | None = None


class AdminApiKeyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    scopes: list[str] | None = None
    ip_allowlist: list[str] | None = None
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=20000)
    expires_at: datetime | None = None


class AdminApiKeySecretOut(BaseModel):
    id: str
    name: str
    key_prefix: str
    token: str
    created_at: str


class AgentManifestLinkOut(BaseModel):
    rel: str
    href: str
    method: str = "GET"
    description: str


class AgentManifestExampleOut(BaseModel):
    name: str
    description: str
    method: str
    path: str
    required_headers: list[str] = Field(default_factory=list)


class AgentManifestOut(BaseModel):
    version: str
    generated_at: str
    auth: dict[str, Any]
    headers: list[str] = Field(default_factory=list)
    links: list[AgentManifestLinkOut] = Field(default_factory=list)
    examples: list[AgentManifestExampleOut] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ProcessVariantsOut(BaseModel):
    """Prozessvarianten-Konfiguration pro Tenant (Gap 009)."""

    variants: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="SchlÃ¼ssel = Prozess-Code (z.B. annahme, settlement), Wert = { steps, required_roles?, description? }",
    )


class PolicyOverridesOut(BaseModel):
    """Policy-Overrides pro Tenant (Gap 014). Ausnahmen regelbasiert dokumentiert."""

    overrides: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="SchlÃ¼ssel = rule_id, Wert = { enabled?, reason, valid_until?, params_override? }",
    )


class ErntefensterTemplateOut(BaseModel):
    """Eine Erntefenster-Vorlage (Raps, Weizen, Mais, etc.)."""

    id: str
    name: str
    description: str
    process_key: str
    default_start_mmdd: str
    default_end_mmdd: str
    product_groups: list[str]


class ErntefensterCampaignOut(BaseModel):
    """Eine aus Vorlage erstellte Erntefenster-Kampagne."""

    id: str
    template_id: str
    name: str
    start_date: str
    end_date: str
    process_key: str
    product_groups: list[str]
    created_at: str


class ErntefensterFromTemplateIn(BaseModel):
    """Payload zum Erstellen einer Kampagne aus Vorlage."""

    template_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=120)
    year: int = Field(..., ge=2020, le=2030)
    start_mmdd: str | None = Field(default=None, pattern=r"^\d{2}-\d{2}$")
    end_mmdd: str | None = Field(default=None, pattern=r"^\d{2}-\d{2}$")


class WorkflowSandboxPreviewIn(BaseModel):
    """Preview eines effektiven Prozessablaufs fuer Simulation/Sandbox (Gap 012)."""

    process_key: str = Field(..., min_length=1)
    simulation_date: date | None = None
    campaign_id: str | None = None
    product_group: str | None = Field(default=None, max_length=80)


class WorkflowSandboxCampaignMatchOut(BaseModel):
    id: str
    name: str
    start_date: str
    end_date: str
    process_key: str
    product_groups: list[str]
    in_window: bool
    product_group_match: bool


class WorkflowSandboxPreviewOut(BaseModel):
    process_key: str
    simulation_date: str
    definition_version: int = 1
    definition_origin: str = "default"
    definition_status: str = "active"
    steps: list[str]
    required_roles: dict[str, list[str]] = Field(default_factory=dict)
    step_sla: dict[str, dict[str, Any]] = Field(default_factory=dict)
    description: str | None = None
    matched_campaigns: list[WorkflowSandboxCampaignMatchOut] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

