"""Core contracts for the NeuroASSIST orchestration model."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.business_commands import build_core_command_catalog


NeuroAssistStageKey = Literal[
    "intake",
    "analysis",
    "proposal",
    "approval",
    "execution",
    "verification",
    "closure",
    "improvement",
]

NeuroAssistGateType = Literal[
    "approval_gate",
    "policy_gate",
    "dq_gate",
    "role_gate",
    "process_gate",
]

GateDecisionStatus = Literal["allowed", "blocked", "escalated", "deferred"]
CaseRunStatus = Literal["pending", "running", "pending_approval", "completed", "rejected", "failed"]


class StageDefinition(BaseModel):
    """Stable stage contract for case-based orchestration."""

    stage_key: NeuroAssistStageKey
    title: str = Field(min_length=2)
    purpose: str = Field(min_length=8)
    allows_side_effects: bool = False
    required_inputs: list[str] = Field(default_factory=list)
    allowed_next_stages: list[NeuroAssistStageKey] = Field(default_factory=list)
    schema_version: int = 1


class GateDecision(BaseModel):
    """Result of an explicit orchestration gate."""

    gate_type: NeuroAssistGateType
    status: GateDecisionStatus
    reason: str = Field(min_length=3)
    required_role: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    schema_version: int = 1


class CaseStageTransition(BaseModel):
    """Persisted transition marker for one case stage."""

    stage_key: NeuroAssistStageKey
    timestamp: str = Field(min_length=10)
    status: Literal["entered", "completed", "blocked", "skipped"] = "entered"
    schema_version: int = 1


class RoleContract(BaseModel):
    """Operational scope and guardrails for one NeuroASSIST role."""

    role_key: str = Field(min_length=3)
    purpose: str = Field(min_length=8)
    scope_domains: list[str] = Field(default_factory=list)
    process_definitions: list[str] = Field(default_factory=list)
    owned_process_scopes: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    allowed_commands: list[str] = Field(default_factory=list)
    required_gates: list[NeuroAssistGateType] = Field(default_factory=list)
    explainability_requirements: list[str] = Field(default_factory=list)
    handover_requirements: list[str] = Field(default_factory=list)
    schema_version: int = 1


class CapabilityPack(BaseModel):
    """Technical execution boundary for one NeuroASSIST capability."""

    capability_key: str = Field(min_length=3)
    role_key: str = Field(min_length=3)
    workflow_schema_key: str = Field(min_length=3)
    prompt_pack_key: str = Field(min_length=3)
    execution_pack_key: str = Field(min_length=3)
    orchestration_pattern: str = Field(min_length=3)
    default_stage_sequence: list[NeuroAssistStageKey] = Field(default_factory=list)
    allowed_queries: list[str] = Field(default_factory=list)
    allowed_commands: list[str] = Field(default_factory=list)
    allowed_services: list[str] = Field(default_factory=list)
    required_gates: list[NeuroAssistGateType] = Field(default_factory=list)
    output_schema: str = Field(min_length=3)
    schema_version: int = 1


class PromptPack(BaseModel):
    """Structured prompt contract for one NeuroASSIST role or capability."""

    prompt_pack_key: str = Field(min_length=3)
    role_key: str = Field(min_length=3)
    mission: str = Field(min_length=8)
    scope: str = Field(min_length=8)
    constraints: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    decision_policy: list[str] = Field(default_factory=list)
    output_schema: str = Field(min_length=3)
    handover_rules: list[str] = Field(default_factory=list)
    schema_version: int = 1


class ExecutionPack(BaseModel):
    """Operational execution boundary for one NeuroASSIST capability."""

    execution_pack_key: str = Field(min_length=3)
    capability_key: str = Field(min_length=3)
    read_models: list[str] = Field(default_factory=list)
    policy_resolvers: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    audit_sinks: list[str] = Field(default_factory=list)
    side_effect_classes: list[str] = Field(default_factory=list)
    schema_version: int = 1


class WorkflowSchema(BaseModel):
    """Reusable orchestration schema for one workflow family."""

    workflow_schema_key: str = Field(min_length=3)
    title: str = Field(min_length=3)
    orchestration_pattern: str = Field(min_length=3)
    default_stage_sequence: list[NeuroAssistStageKey] = Field(default_factory=list)
    required_gates: list[NeuroAssistGateType] = Field(default_factory=list)
    terminal_statuses: list[CaseRunStatus] = Field(default_factory=list)
    schema_version: int = 1


class CaseRun(BaseModel):
    """Persisted contract for one NeuroASSIST case execution."""

    run_id: str = Field(min_length=3)
    capability_key: str = Field(min_length=3)
    workflow_schema_key: str = Field(min_length=3)
    tenant_id: str = Field(min_length=1)
    status: CaseRunStatus
    current_stage_key: NeuroAssistStageKey
    started_at: str = Field(min_length=10)
    completed_at: str | None = None
    stage_transition_log: list[CaseStageTransition] = Field(default_factory=list)
    gate_decisions: list[GateDecision] = Field(default_factory=list)
    result_refs: list[str] = Field(default_factory=list)
    schema_version: int = 1


_STAGE_DEFINITIONS: tuple[StageDefinition, ...] = (
    StageDefinition(
        stage_key="intake",
        title="Intake",
        purpose="Capture the case, signal, tenant and process context.",
        required_inputs=["case_context"],
        allowed_next_stages=["analysis", "closure"],
    ),
    StageDefinition(
        stage_key="analysis",
        title="Analysis",
        purpose="Evaluate process state, policy, data quality and risk.",
        required_inputs=["case_context", "process_context"],
        allowed_next_stages=["proposal", "closure"],
    ),
    StageDefinition(
        stage_key="proposal",
        title="Proposal",
        purpose="Produce a structured recommendation or decision proposal.",
        required_inputs=["analysis_result"],
        allowed_next_stages=["approval", "execution", "closure"],
    ),
    StageDefinition(
        stage_key="approval",
        title="Approval",
        purpose="Resolve explicit human or policy gates before execution.",
        required_inputs=["proposal_result", "gate_context"],
        allowed_next_stages=["execution", "closure"],
    ),
    StageDefinition(
        stage_key="execution",
        title="Execution",
        purpose="Execute contracted commands or services with controlled side effects.",
        allows_side_effects=True,
        required_inputs=["approved_action"],
        allowed_next_stages=["verification", "closure"],
    ),
    StageDefinition(
        stage_key="verification",
        title="Verification",
        purpose="Verify outcome, policy compliance, DQ integrity and event completeness.",
        required_inputs=["execution_result"],
        allowed_next_stages=["closure", "improvement"],
    ),
    StageDefinition(
        stage_key="closure",
        title="Closure",
        purpose="Persist final status, handover and audit state for the case.",
        required_inputs=["final_state"],
        allowed_next_stages=[],
    ),
    StageDefinition(
        stage_key="improvement",
        title="Improvement",
        purpose="Capture structured follow-up improvements outside the productive case path.",
        required_inputs=["verification_result"],
        allowed_next_stages=["closure"],
    ),
)


_ROLE_CONTRACTS: tuple[RoleContract, ...] = (
    RoleContract(
        role_key="procurement_assistant",
        purpose="Prepare and execute controlled procurement decisions.",
        scope_domains=["einkauf", "disposition"],
        process_definitions=["contract_to_intake"],
        owned_process_scopes=["purchase_order"],
        allowed_actions=["analyze", "propose", "prepare_command", "execute_contracted_write"],
        forbidden_actions=["bypass_human_approval", "invent_fallback_ids", "perform_uncontracted_http_calls"],
        required_inputs=["process_context", "policy_context", "command_catalog", "inventory_read_models"],
        allowed_commands=["CreatePurchaseOrder"],
        required_gates=["approval_gate", "role_gate", "process_gate"],
        explainability_requirements=["decision_reason", "evidence_refs", "approval_trace"],
        handover_requirements=["audit_entry", "workflow_status", "command_result"],
    ),
    RoleContract(
        role_key="finance_action_assistant",
        purpose="Prepare finance actions and explain trade-offs before execution.",
        scope_domains=["finance"],
        process_definitions=["settlement_to_finance"],
        owned_process_scopes=["payment_planning", "cash_discount"],
        allowed_actions=["analyze", "propose", "simulate"],
        forbidden_actions=["post_without_command", "bypass_approval"],
        required_inputs=["finance_read_models", "policy_context", "liquidity_context"],
        allowed_commands=[],
        required_gates=["policy_gate", "approval_gate"],
        explainability_requirements=["decision_reason", "risk_summary"],
        handover_requirements=["recommendation_result"],
    ),
    RoleContract(
        role_key="compliance_review_assistant",
        purpose="Review regulatory and rule-based cases with explainable findings.",
        scope_domains=["compliance", "quality"],
        process_definitions=["intake_to_quality", "quality_to_settlement"],
        owned_process_scopes=["compliance_review", "quality_gate"],
        allowed_actions=["analyze", "classify", "recommend"],
        forbidden_actions=["approve_instead_of_human", "write_without_contract"],
        required_inputs=["rule_context", "entity_snapshot"],
        required_gates=["policy_gate"],
        explainability_requirements=["violations", "evidence_refs", "recommendations"],
        handover_requirements=["review_result"],
    ),
    RoleContract(
        role_key="data_quality_assistant",
        purpose="Diagnose and explain data quality failures at their root cause.",
        scope_domains=["data_quality", "integration"],
        owned_process_scopes=["dq_validation", "import_exception"],
        allowed_actions=["analyze", "classify", "recommend"],
        forbidden_actions=["silently_skip_invalid_data"],
        required_inputs=["dq_findings", "payload_snapshot", "ingestion_context"],
        required_gates=["dq_gate", "approval_gate"],
        explainability_requirements=["dq_rule_hits", "root_cause_summary"],
        handover_requirements=["dq_resolution_proposal"],
    ),
    RoleContract(
        role_key="operations_exception_assistant",
        purpose="Handle operational exceptions across intake, quality and settlement flows.",
        scope_domains=["operations", "agrar"],
        process_definitions=["contract_to_intake", "intake_to_quality", "quality_to_settlement"],
        owned_process_scopes=["exception_case"],
        allowed_actions=["analyze", "propose", "escalate"],
        forbidden_actions=["force_state_transitions"],
        required_inputs=["process_context", "exception_context"],
        required_gates=["process_gate", "approval_gate"],
        explainability_requirements=["exception_summary", "evidence_refs"],
        handover_requirements=["exception_handover"],
    ),
    RoleContract(
        role_key="platform_improvement_assistant",
        purpose="Support internal improvement runbooks without entering productive write paths.",
        scope_domains=["platform", "architecture"],
        owned_process_scopes=["improvement_runbook"],
        allowed_actions=["analyze", "plan", "propose_refactor", "verify"],
        forbidden_actions=["modify_productive_state_without_review"],
        required_inputs=["architecture_context", "test_results"],
        required_gates=["role_gate"],
        explainability_requirements=["change_rationale"],
        handover_requirements=["implementation_plan", "verification_summary"],
    ),
)


_WORKFLOW_SCHEMAS: tuple[WorkflowSchema, ...] = (
    WorkflowSchema(
        workflow_schema_key="decision_workflow",
        title="Decision Workflow",
        orchestration_pattern="decision_workflow",
        default_stage_sequence=[
            "intake",
            "analysis",
            "proposal",
            "approval",
            "execution",
            "verification",
            "closure",
        ],
        required_gates=["approval_gate", "role_gate", "process_gate"],
        terminal_statuses=["completed", "rejected", "failed"],
    ),
    WorkflowSchema(
        workflow_schema_key="review_workflow",
        title="Review Workflow",
        orchestration_pattern="review_workflow",
        default_stage_sequence=["intake", "analysis", "proposal", "closure"],
        required_gates=["policy_gate"],
        terminal_statuses=["completed", "rejected", "failed"],
    ),
    WorkflowSchema(
        workflow_schema_key="exception_workflow",
        title="Exception Workflow",
        orchestration_pattern="exception_workflow",
        default_stage_sequence=[
            "intake",
            "analysis",
            "proposal",
            "approval",
            "execution",
            "verification",
            "closure",
        ],
        required_gates=["process_gate", "approval_gate", "dq_gate"],
        terminal_statuses=["completed", "rejected", "failed"],
    ),
    WorkflowSchema(
        workflow_schema_key="ingestion_workflow",
        title="Ingestion Workflow",
        orchestration_pattern="ingestion_workflow",
        default_stage_sequence=[
            "intake",
            "analysis",
            "verification",
            "approval",
            "execution",
            "closure",
        ],
        required_gates=["dq_gate", "approval_gate"],
        terminal_statuses=["completed", "rejected", "failed"],
    ),
    WorkflowSchema(
        workflow_schema_key="improvement_runbook",
        title="Improvement Runbook",
        orchestration_pattern="improvement_runbook",
        default_stage_sequence=[
            "intake",
            "analysis",
            "proposal",
            "execution",
            "verification",
            "closure",
        ],
        required_gates=["role_gate"],
        terminal_statuses=["completed", "rejected", "failed"],
    ),
)


_PROMPT_PACKS: tuple[PromptPack, ...] = (
    PromptPack(
        prompt_pack_key="procurement_decision_prompt",
        role_key="procurement_assistant",
        mission="Prepare procurement decisions with explicit approval and command boundaries.",
        scope="Operate on procurement, disposition and purchase-order preparation only.",
        constraints=[
            "No invented fallback identifiers.",
            "No write path without contracted command boundary.",
            "No approval bypass or side-channel HTTP calls.",
        ],
        inputs=["process_context", "policy_context", "inventory_read_models", "command_catalog"],
        decision_policy=[
            "Escalate to approval when human approval is required.",
            "Reject execution when supplier or command contract is incomplete.",
            "Emit explainable recommendation before any side effect.",
        ],
        output_schema="BestellvorschlagState",
        handover_rules=["audit_entry", "workflow_status", "command_result"],
    ),
    PromptPack(
        prompt_pack_key="finance_review_prompt",
        role_key="finance_action_assistant",
        mission="Review finance actions and explain trade-offs before execution.",
        scope="Operate on finance review, liquidity context and payment planning only.",
        constraints=[
            "No posting without command contract.",
            "No hidden approval bypass.",
        ],
        inputs=["finance_read_models", "policy_context", "liquidity_context"],
        decision_policy=[
            "Block action when policy gate denies execution.",
            "Prefer explainable recommendation over implicit booking.",
        ],
        output_schema="SkontoOptimizerState",
        handover_rules=["recommendation_result", "risk_summary"],
    ),
    PromptPack(
        prompt_pack_key="compliance_review_prompt",
        role_key="compliance_review_assistant",
        mission="Review rule-based compliance cases with explainable findings.",
        scope="Operate on compliance and quality review contexts only.",
        constraints=[
            "No human decision substitution.",
            "No write path outside contracted review outputs.",
        ],
        inputs=["rule_context", "entity_snapshot"],
        decision_policy=[
            "Escalate blocked findings through policy gate.",
            "Return evidence-backed recommendations for each violation cluster.",
        ],
        output_schema="ComplianceCopilotState",
        handover_rules=["review_result", "evidence_refs"],
    ),
    PromptPack(
        prompt_pack_key="data_quality_exception_prompt",
        role_key="data_quality_assistant",
        mission="Diagnose data-quality failures at root cause and prepare a structured remediation path.",
        scope="Operate on ingestion, import and DQ validation contexts only.",
        constraints=[
            "No silent skipping of invalid data.",
            "No write continuation while blocking DQ findings remain unresolved.",
        ],
        inputs=["dq_findings", "payload_snapshot", "ingestion_context"],
        decision_policy=[
            "Block the run when blocking DQ findings are present.",
            "Escalate remediation to a data steward when manual confirmation is required.",
        ],
        output_schema="DataQualityAssistantState",
        handover_rules=["dq_resolution_proposal", "dq_rule_hits"],
    ),
    PromptPack(
        prompt_pack_key="operations_exception_prompt",
        role_key="operations_exception_assistant",
        mission="Handle operational exceptions without forcing unsafe process transitions.",
        scope="Operate on intake, quality and settlement exception contexts only.",
        constraints=[
            "No forced process continuation through blocked process gates.",
            "No hidden approval bypass for operational exceptions.",
        ],
        inputs=["process_context", "exception_context"],
        decision_policy=[
            "Escalate unresolved process exceptions through the process gate.",
            "Require human approval before any exception resolution with process impact.",
        ],
        output_schema="OperationsExceptionState",
        handover_rules=["exception_handover", "evidence_refs"],
    ),
    PromptPack(
        prompt_pack_key="platform_improvement_prompt",
        role_key="platform_improvement_assistant",
        mission="Support internal platform improvement runbooks without productive writes.",
        scope="Operate on architecture, test and operational platform context only.",
        constraints=[
            "No productive state modification.",
            "No implicit rollout recommendation without verification.",
        ],
        inputs=["architecture_context", "test_results"],
        decision_policy=[
            "Prefer refactoring and verification plans over direct execution.",
        ],
        output_schema="SystemOptimizerState",
        handover_rules=["implementation_plan", "verification_summary"],
    ),
)


_EXECUTION_PACKS: tuple[ExecutionPack, ...] = (
    ExecutionPack(
        execution_pack_key="bestellvorschlag_execution",
        capability_key="bestellvorschlag_assistant",
        read_models=["inventory.low_stock", "inventory.sales_history"],
        policy_resolvers=["approval_gate", "role_gate", "process_gate"],
        commands=["CreatePurchaseOrder"],
        services=["app.agents.workflows.bestellvorschlag"],
        audit_sinks=["neuroassist.audit.default"],
        side_effect_classes=["purchase_order_create"],
    ),
    ExecutionPack(
        execution_pack_key="finance_skonto_execution",
        capability_key="finance_skonto_assistant",
        read_models=["finance.open_invoices", "finance.cash_position"],
        policy_resolvers=["policy_gate"],
        commands=[],
        services=["app.agents.workflows.skonto_optimizer"],
        audit_sinks=["neuroassist.audit.default"],
        side_effect_classes=[],
    ),
    ExecutionPack(
        execution_pack_key="compliance_review_execution",
        capability_key="compliance_copilot",
        read_models=["compliance.rules", "compliance.entity_snapshot"],
        policy_resolvers=["policy_gate"],
        commands=[],
        services=["app.agents.workflows.compliance_copilot"],
        audit_sinks=["neuroassist.audit.default"],
        side_effect_classes=[],
    ),
    ExecutionPack(
        execution_pack_key="data_quality_assistant_execution",
        capability_key="data_quality_assistant",
        read_models=["dq.findings", "integration.payload_snapshot", "integration.ingestion_context"],
        policy_resolvers=["dq_gate", "approval_gate"],
        commands=[],
        services=["app.agents.workflows.data_quality_assistant"],
        audit_sinks=["neuroassist.audit.default"],
        side_effect_classes=[],
    ),
    ExecutionPack(
        execution_pack_key="operations_exception_execution",
        capability_key="operations_exception_assistant",
        read_models=["process.case_context", "process.exception_context"],
        policy_resolvers=["process_gate", "approval_gate"],
        commands=[],
        services=["app.agents.workflows.operations_exception_assistant"],
        audit_sinks=["neuroassist.audit.default"],
        side_effect_classes=[],
    ),
    ExecutionPack(
        execution_pack_key="platform_improvement_execution",
        capability_key="system_optimizer",
        read_models=["ops.metrics", "ops.signals"],
        policy_resolvers=["role_gate"],
        commands=[],
        services=["app.agents.workflows.system_optimizer"],
        audit_sinks=["neuroassist.audit.default"],
        side_effect_classes=[],
    ),
)


_CAPABILITY_PACKS: tuple[CapabilityPack, ...] = (
    CapabilityPack(
        capability_key="bestellvorschlag_assistant",
        role_key="procurement_assistant",
        workflow_schema_key="decision_workflow",
        prompt_pack_key="procurement_decision_prompt",
        execution_pack_key="bestellvorschlag_execution",
        orchestration_pattern="decision_workflow",
        default_stage_sequence=[
            "intake",
            "analysis",
            "proposal",
            "approval",
            "execution",
            "verification",
            "closure",
        ],
        allowed_queries=["inventory.low_stock", "inventory.sales_history"],
        allowed_commands=["CreatePurchaseOrder"],
        allowed_services=["app.agents.workflows.bestellvorschlag"],
        required_gates=["approval_gate", "role_gate", "process_gate"],
        output_schema="BestellvorschlagState",
    ),
    CapabilityPack(
        capability_key="finance_skonto_assistant",
        role_key="finance_action_assistant",
        workflow_schema_key="review_workflow",
        prompt_pack_key="finance_review_prompt",
        execution_pack_key="finance_skonto_execution",
        orchestration_pattern="review_workflow",
        default_stage_sequence=["intake", "analysis", "proposal", "closure"],
        allowed_queries=["finance.open_invoices", "finance.cash_position"],
        allowed_services=["app.agents.workflows.skonto_optimizer"],
        required_gates=["policy_gate"],
        output_schema="SkontoOptimizerState",
    ),
    CapabilityPack(
        capability_key="compliance_copilot",
        role_key="compliance_review_assistant",
        workflow_schema_key="review_workflow",
        prompt_pack_key="compliance_review_prompt",
        execution_pack_key="compliance_review_execution",
        orchestration_pattern="review_workflow",
        default_stage_sequence=["intake", "analysis", "proposal", "closure"],
        allowed_queries=["compliance.rules", "compliance.entity_snapshot"],
        allowed_services=["app.agents.workflows.compliance_copilot"],
        required_gates=["policy_gate"],
        output_schema="ComplianceCopilotState",
    ),
    CapabilityPack(
        capability_key="data_quality_assistant",
        role_key="data_quality_assistant",
        workflow_schema_key="ingestion_workflow",
        prompt_pack_key="data_quality_exception_prompt",
        execution_pack_key="data_quality_assistant_execution",
        orchestration_pattern="ingestion_workflow",
        default_stage_sequence=[
            "intake",
            "analysis",
            "verification",
            "approval",
            "execution",
            "closure",
        ],
        allowed_queries=["dq.findings", "integration.payload_snapshot", "integration.ingestion_context"],
        allowed_services=["app.agents.workflows.data_quality_assistant"],
        required_gates=["dq_gate", "approval_gate"],
        output_schema="DataQualityAssistantState",
    ),
    CapabilityPack(
        capability_key="operations_exception_assistant",
        role_key="operations_exception_assistant",
        workflow_schema_key="exception_workflow",
        prompt_pack_key="operations_exception_prompt",
        execution_pack_key="operations_exception_execution",
        orchestration_pattern="exception_workflow",
        default_stage_sequence=[
            "intake",
            "analysis",
            "proposal",
            "approval",
            "execution",
            "verification",
            "closure",
        ],
        allowed_queries=["process.case_context", "process.exception_context"],
        allowed_services=["app.agents.workflows.operations_exception_assistant"],
        required_gates=["process_gate", "approval_gate"],
        output_schema="OperationsExceptionState",
    ),
    CapabilityPack(
        capability_key="system_optimizer",
        role_key="platform_improvement_assistant",
        workflow_schema_key="improvement_runbook",
        prompt_pack_key="platform_improvement_prompt",
        execution_pack_key="platform_improvement_execution",
        orchestration_pattern="improvement_runbook",
        default_stage_sequence=[
            "intake",
            "analysis",
            "proposal",
            "execution",
            "verification",
            "closure",
        ],
        allowed_queries=["ops.metrics", "ops.signals"],
        allowed_services=["app.agents.workflows.system_optimizer"],
        required_gates=["role_gate"],
        output_schema="SystemOptimizerState",
    ),
)


def get_stage_definitions() -> tuple[StageDefinition, ...]:
    return _STAGE_DEFINITIONS


def get_role_contracts() -> tuple[RoleContract, ...]:
    return _ROLE_CONTRACTS


def get_capability_packs() -> tuple[CapabilityPack, ...]:
    return _CAPABILITY_PACKS


def get_workflow_schemas() -> tuple[WorkflowSchema, ...]:
    return _WORKFLOW_SCHEMAS


def get_prompt_packs() -> tuple[PromptPack, ...]:
    return _PROMPT_PACKS


def get_execution_packs() -> tuple[ExecutionPack, ...]:
    return _EXECUTION_PACKS


def resolve_role_contract(role_key: str) -> RoleContract:
    for contract in _ROLE_CONTRACTS:
        if contract.role_key == role_key:
            return contract
    raise KeyError(f"Unknown NeuroASSIST role contract: {role_key}")


def resolve_capability_pack(capability_key: str) -> CapabilityPack:
    for pack in _CAPABILITY_PACKS:
        if pack.capability_key == capability_key:
            return pack
    raise KeyError(f"Unknown NeuroASSIST capability pack: {capability_key}")


def resolve_workflow_schema(workflow_schema_key: str) -> WorkflowSchema:
    for schema in _WORKFLOW_SCHEMAS:
        if schema.workflow_schema_key == workflow_schema_key:
            return schema
    raise KeyError(f"Unknown NeuroASSIST workflow schema: {workflow_schema_key}")


def resolve_prompt_pack(prompt_pack_key: str) -> PromptPack:
    for pack in _PROMPT_PACKS:
        if pack.prompt_pack_key == prompt_pack_key:
            return pack
    raise KeyError(f"Unknown NeuroASSIST prompt pack: {prompt_pack_key}")


def resolve_execution_pack(execution_pack_key: str) -> ExecutionPack:
    for pack in _EXECUTION_PACKS:
        if pack.execution_pack_key == execution_pack_key:
            return pack
    raise KeyError(f"Unknown NeuroASSIST execution pack: {execution_pack_key}")


def build_case_run(
    *,
    run_id: str,
    capability_key: str,
    workflow_schema_key: str,
    tenant_id: str,
    status: CaseRunStatus,
    current_stage_key: NeuroAssistStageKey,
    gate_decisions: list[GateDecision] | None = None,
    stage_transition_log: list[CaseStageTransition] | None = None,
    result_refs: list[str] | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
) -> CaseRun:
    return CaseRun(
        run_id=run_id,
        capability_key=capability_key,
        workflow_schema_key=workflow_schema_key,
        tenant_id=tenant_id,
        status=status,
        current_stage_key=current_stage_key,
        started_at=started_at or datetime.utcnow().isoformat(),
        completed_at=completed_at,
        stage_transition_log=stage_transition_log or [],
        gate_decisions=gate_decisions or [],
        result_refs=result_refs or [],
    )


def validate_neuroassist_contracts() -> list[str]:
    errors: list[str] = []
    stage_index = {stage.stage_key: stage for stage in _STAGE_DEFINITIONS}
    role_index = {role.role_key: role for role in _ROLE_CONTRACTS}
    workflow_schema_index = {
        schema.workflow_schema_key: schema for schema in _WORKFLOW_SCHEMAS
    }
    prompt_pack_index = {pack.prompt_pack_key: pack for pack in _PROMPT_PACKS}
    execution_pack_index = {pack.execution_pack_key: pack for pack in _EXECUTION_PACKS}
    known_commands = {definition.command_name for definition in build_core_command_catalog()}

    if len(stage_index) != len(_STAGE_DEFINITIONS):
        errors.append("Duplicate NeuroASSIST stage_key detected")
    if len(role_index) != len(_ROLE_CONTRACTS):
        errors.append("Duplicate NeuroASSIST role_key detected")
    if len(workflow_schema_index) != len(_WORKFLOW_SCHEMAS):
        errors.append("Duplicate NeuroASSIST workflow_schema_key detected")
    if len(prompt_pack_index) != len(_PROMPT_PACKS):
        errors.append("Duplicate NeuroASSIST prompt_pack_key detected")
    if len(execution_pack_index) != len(_EXECUTION_PACKS):
        errors.append("Duplicate NeuroASSIST execution_pack_key detected")

    for stage in _STAGE_DEFINITIONS:
        for next_stage in stage.allowed_next_stages:
            if next_stage not in stage_index:
                errors.append(
                    f"Stage '{stage.stage_key}' references unknown next stage '{next_stage}'"
                )

    for role in _ROLE_CONTRACTS:
        for command_name in role.allowed_commands:
            if command_name not in known_commands:
                errors.append(
                    f"Role '{role.role_key}' references unknown command '{command_name}'"
                )

    for prompt_pack in _PROMPT_PACKS:
        if prompt_pack.role_key not in role_index:
            errors.append(
                f"Prompt pack '{prompt_pack.prompt_pack_key}' references unknown role '{prompt_pack.role_key}'"
            )

    seen_execution_capabilities: set[str] = set()
    for execution_pack in _EXECUTION_PACKS:
        if execution_pack.capability_key in seen_execution_capabilities:
            errors.append(
                f"Duplicate NeuroASSIST execution pack for capability '{execution_pack.capability_key}'"
            )
        seen_execution_capabilities.add(execution_pack.capability_key)
        for command_name in execution_pack.commands:
            if command_name not in known_commands:
                errors.append(
                    f"Execution pack '{execution_pack.execution_pack_key}' references unknown command "
                    f"'{command_name}'"
                )

    for schema in _WORKFLOW_SCHEMAS:
        for stage_key in schema.default_stage_sequence:
            if stage_key not in stage_index:
                errors.append(
                    f"Workflow schema '{schema.workflow_schema_key}' references unknown stage '{stage_key}'"
                )
        for gate_type in schema.required_gates:
            if gate_type not in {
                "approval_gate",
                "policy_gate",
                "dq_gate",
                "role_gate",
                "process_gate",
            }:
                errors.append(
                    f"Workflow schema '{schema.workflow_schema_key}' references unknown gate '{gate_type}'"
                )

    seen_capability_keys: set[str] = set()
    for pack in _CAPABILITY_PACKS:
        if pack.capability_key in seen_capability_keys:
            errors.append(f"Duplicate capability pack '{pack.capability_key}'")
        seen_capability_keys.add(pack.capability_key)
        if pack.role_key not in role_index:
            errors.append(
                f"Capability '{pack.capability_key}' references unknown role '{pack.role_key}'"
            )
        if pack.workflow_schema_key not in workflow_schema_index:
            errors.append(
                f"Capability '{pack.capability_key}' references unknown workflow schema "
                f"'{pack.workflow_schema_key}'"
            )
        if pack.prompt_pack_key not in prompt_pack_index:
            errors.append(
                f"Capability '{pack.capability_key}' references unknown prompt pack "
                f"'{pack.prompt_pack_key}'"
            )
        if pack.execution_pack_key not in execution_pack_index:
            errors.append(
                f"Capability '{pack.capability_key}' references unknown execution pack "
                f"'{pack.execution_pack_key}'"
            )
        for stage_key in pack.default_stage_sequence:
            if stage_key not in stage_index:
                errors.append(
                    f"Capability '{pack.capability_key}' references unknown stage '{stage_key}'"
                )
        for command_name in pack.allowed_commands:
            if command_name not in known_commands:
                errors.append(
                    f"Capability '{pack.capability_key}' references unknown command '{command_name}'"
                )
        workflow_schema = workflow_schema_index.get(pack.workflow_schema_key)
        if workflow_schema is not None:
            if pack.orchestration_pattern != workflow_schema.orchestration_pattern:
                errors.append(
                    f"Capability '{pack.capability_key}' orchestration pattern "
                    f"'{pack.orchestration_pattern}' does not match workflow schema "
                    f"'{pack.workflow_schema_key}'"
                )
            if pack.default_stage_sequence != workflow_schema.default_stage_sequence:
                errors.append(
                    f"Capability '{pack.capability_key}' stage sequence does not match workflow schema "
                    f"'{pack.workflow_schema_key}'"
                )
            missing_schema_gates = set(pack.required_gates) - set(workflow_schema.required_gates)
            if missing_schema_gates:
                errors.append(
                    f"Capability '{pack.capability_key}' requires gates not covered by workflow schema "
                    f"'{pack.workflow_schema_key}': {sorted(missing_schema_gates)}"
                )
        prompt_pack = prompt_pack_index.get(pack.prompt_pack_key)
        if prompt_pack is not None and prompt_pack.role_key != pack.role_key:
            errors.append(
                f"Capability '{pack.capability_key}' prompt pack role '{prompt_pack.role_key}' "
                f"does not match role '{pack.role_key}'"
            )
        execution_pack = execution_pack_index.get(pack.execution_pack_key)
        if execution_pack is not None:
            if execution_pack.capability_key != pack.capability_key:
                errors.append(
                    f"Capability '{pack.capability_key}' execution pack points to "
                    f"'{execution_pack.capability_key}'"
                )
            missing_execution_commands = set(pack.allowed_commands) - set(execution_pack.commands)
            if missing_execution_commands:
                errors.append(
                    f"Capability '{pack.capability_key}' exposes commands not covered by execution pack "
                    f"'{pack.execution_pack_key}': {sorted(missing_execution_commands)}"
                )
            missing_execution_services = set(pack.allowed_services) - set(execution_pack.services)
            if missing_execution_services:
                errors.append(
                    f"Capability '{pack.capability_key}' exposes services not covered by execution pack "
                    f"'{pack.execution_pack_key}': {sorted(missing_execution_services)}"
                )
        role = role_index.get(pack.role_key)
        if role is not None:
            missing_gates = set(pack.required_gates) - set(role.required_gates)
            if missing_gates:
                errors.append(
                    f"Capability '{pack.capability_key}' requires gates not covered by role "
                    f"'{pack.role_key}': {sorted(missing_gates)}"
                )
            missing_commands = set(pack.allowed_commands) - set(role.allowed_commands)
            if missing_commands:
                errors.append(
                    f"Capability '{pack.capability_key}' exposes commands not allowed by role "
                    f"'{pack.role_key}': {sorted(missing_commands)}"
                )

    return errors
