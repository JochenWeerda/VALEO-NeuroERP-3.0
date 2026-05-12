"""Shared Agent Ops runtime for NeuroASSIST budgeting, costs, roles, goals, tickets and heartbeats."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from pydantic import BaseModel, Field

from .agent_ops_persistence import (
    build_agent_ops_persistence_status,
    load_agent_ops_tenant_snapshot,
    save_agent_ops_tenant_snapshot,
)
from .neuroassist import get_productive_neuroassist_capabilities


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


class AgentBudgetGuardrailExceededError(ValueError):
    """Raised when a tenant budget would be exceeded by a new run."""


class AgentBudgetSummary(BaseModel):
    tenant_id: str
    capability_key: str
    monthly_budget_cents: int = Field(ge=0)
    spent_cents: int = Field(ge=0)
    remaining_cents: int
    blocked: bool = False
    last_run_id: str | None = None
    version: int = 1


class AgentCostLedgerEntry(BaseModel):
    tenant_id: str
    run_id: str
    capability_key: str
    amount_cents: int = Field(ge=0)
    recorded_at: str
    status: str


class AgentHeartbeat(BaseModel):
    tenant_id: str
    heartbeat_key: str
    capability_key: str
    cadence: str
    enabled: bool = True
    owner_role: str
    next_run_hint: str
    last_run_id: str | None = None
    last_status: str | None = None
    stale_after_hours: int = 24
    version: int = 1


class AgentRoleNode(BaseModel):
    tenant_id: str
    role_key: str
    display_name: str
    domain: str
    reports_to: str | None = None
    owns_capabilities: list[str] = Field(default_factory=list)
    can_intervene: bool = True
    manages_roles: list[str] = Field(default_factory=list)


class AgentProfile(BaseModel):
    tenant_id: str
    profile_key: str
    capability_key: str
    display_name: str
    owner_role: str
    escalation_role: str
    review_sla_hours: int = 8
    stale_after_hours: int = 24
    allowed_actions: list[str] = Field(default_factory=list)
    version: int = 1


class AgentGoalNode(BaseModel):
    tenant_id: str
    goal_key: str
    title: str
    domain: str
    parent_goal_key: str | None = None
    capability_keys: list[str] = Field(default_factory=list)
    active_ticket_count: int = 0


class AgentTicket(BaseModel):
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


class AgentInterventionRecord(BaseModel):
    tenant_id: str
    intervention_id: str
    ticket_id: str
    run_id: str
    action: str
    requested_by: str
    note: str | None = None
    created_at: str
    resulting_status: str


class AgentSkillPack(BaseModel):
    tenant_id: str
    skill_pack_key: str
    display_name: str
    role_key: str
    capability_keys: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    prompt_contracts: list[str] = Field(default_factory=list)
    version: int = 1


class AgentConfigRevision(BaseModel):
    tenant_id: str
    revision_id: str
    config_type: str
    config_key: str
    version: int = Field(ge=1)
    changed_at: str
    changed_by: str
    summary: str


class AgentTemplateExport(BaseModel):
    tenant_id: str
    template_key: str
    exported_at: str
    budgets: list[AgentBudgetSummary] = Field(default_factory=list)
    heartbeats: list[AgentHeartbeat] = Field(default_factory=list)
    roles: list[AgentRoleNode] = Field(default_factory=list)
    profiles: list[AgentProfile] = Field(default_factory=list)
    goals: list[AgentGoalNode] = Field(default_factory=list)
    skill_packs: list[AgentSkillPack] = Field(default_factory=list)


class AgentOpsDashboard(BaseModel):
    tenant_id: str
    budget_health: str
    active_ticket_count: int = Field(ge=0)
    intervention_count: int = Field(ge=0)
    blocked_capabilities: list[str] = Field(default_factory=list)
    top_budget_pressures: list[AgentBudgetSummary] = Field(default_factory=list)
    recent_interventions: list[AgentInterventionRecord] = Field(default_factory=list)
    stale_work_count: int = Field(ge=0)
    review_queue_count: int = Field(ge=0)
    open_blocker_count: int = Field(ge=0)
    mobile_actions: list[str] = Field(default_factory=list)


class AgentMobileOpsOverview(BaseModel):
    tenant_id: str
    urgent_ticket_count: int = Field(ge=0)
    blocked_budget_count: int = Field(ge=0)
    pending_intervention_count: int = Field(ge=0)
    review_ticket_count: int = Field(ge=0)
    top_actions: list[str] = Field(default_factory=list)


class AgentPluginBoundaryReview(BaseModel):
    tenant_id: str
    schema_version: int = 1
    approved_patterns: list[str] = Field(default_factory=list)
    forbidden_patterns: list[str] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)


class AgentControlCenter(BaseModel):
    tenant_id: str
    dashboard: AgentOpsDashboard
    tickets: list[AgentTicket] = Field(default_factory=list)
    chain_of_command: list[AgentRoleNode] = Field(default_factory=list)
    config_revisions: list[AgentConfigRevision] = Field(default_factory=list)
    mobile_overview: AgentMobileOpsOverview


class AgentOpsOverview(BaseModel):
    tenant_id: str
    schema_version: int = 1
    budget_total_cents: int = Field(ge=0)
    spent_total_cents: int = Field(ge=0)
    remaining_total_cents: int
    blocked_budget_count: int = Field(ge=0)
    monthly_run_count: int = Field(ge=0)
    budget_summaries: list[AgentBudgetSummary] = Field(default_factory=list)
    cost_ledger: list[AgentCostLedgerEntry] = Field(default_factory=list)
    heartbeats: list[AgentHeartbeat] = Field(default_factory=list)
    roles: list[AgentRoleNode] = Field(default_factory=list)
    profiles: list[AgentProfile] = Field(default_factory=list)
    goals: list[AgentGoalNode] = Field(default_factory=list)
    open_tickets: list[AgentTicket] = Field(default_factory=list)


_CAPABILITY_COSTS_CENTS: dict[str, int] = {
    "bestellvorschlag_assistant": 180,
    "finance_skonto_assistant": 95,
    "compliance_copilot": 125,
    "data_quality_assistant": 140,
    "operations_exception_assistant": 160,
}

_CADENCE_BY_PATTERN: dict[str, str] = {
    "decision_workflow": "daily",
    "review_workflow": "daily",
    "ingestion_workflow": "hourly",
    "exception_workflow": "15m",
}


class AgentOpsService:
    """In-memory operational registry for agent governance surfaces."""

    _tenant_initialized: set[str] = set()
    _budgets: dict[str, dict[str, AgentBudgetSummary]] = defaultdict(dict)
    _ledger: dict[str, list[AgentCostLedgerEntry]] = defaultdict(list)
    _heartbeats: dict[str, dict[str, AgentHeartbeat]] = defaultdict(dict)
    _roles: dict[str, dict[str, AgentRoleNode]] = defaultdict(dict)
    _profiles: dict[str, dict[str, AgentProfile]] = defaultdict(dict)
    _goals: dict[str, dict[str, AgentGoalNode]] = defaultdict(dict)
    _tickets: dict[str, dict[str, AgentTicket]] = defaultdict(dict)
    _interventions: dict[str, list[AgentInterventionRecord]] = defaultdict(list)
    _skill_packs: dict[str, dict[str, AgentSkillPack]] = defaultdict(dict)
    _config_revisions: dict[str, list[AgentConfigRevision]] = defaultdict(list)

    @classmethod
    def _tenant_snapshot(cls, tenant_id: str) -> dict[str, Any]:
        return {
            "budgets": [item.model_dump(mode="json") for item in cls._budgets[tenant_id].values()],
            "ledger": [item.model_dump(mode="json") for item in cls._ledger[tenant_id]],
            "heartbeats": [item.model_dump(mode="json") for item in cls._heartbeats[tenant_id].values()],
            "roles": [item.model_dump(mode="json") for item in cls._roles[tenant_id].values()],
            "profiles": [item.model_dump(mode="json") for item in cls._profiles[tenant_id].values()],
            "goals": [item.model_dump(mode="json") for item in cls._goals[tenant_id].values()],
            "tickets": [item.model_dump(mode="json") for item in cls._tickets[tenant_id].values()],
            "interventions": [item.model_dump(mode="json") for item in cls._interventions[tenant_id]],
            "skill_packs": [item.model_dump(mode="json") for item in cls._skill_packs[tenant_id].values()],
            "config_revisions": [item.model_dump(mode="json") for item in cls._config_revisions[tenant_id]],
        }

    @classmethod
    def _restore_tenant_snapshot(cls, tenant_id: str, snapshot: dict[str, Any]) -> bool:
        if not snapshot:
            return False
        cls._budgets[tenant_id] = {
            item["capability_key"]: AgentBudgetSummary.model_validate(item)
            for item in snapshot.get("budgets", [])
        }
        cls._ledger[tenant_id] = [AgentCostLedgerEntry.model_validate(item) for item in snapshot.get("ledger", [])]
        cls._heartbeats[tenant_id] = {
            item["capability_key"]: AgentHeartbeat.model_validate(item)
            for item in snapshot.get("heartbeats", [])
        }
        cls._roles[tenant_id] = {
            item["role_key"]: AgentRoleNode.model_validate(item)
            for item in snapshot.get("roles", [])
        }
        cls._profiles[tenant_id] = {
            item["capability_key"]: AgentProfile.model_validate(item)
            for item in snapshot.get("profiles", [])
        }
        cls._goals[tenant_id] = {
            item["goal_key"]: AgentGoalNode.model_validate(item)
            for item in snapshot.get("goals", [])
        }
        cls._tickets[tenant_id] = {
            item["run_id"]: AgentTicket.model_validate(item)
            for item in snapshot.get("tickets", [])
        }
        cls._interventions[tenant_id] = [
            AgentInterventionRecord.model_validate(item) for item in snapshot.get("interventions", [])
        ]
        cls._skill_packs[tenant_id] = {
            item["skill_pack_key"]: AgentSkillPack.model_validate(item)
            for item in snapshot.get("skill_packs", [])
        }
        cls._config_revisions[tenant_id] = [
            AgentConfigRevision.model_validate(item) for item in snapshot.get("config_revisions", [])
        ]
        cls._tenant_initialized.add(tenant_id)
        return True

    @classmethod
    def _persist_tenant(cls, tenant_id: str, *, reason: str) -> None:
        save_agent_ops_tenant_snapshot(tenant_id, cls._tenant_snapshot(tenant_id), reason=reason)

    @classmethod
    def _append_revision(
        cls,
        tenant_id: str,
        *,
        config_type: str,
        config_key: str,
        version: int,
        changed_by: str,
        summary: str,
    ) -> None:
        cls._config_revisions[tenant_id].append(
            AgentConfigRevision(
                tenant_id=tenant_id,
                revision_id=f"rev-{config_type}-{config_key}-{version}",
                config_type=config_type,
                config_key=config_key,
                version=version,
                changed_at=_utcnow(),
                changed_by=changed_by,
                summary=summary,
            )
        )

    @classmethod
    def _ensure_tenant(cls, tenant_id: str) -> None:
        if tenant_id in cls._tenant_initialized:
            return

        if cls._restore_tenant_snapshot(tenant_id, load_agent_ops_tenant_snapshot(tenant_id) or {}):
            return

        capabilities = get_productive_neuroassist_capabilities()
        cls._roles[tenant_id]["tenant_operations_lead"] = AgentRoleNode(
            tenant_id=tenant_id,
            role_key="tenant_operations_lead",
            display_name="Tenant Operations Lead",
            domain="shared",
            reports_to=None,
            owns_capabilities=[],
        )
        managed_roles: list[str] = []
        goal_keys_by_domain: dict[str, str] = {}
        for capability in capabilities:
            monthly_budget = _CAPABILITY_COSTS_CENTS.get(capability.capability_key, 100) * 20
            cls._budgets[tenant_id][capability.capability_key] = AgentBudgetSummary(
                tenant_id=tenant_id,
                capability_key=capability.capability_key,
                monthly_budget_cents=monthly_budget,
                spent_cents=0,
                remaining_cents=monthly_budget,
            )
            cls._append_revision(
                tenant_id,
                config_type="budget",
                config_key=capability.capability_key,
                version=1,
                changed_by="system-bootstrap",
                summary=f"Initial monthly budget set to {monthly_budget} cents",
            )
            cls._heartbeats[tenant_id][capability.capability_key] = AgentHeartbeat(
                tenant_id=tenant_id,
                heartbeat_key=f"{capability.capability_key}.heartbeat",
                capability_key=capability.capability_key,
                cadence=_CADENCE_BY_PATTERN.get(capability.orchestration_pattern, "daily"),
                owner_role=capability.role_key,
                next_run_hint="scheduler://neuroassist/default",
            )
            cls._append_revision(
                tenant_id,
                config_type="heartbeat",
                config_key=capability.capability_key,
                version=1,
                changed_by="system-bootstrap",
                summary=f"Initial heartbeat cadence {_CADENCE_BY_PATTERN.get(capability.orchestration_pattern, 'daily')}",
            )
            cls._roles[tenant_id][capability.role_key] = AgentRoleNode(
                tenant_id=tenant_id,
                role_key=capability.role_key,
                display_name=capability.title,
                domain=capability.domain,
                reports_to="tenant_operations_lead",
                owns_capabilities=[capability.capability_key],
            )
            managed_roles.append(capability.role_key)
            cls._profiles[tenant_id][capability.capability_key] = AgentProfile(
                tenant_id=tenant_id,
                profile_key=capability.capability_key,
                capability_key=capability.capability_key,
                display_name=f"{capability.title} Profile",
                owner_role=capability.role_key,
                escalation_role="tenant_operations_lead",
                review_sla_hours=8,
                stale_after_hours=24,
                allowed_actions=["pause", "resume", "escalate"],
            )
            cls._append_revision(
                tenant_id,
                config_type="profile",
                config_key=capability.capability_key,
                version=1,
                changed_by="system-bootstrap",
                summary="Initial agent profile created",
            )
            domain_goal_key = goal_keys_by_domain.get(capability.domain)
            if domain_goal_key is None:
                domain_goal_key = f"{capability.domain}_ops"
                goal_keys_by_domain[capability.domain] = domain_goal_key
                cls._goals[tenant_id][domain_goal_key] = AgentGoalNode(
                    tenant_id=tenant_id,
                    goal_key=domain_goal_key,
                    title=f"{capability.domain.title()} Agent Operations",
                    domain=capability.domain,
                    capability_keys=[],
                )
            cls._goals[tenant_id][domain_goal_key].capability_keys.append(capability.capability_key)
            cls._goals[tenant_id][f"{capability.capability_key}.goal"] = AgentGoalNode(
                tenant_id=tenant_id,
                goal_key=f"{capability.capability_key}.goal",
                title=capability.title,
                domain=capability.domain,
                parent_goal_key=domain_goal_key,
                capability_keys=[capability.capability_key],
            )
            cls._skill_packs[tenant_id][f"{capability.role_key}.pack"] = AgentSkillPack(
                tenant_id=tenant_id,
                skill_pack_key=f"{capability.role_key}.pack",
                display_name=f"{capability.title} Skill Pack",
                role_key=capability.role_key,
                capability_keys=[capability.capability_key],
                skills=[
                    "policy_guardrails",
                    "human_handoff_contract",
                    "audit_traceability",
                ],
                prompt_contracts=[
                    f"{capability.capability_key}.prompt.default",
                    f"{capability.capability_key}.handoff.default",
                ],
            )
            cls._append_revision(
                tenant_id,
                config_type="skill_pack",
                config_key=f"{capability.role_key}.pack",
                version=1,
                changed_by="system-bootstrap",
                summary="Initial skill pack provisioned",
            )

        cls._roles[tenant_id]["tenant_operations_lead"].manages_roles = sorted(managed_roles)

        cls._tenant_initialized.add(tenant_id)
        cls._persist_tenant(tenant_id, reason="bootstrap")

    @classmethod
    def _estimate_run_cost_cents(cls, capability_key: str, runtime: dict[str, Any], result: dict[str, Any]) -> int:
        base = _CAPABILITY_COSTS_CENTS.get(capability_key, 100)
        gate_count = len(runtime.get("gate_decisions") or [])
        stage_count = len(runtime.get("stage_runs") or [])
        findings_count = len(result.get("dq_findings") or [])
        computed = Decimal(base) + Decimal(gate_count * 7) + Decimal(stage_count * 3) + Decimal(findings_count * 4)
        return int(computed.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @staticmethod
    def _minutes_since(timestamp: str) -> int:
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return 0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return max(int((datetime.now(UTC) - parsed.astimezone(UTC)).total_seconds() // 60), 0)

    @classmethod
    def _hydrate_ticket(cls, tenant_id: str, ticket: AgentTicket) -> AgentTicket:
        hydrated = ticket.model_copy(deep=True)
        profile = cls._profiles[tenant_id].get(hydrated.capability_key)
        if profile is not None:
            hydrated.owner_role = profile.owner_role
            hydrated.escalation_role = profile.escalation_role
            hydrated.allowed_actions = list(profile.allowed_actions)
            if hydrated.review_due_at is None:
                updated_at = datetime.fromisoformat(hydrated.updated_at.replace("Z", "+00:00"))
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=UTC)
                hydrated.review_due_at = (updated_at + timedelta(hours=profile.review_sla_hours)).isoformat()
        hydrated.age_minutes = cls._minutes_since(hydrated.updated_at)
        stale_after_hours = profile.stale_after_hours if profile is not None else 24
        hydrated.is_stale = hydrated.age_minutes >= stale_after_hours * 60 or hydrated.status in {"paused", "stale"}
        hydrated.requires_review = hydrated.status in {"pending_approval", "escalated", "review"} or bool(hydrated.blocker_reasons)
        return hydrated

    @classmethod
    def enforce_budget(
        cls,
        tenant_id: str,
        capability_key: str,
        *,
        projected_cost_cents: int | None = None,
    ) -> AgentBudgetSummary:
        cls._ensure_tenant(tenant_id)
        budget = cls._budgets[tenant_id][capability_key]
        projected = projected_cost_cents or _CAPABILITY_COSTS_CENTS.get(capability_key, 100)
        if budget.spent_cents + projected > budget.monthly_budget_cents:
            budget.blocked = True
            budget.remaining_cents = max(budget.monthly_budget_cents - budget.spent_cents, 0)
            raise AgentBudgetGuardrailExceededError(
                f"Agent budget for capability '{capability_key}' in tenant '{tenant_id}' would be exceeded"
            )
        return budget

    @classmethod
    def set_budget(
        cls,
        tenant_id: str,
        capability_key: str,
        monthly_budget_cents: int,
        *,
        changed_by: str = "admin-ui",
    ) -> AgentBudgetSummary:
        cls._ensure_tenant(tenant_id)
        budget = cls._budgets[tenant_id][capability_key]
        budget.monthly_budget_cents = monthly_budget_cents
        budget.remaining_cents = max(monthly_budget_cents - budget.spent_cents, 0)
        budget.blocked = budget.spent_cents >= monthly_budget_cents
        budget.version += 1
        cls._append_revision(
            tenant_id,
            config_type="budget",
            config_key=capability_key,
            version=budget.version,
            changed_by=changed_by,
            summary=f"Monthly budget changed to {monthly_budget_cents} cents",
        )
        cls._persist_tenant(tenant_id, reason=f"budget:{capability_key}")
        return budget

    @classmethod
    def set_heartbeat(
        cls,
        tenant_id: str,
        capability_key: str,
        *,
        cadence: str | None = None,
        enabled: bool | None = None,
        stale_after_hours: int | None = None,
        changed_by: str = "admin-ui",
    ) -> AgentHeartbeat:
        cls._ensure_tenant(tenant_id)
        heartbeat = cls._heartbeats[tenant_id][capability_key]
        if cadence is not None:
            heartbeat.cadence = cadence
        if enabled is not None:
            heartbeat.enabled = enabled
        if stale_after_hours is not None:
            heartbeat.stale_after_hours = stale_after_hours
        heartbeat.version += 1
        cls._append_revision(
            tenant_id,
            config_type="heartbeat",
            config_key=capability_key,
            version=heartbeat.version,
            changed_by=changed_by,
            summary=f"Heartbeat updated: cadence={heartbeat.cadence}, enabled={heartbeat.enabled}",
        )
        cls._persist_tenant(tenant_id, reason=f"heartbeat:{capability_key}")
        return heartbeat

    @classmethod
    def set_profile(
        cls,
        tenant_id: str,
        capability_key: str,
        *,
        owner_role: str | None = None,
        escalation_role: str | None = None,
        review_sla_hours: int | None = None,
        stale_after_hours: int | None = None,
        allowed_actions: list[str] | None = None,
        changed_by: str = "admin-ui",
    ) -> AgentProfile:
        cls._ensure_tenant(tenant_id)
        profile = cls._profiles[tenant_id][capability_key]
        if owner_role is not None:
            profile.owner_role = owner_role
        if escalation_role is not None:
            profile.escalation_role = escalation_role
        if review_sla_hours is not None:
            profile.review_sla_hours = review_sla_hours
        if stale_after_hours is not None:
            profile.stale_after_hours = stale_after_hours
        if allowed_actions is not None:
            profile.allowed_actions = list(allowed_actions)
        profile.version += 1
        cls._append_revision(
            tenant_id,
            config_type="profile",
            config_key=capability_key,
            version=profile.version,
            changed_by=changed_by,
            summary=f"Profile updated: owner={profile.owner_role}, escalation={profile.escalation_role}",
        )
        cls._persist_tenant(tenant_id, reason=f"profile:{capability_key}")
        return profile

    @classmethod
    def update_skill_pack(
        cls,
        tenant_id: str,
        skill_pack_key: str,
        *,
        skills: list[str] | None = None,
        prompt_contracts: list[str] | None = None,
        changed_by: str = "admin-ui",
    ) -> AgentSkillPack:
        cls._ensure_tenant(tenant_id)
        skill_pack = cls._skill_packs[tenant_id][skill_pack_key]
        if skills is not None:
            skill_pack.skills = list(skills)
        if prompt_contracts is not None:
            skill_pack.prompt_contracts = list(prompt_contracts)
        skill_pack.version += 1
        cls._append_revision(
            tenant_id,
            config_type="skill_pack",
            config_key=skill_pack_key,
            version=skill_pack.version,
            changed_by=changed_by,
            summary=f"Skill pack updated with {len(skill_pack.skills)} skills",
        )
        cls._persist_tenant(tenant_id, reason=f"skill-pack:{skill_pack_key}")
        return skill_pack

    @classmethod
    def record_run(
        cls,
        *,
        tenant_id: str,
        run_id: str,
        capability_key: str,
        role_key: str,
        status: str,
        current_stage_key: str,
        runtime: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        cls._ensure_tenant(tenant_id)
        cost = cls._estimate_run_cost_cents(capability_key, runtime, result)
        budget = cls._budgets[tenant_id][capability_key]
        profile = cls._profiles[tenant_id].get(capability_key)
        budget.spent_cents += cost
        budget.remaining_cents = max(budget.monthly_budget_cents - budget.spent_cents, 0)
        budget.blocked = budget.spent_cents >= budget.monthly_budget_cents
        budget.last_run_id = run_id

        cls._ledger[tenant_id].append(
            AgentCostLedgerEntry(
                tenant_id=tenant_id,
                run_id=run_id,
                capability_key=capability_key,
                amount_cents=cost,
                recorded_at=_utcnow(),
                status=status,
            )
        )
        heartbeat = cls._heartbeats[tenant_id][capability_key]
        heartbeat.last_run_id = run_id
        heartbeat.last_status = status

        goal_key = f"{capability_key}.goal"
        summary = result.get("exception_summary") or result.get("root_cause_summary") or result.get("current_stage_key") or current_stage_key
        blocker_reasons = [decision.get("gate_type", "gate") for decision in runtime.get("gate_decisions") or [] if decision.get("status") in {"blocked", "deferred", "escalated"}]
        requires_review = status in {"pending_approval", "escalated", "review"} or bool(blocker_reasons)
        ticket = cls._tickets[tenant_id].get(run_id)
        now = _utcnow()
        if ticket is None:
            ticket = AgentTicket(
                tenant_id=tenant_id,
                ticket_id=f"agt-{run_id}",
                run_id=run_id,
                capability_key=capability_key,
                role_key=role_key,
                goal_key=goal_key,
                status=status,
                opened_at=now,
                updated_at=now,
                latest_stage_key=current_stage_key,
                latest_summary=str(summary),
                work_item_id=result.get("workflow_id") or run_id,
                work_item_title=f"{capability_key.replace('_', ' ').title()} work item",
                owner_role=profile.owner_role if profile else role_key,
                escalation_role=profile.escalation_role if profile else "tenant_operations_lead",
                allowed_actions=list(profile.allowed_actions) if profile else ["pause", "resume", "escalate"],
                blocker_reasons=blocker_reasons,
                requires_review=requires_review,
            )
            cls._tickets[tenant_id][run_id] = ticket
        else:
            ticket.status = status
            ticket.updated_at = now
            ticket.latest_stage_key = current_stage_key
            ticket.latest_summary = str(summary)
            ticket.blocker_reasons = blocker_reasons
            ticket.requires_review = requires_review

        cls._recount_goal_tickets(tenant_id)
        cls._persist_tenant(tenant_id, reason=f"run:{run_id}")

    @classmethod
    def _recount_goal_tickets(cls, tenant_id: str) -> None:
        counts: dict[str, int] = defaultdict(int)
        for ticket in cls._tickets[tenant_id].values():
            if ticket.status not in {"completed", "rejected", "failed"}:
                counts[ticket.goal_key] += 1
                goal = cls._goals[tenant_id].get(ticket.goal_key)
                if goal and goal.parent_goal_key:
                    counts[goal.parent_goal_key] += 1
        for goal in cls._goals[tenant_id].values():
            goal.active_ticket_count = counts.get(goal.goal_key, 0)

    @classmethod
    def build_overview(cls, tenant_id: str = "system") -> AgentOpsOverview:
        cls._ensure_tenant(tenant_id)
        budgets = list(cls._budgets[tenant_id].values())
        ledger = list(cls._ledger[tenant_id])[-10:]
        goals = sorted(cls._goals[tenant_id].values(), key=lambda item: (item.parent_goal_key or "", item.goal_key))
        open_tickets = [cls._hydrate_ticket(tenant_id, ticket) for ticket in cls._tickets[tenant_id].values() if ticket.status not in {"completed", "rejected", "failed"}]
        budget_total = sum(item.monthly_budget_cents for item in budgets)
        spent_total = sum(item.spent_cents for item in budgets)
        return AgentOpsOverview(
            tenant_id=tenant_id,
            budget_total_cents=budget_total,
            spent_total_cents=spent_total,
            remaining_total_cents=max(budget_total - spent_total, 0),
            blocked_budget_count=sum(1 for item in budgets if item.blocked),
            monthly_run_count=len(cls._ledger[tenant_id]),
            budget_summaries=sorted(budgets, key=lambda item: item.capability_key),
            cost_ledger=sorted(ledger, key=lambda item: item.recorded_at, reverse=True),
            heartbeats=sorted(cls._heartbeats[tenant_id].values(), key=lambda item: item.capability_key),
            roles=sorted(cls._roles[tenant_id].values(), key=lambda item: item.role_key),
            profiles=sorted(cls._profiles[tenant_id].values(), key=lambda item: item.profile_key),
            goals=goals,
            open_tickets=sorted(open_tickets, key=lambda item: item.updated_at, reverse=True),
        )

    @classmethod
    def list_tickets(cls, tenant_id: str = "system", *, include_closed: bool = False) -> list[AgentTicket]:
        cls._ensure_tenant(tenant_id)
        tickets = [cls._hydrate_ticket(tenant_id, ticket) for ticket in cls._tickets[tenant_id].values()]
        if not include_closed:
            tickets = [ticket for ticket in tickets if ticket.status not in {"completed", "rejected", "failed"}]
        return sorted(tickets, key=lambda item: item.updated_at, reverse=True)

    @classmethod
    def list_interventions(cls, tenant_id: str = "system") -> list[AgentInterventionRecord]:
        cls._ensure_tenant(tenant_id)
        return sorted(cls._interventions[tenant_id], key=lambda item: item.created_at, reverse=True)

    @classmethod
    def apply_intervention(
        cls,
        tenant_id: str,
        ticket_id: str,
        *,
        action: str,
        requested_by: str,
        note: str | None = None,
    ) -> AgentInterventionRecord:
        cls._ensure_tenant(tenant_id)
        ticket = next((item for item in cls._tickets[tenant_id].values() if item.ticket_id == ticket_id), None)
        if ticket is None:
            raise KeyError(f"Agent ticket '{ticket_id}' not found")
        action_to_status = {
            "approve": "review",
            "pause": "paused",
            "resume": "running",
            "escalate": "escalated",
            "override": "override_granted",
            "close": "completed",
        }
        resulting_status = action_to_status.get(action)
        if resulting_status is None:
            raise ValueError(f"Unsupported intervention action '{action}'")
        ticket.status = resulting_status
        ticket.updated_at = _utcnow()
        ticket.latest_summary = note or f"Intervention: {action}"
        intervention = AgentInterventionRecord(
            tenant_id=tenant_id,
            intervention_id=f"agi-{ticket.run_id}-{len(cls._interventions[tenant_id]) + 1}",
            ticket_id=ticket.ticket_id,
            run_id=ticket.run_id,
            action=action,
            requested_by=requested_by,
            note=note,
            created_at=ticket.updated_at,
            resulting_status=resulting_status,
        )
        cls._interventions[tenant_id].append(intervention)
        cls._recount_goal_tickets(tenant_id)
        cls._persist_tenant(tenant_id, reason=f"intervention:{action}")
        return intervention

    @classmethod
    def list_skill_packs(cls, tenant_id: str = "system") -> list[AgentSkillPack]:
        cls._ensure_tenant(tenant_id)
        return sorted(cls._skill_packs[tenant_id].values(), key=lambda item: item.skill_pack_key)

    @classmethod
    def export_template(cls, tenant_id: str = "system", *, template_key: str = "default") -> AgentTemplateExport:
        cls._ensure_tenant(tenant_id)
        return AgentTemplateExport(
            tenant_id=tenant_id,
            template_key=template_key,
            exported_at=_utcnow(),
            budgets=[item.model_copy(deep=True) for item in cls._budgets[tenant_id].values()],
            heartbeats=[item.model_copy(deep=True) for item in cls._heartbeats[tenant_id].values()],
            roles=[item.model_copy(deep=True) for item in cls._roles[tenant_id].values()],
            profiles=[item.model_copy(deep=True) for item in cls._profiles[tenant_id].values()],
            goals=[item.model_copy(deep=True) for item in cls._goals[tenant_id].values()],
            skill_packs=[item.model_copy(deep=True) for item in cls._skill_packs[tenant_id].values()],
        )

    @classmethod
    def import_template(cls, tenant_id: str, template: AgentTemplateExport) -> AgentTemplateExport:
        cls._ensure_tenant(tenant_id)
        for budget in template.budgets:
            cls._budgets[tenant_id][budget.capability_key] = budget.model_copy(deep=True)
        for heartbeat in template.heartbeats:
            cls._heartbeats[tenant_id][heartbeat.capability_key] = heartbeat.model_copy(deep=True)
        for role in template.roles:
            cls._roles[tenant_id][role.role_key] = role.model_copy(deep=True)
        for profile in template.profiles:
            cls._profiles[tenant_id][profile.capability_key] = profile.model_copy(deep=True)
        for goal in template.goals:
            cls._goals[tenant_id][goal.goal_key] = goal.model_copy(deep=True)
        for skill_pack in template.skill_packs:
            cls._skill_packs[tenant_id][skill_pack.skill_pack_key] = skill_pack.model_copy(deep=True)
        cls._persist_tenant(tenant_id, reason=f"template-import:{template.template_key}")
        return cls.export_template(tenant_id, template_key=template.template_key)

    @classmethod
    def build_dashboard(cls, tenant_id: str = "system") -> AgentOpsDashboard:
        overview = cls.build_overview(tenant_id)
        blocked = [item.capability_key for item in overview.budget_summaries if item.blocked]
        budget_health = "blocked" if blocked else ("watch" if overview.spent_total_cents > (overview.budget_total_cents * 0.7) else "healthy")
        stale_work = [item for item in overview.open_tickets if item.is_stale]
        review_queue = [item for item in overview.open_tickets if item.requires_review]
        open_blockers = sum(len(item.blocker_reasons) for item in overview.open_tickets)
        return AgentOpsDashboard(
            tenant_id=tenant_id,
            budget_health=budget_health,
            active_ticket_count=len(overview.open_tickets),
            intervention_count=len(cls._interventions[tenant_id]),
            blocked_capabilities=blocked,
            top_budget_pressures=sorted(overview.budget_summaries, key=lambda item: item.remaining_cents)[:3],
            recent_interventions=cls.list_interventions(tenant_id)[:5],
            stale_work_count=len(stale_work),
            review_queue_count=len(review_queue),
            open_blocker_count=open_blockers,
            mobile_actions=[
                "Freigeben",
                "Pausieren",
                "Eskalieren",
                "Budgetwarnung ansehen",
            ],
        )

    @classmethod
    def build_mobile_overview(cls, tenant_id: str = "system") -> AgentMobileOpsOverview:
        overview = cls.build_overview(tenant_id)
        interventions = cls.list_interventions(tenant_id)
        return AgentMobileOpsOverview(
            tenant_id=tenant_id,
            urgent_ticket_count=len([item for item in overview.open_tickets if item.status in {"pending_approval", "escalated", "paused"}]),
            blocked_budget_count=overview.blocked_budget_count,
            pending_intervention_count=len([item for item in interventions if item.resulting_status in {"paused", "escalated"}]),
            review_ticket_count=len([item for item in overview.open_tickets if item.requires_review]),
            top_actions=[
                "Freigeben",
                "Pausieren",
                "Eskalieren",
                "Budgetwarnung ansehen",
            ],
        )

    @classmethod
    def list_config_revisions(cls, tenant_id: str = "system") -> list[AgentConfigRevision]:
        cls._ensure_tenant(tenant_id)
        return sorted(cls._config_revisions[tenant_id], key=lambda item: item.changed_at, reverse=True)

    @classmethod
    def build_control_center(cls, tenant_id: str = "system") -> AgentControlCenter:
        overview = cls.build_overview(tenant_id)
        return AgentControlCenter(
            tenant_id=tenant_id,
            dashboard=cls.build_dashboard(tenant_id),
            tickets=overview.open_tickets,
            chain_of_command=sorted(cls._roles[tenant_id].values(), key=lambda item: item.role_key),
            config_revisions=cls.list_config_revisions(tenant_id)[:12],
            mobile_overview=cls.build_mobile_overview(tenant_id),
        )

    @classmethod
    def build_plugin_boundary_review(cls, tenant_id: str = "system") -> AgentPluginBoundaryReview:
        cls._ensure_tenant(tenant_id)
        return AgentPluginBoundaryReview(
            tenant_id=tenant_id,
            approved_patterns=[
                "budget controls around existing NeuroASSIST runs",
                "thin UI wrappers over Agent Ops endpoints",
                "template export/import without secret material",
                "skill-pack manifests mapped to existing capability contracts",
            ],
            forbidden_patterns=[
                "second agent orchestrator beside NeuroASSIST",
                "parallel tool registry outside VALEO command manifest and Superglue",
                "plugins that bypass policy, approval or audit sinks",
                "embedding a full external company-control-plane into ERP core",
            ],
            rationale=[
                "VALEO keeps one orchestrator and one governance path for agentic work.",
                "External inspirations are accepted only as thin wrappers around existing contracts.",
                "Secrets, approvals and audits remain VALEO-owned responsibilities.",
            ],
        )

    @classmethod
    def reset(cls) -> None:
        cls._tenant_initialized.clear()
        cls._budgets.clear()
        cls._ledger.clear()
        cls._heartbeats.clear()
        cls._roles.clear()
        cls._profiles.clear()
        cls._goals.clear()
        cls._tickets.clear()
        cls._interventions.clear()
        cls._skill_packs.clear()
        cls._config_revisions.clear()

    @classmethod
    def build_persistence_status(cls, tenant_id: str = "system") -> dict[str, Any]:
        cls._ensure_tenant(tenant_id)
        return build_agent_ops_persistence_status(tenant_id)


def get_agent_ops_service() -> AgentOpsService:
    return AgentOpsService()
