"""Pydantic schemas for the agents domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AgentOut(BaseSchema):
    """Typed response schema for AgentOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class CapabilityResponse(BaseModel):
    capability_key: str
    title: str
    kind: str
    domain: str
    role_key: str
    orchestration_pattern: str
    default_stage_sequence: list[str]
    readiness: str
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    description: str
    process_scopes: list[str]


class NeuroAssistRunRequest(BaseModel):
    capability_key: str
    tenant_id: str = "system"
    parameters: dict = Field(default_factory=dict)


class NeuroAssistRunResponse(BaseModel):
    run_id: str
    correlation_id: str
    capability_key: str
    status: str
    started_at: str
    runtime: dict
    result: dict = Field(default_factory=dict)


class NeuroAssistGateActionRequest(BaseModel):
    gate_type: str
    decision: str
    rejection_reason: str | None = None


class NeuroAssistGateActionResponse(BaseModel):
    run_id: str
    correlation_id: str
    capability_key: str
    started_at: str
    status: str
    runtime: dict
    result: dict = Field(default_factory=dict)


class AgentBudgetUpdateRequest(BaseModel):
    tenant_id: str = "system"
    monthly_budget_cents: int = Field(ge=0)
    changed_by: str = "admin-ui"


class AgentOpsOverviewResponse(BaseModel):
    tenant_id: str
    schema_version: int
    budget_total_cents: int
    spent_total_cents: int
    remaining_total_cents: int
    blocked_budget_count: int
    monthly_run_count: int
    budget_summaries: list[dict] = Field(default_factory=list)
    cost_ledger: list[dict] = Field(default_factory=list)
    heartbeats: list[dict] = Field(default_factory=list)
    roles: list[dict] = Field(default_factory=list)
    profiles: list[dict] = Field(default_factory=list)
    goals: list[dict] = Field(default_factory=list)
    open_tickets: list[dict] = Field(default_factory=list)


class AgentTicketResponse(BaseModel):
    tenant_id: str
    ticket_id: str
    run_id: str
    capability_key: str
    role_key: str
    goal_key: str
    status: str
    opened_at: str
    updated_at: str
    latest_stage_key: str
    latest_summary: str
    work_item_type: str = "agent_case"
    work_item_id: str | None = None
    work_item_title: str | None = None
    owner_role: str | None = None
    escalation_role: str | None = None
    allowed_actions: list[str] = Field(default_factory=list)
    blocker_reasons: list[str] = Field(default_factory=list)
    requires_review: bool = False
    is_stale: bool = False
    review_due_at: str | None = None
    age_minutes: int = 0


class AgentInterventionRequest(BaseModel):
    tenant_id: str = "system"
    action: str
    requested_by: str = "admin-ui"
    note: str | None = None


class AgentTemplateImportRequest(BaseModel):
    tenant_id: str = "system"
    template: dict


class AgentHeartbeatUpdateRequest(BaseModel):
    tenant_id: str = "system"
    cadence: str | None = None
    enabled: bool | None = None
    stale_after_hours: int | None = Field(default=None, ge=1)
    changed_by: str = "admin-ui"


class AgentProfileUpdateRequest(BaseModel):
    tenant_id: str = "system"
    owner_role: str | None = None
    escalation_role: str | None = None
    review_sla_hours: int | None = Field(default=None, ge=1)
    stale_after_hours: int | None = Field(default=None, ge=1)
    allowed_actions: list[str] | None = None
    changed_by: str = "admin-ui"


class AgentSkillPackUpdateRequest(BaseModel):
    tenant_id: str = "system"
    skills: list[str] | None = None
    prompt_contracts: list[str] | None = None
    changed_by: str = "admin-ui"


class LowStockSimulateRequest(BaseModel):
    tenant_id: str = "default"
    artikel_id: str
    artikel_name: str
    bestand: float = Field(ge=0)
    mindestbestand: float = Field(gt=0)
    einheit: str = "Stk"
    lieferant_id: str | None = None
    durchschnittlicher_verbrauch_pro_tag: float | None = Field(default=None, ge=0)


class AgentPersistenceStatusResponse(BaseModel):
    tenant_id: str
    state_path: str
    history_path: str
    persisted: bool
    persisted_at: str | None = None
    history_count: int
    recent_events: list[dict] = Field(default_factory=list)
    snapshot_counts: dict = Field(default_factory=dict)
    schema_version: int = 1


class ControlCenterPlanItemRequest(BaseModel):
    tenant_id: str = "system"
    plan_id: str
    title: str
    kind: str
    owner: str
    scheduled_for: str
    status: str
    notes: str | None = None


class ControlCenterIncidentActionRequest(BaseModel):
    tenant_id: str = "system"
    action: str
    requested_by: str = "admin-ui"
    note: str | None = None

