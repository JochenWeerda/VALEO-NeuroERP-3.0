"""NeuroASSIST capability registry for business workflows and operational assistants."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Literal

from .neuroassist_contracts import (
    CapabilityPack,
    ExecutionPack,
    PromptPack,
    RoleContract,
    WorkflowSchema,
    resolve_execution_pack,
    resolve_capability_pack,
    resolve_prompt_pack,
    resolve_role_contract,
    resolve_workflow_schema,
)

NeuroAssistCapabilityKind = Literal["business_workflow", "operational_assistant"]
NeuroAssistReadiness = Literal["productive", "assisted", "prototype"]


@dataclass(frozen=True)
class NeuroAssistCapability:
    capability_key: str
    title: str
    kind: NeuroAssistCapabilityKind
    domain: str
    role_key: str
    orchestration_pattern: str
    default_stage_sequence: tuple[str, ...]
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    readiness: NeuroAssistReadiness
    description: str
    process_scopes: tuple[str, ...]
    capability_pack: CapabilityPack
    role_contract: RoleContract
    workflow_schema_key: str
    workflow_schema: WorkflowSchema
    prompt_pack: PromptPack
    execution_pack: ExecutionPack


@dataclass(frozen=True)
class _CapabilityMetadata:
    capability_key: str
    title: str
    kind: NeuroAssistCapabilityKind
    domain: str
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    readiness: NeuroAssistReadiness
    description: str
    process_scopes: tuple[str, ...]


_NEUROASSIST_CAPABILITY_METADATA: tuple[_CapabilityMetadata, ...] = (
    _CapabilityMetadata(
        capability_key="bestellvorschlag_assistant",
        title="Bestellvorschlag Assistant",
        kind="business_workflow",
        domain="einkauf",
        workflow_module="app.agents.workflows.bestellvorschlag",
        workflow_builder="build_bestellvorschlag_workflow",
        workflow_entrypoint="run_bestellvorschlag_workflow",
        readiness="productive",
        description="Erzeugt Bestellvorschlaege mit Analyse, Approval-Checkpoint und Bestellanlage.",
        process_scopes=("disposition", "purchase_order", "human_approval"),
    ),
    _CapabilityMetadata(
        capability_key="finance_skonto_assistant",
        title="Finance Skonto Assistant",
        kind="operational_assistant",
        domain="finance",
        workflow_module="app.agents.workflows.skonto_optimizer",
        workflow_builder="build_skonto_workflow",
        workflow_entrypoint="run_skonto_optimization",
        readiness="assisted",
        description="Bereitet Skonto- und Liquiditaetsentscheidungen als Finance-Assistent vor.",
        process_scopes=("ap_invoice", "payment_planning", "cash_discount"),
    ),
    _CapabilityMetadata(
        capability_key="compliance_copilot",
        title="Compliance Copilot",
        kind="operational_assistant",
        domain="compliance",
        workflow_module="app.agents.workflows.compliance_copilot",
        workflow_builder="build_compliance_workflow",
        workflow_entrypoint="run_compliance_workflow",
        readiness="assisted",
        description="Prueft regelbasierte Compliance-Sachverhalte und erzeugt erklaerbare Handlungsempfehlungen.",
        process_scopes=("compliance_review", "quality_gate", "article_validation"),
    ),
    _CapabilityMetadata(
        capability_key="data_quality_assistant",
        title="Data Quality Assistant",
        kind="operational_assistant",
        domain="integration",
        workflow_module="app.agents.workflows.data_quality_assistant",
        workflow_builder="run_data_quality_assistant",
        workflow_entrypoint="run_data_quality_assistant",
        readiness="assisted",
        description="Analysiert DQ- und Ingestion-Faelle, blockiert unsaubere Fortsetzungen und erzeugt strukturierte Remediation-Vorschlaege.",
        process_scopes=("dq_validation", "import_exception", "ingestion_review"),
    ),
    _CapabilityMetadata(
        capability_key="operations_exception_assistant",
        title="Operations Exception Assistant",
        kind="operational_assistant",
        domain="operations",
        workflow_module="app.agents.workflows.operations_exception_assistant",
        workflow_builder="run_operations_exception_assistant",
        workflow_entrypoint="run_operations_exception_assistant",
        readiness="assisted",
        description="Bearbeitet betriebliche Ausnahmefaelle mit Prozess- und Approval-Gates statt impliziter Sonderpfade.",
        process_scopes=("exception_case", "settlement_exception", "quality_exception"),
    ),
    _CapabilityMetadata(
        capability_key="system_optimizer",
        title="System Optimizer",
        kind="operational_assistant",
        domain="operations",
        workflow_module="app.agents.workflows.system_optimizer",
        workflow_builder="build_system_optimizer_workflow",
        workflow_entrypoint="get_optimizer_agent",
        readiness="prototype",
        description="Bewertet technische Systemsignale fuer operative Optimierungsablaeufe.",
        process_scopes=("ops_monitoring", "resource_planning"),
    ),
)


def _build_capability(metadata: _CapabilityMetadata) -> NeuroAssistCapability:
    capability_pack = resolve_capability_pack(metadata.capability_key)
    role_contract = resolve_role_contract(capability_pack.role_key)
    workflow_schema = resolve_workflow_schema(capability_pack.workflow_schema_key)
    prompt_pack = resolve_prompt_pack(capability_pack.prompt_pack_key)
    execution_pack = resolve_execution_pack(capability_pack.execution_pack_key)
    return NeuroAssistCapability(
        capability_key=metadata.capability_key,
        title=metadata.title,
        kind=metadata.kind,
        domain=metadata.domain,
        role_key=capability_pack.role_key,
        orchestration_pattern=capability_pack.orchestration_pattern,
        default_stage_sequence=tuple(capability_pack.default_stage_sequence),
        workflow_module=metadata.workflow_module,
        workflow_builder=metadata.workflow_builder,
        workflow_entrypoint=metadata.workflow_entrypoint,
        readiness=metadata.readiness,
        description=metadata.description,
        process_scopes=metadata.process_scopes,
        capability_pack=capability_pack,
        role_contract=role_contract,
        workflow_schema_key=workflow_schema.workflow_schema_key,
        workflow_schema=workflow_schema,
        prompt_pack=prompt_pack,
        execution_pack=execution_pack,
    )


_NEUROASSIST_CAPABILITIES: tuple[NeuroAssistCapability, ...] = tuple(
    _build_capability(metadata) for metadata in _NEUROASSIST_CAPABILITY_METADATA
)


def get_neuroassist_capabilities() -> tuple[NeuroAssistCapability, ...]:
    return _NEUROASSIST_CAPABILITIES


def get_productive_neuroassist_capabilities() -> tuple[NeuroAssistCapability, ...]:
    return tuple(cap for cap in _NEUROASSIST_CAPABILITIES if cap.readiness in {"productive", "assisted"})


def resolve_neuroassist_capability(capability_key: str) -> NeuroAssistCapability:
    for capability in _NEUROASSIST_CAPABILITIES:
        if capability.capability_key == capability_key:
            return capability
    raise KeyError(f"Unknown NeuroASSIST capability: {capability_key}")


def validate_neuroassist_capabilities() -> list[str]:
    errors: list[str] = []
    seen_keys: set[str] = set()
    for capability in _NEUROASSIST_CAPABILITIES:
        if capability.capability_key in seen_keys:
            errors.append(f"Duplicate NeuroASSIST capability registered: {capability.capability_key}")
        seen_keys.add(capability.capability_key)
        if find_spec(capability.workflow_module) is None:
            errors.append(
                "Workflow module for NeuroASSIST capability not importable: "
                f"{capability.capability_key} -> {capability.workflow_module}"
            )
        if capability.capability_pack.capability_key != capability.capability_key:
            errors.append(
                f"Capability-pack mismatch for {capability.capability_key}: "
                f"{capability.capability_pack.capability_key}"
            )
        if capability.role_contract.role_key != capability.role_key:
            errors.append(
                f"Role-contract mismatch for {capability.capability_key}: "
                f"{capability.role_contract.role_key}"
            )
    return errors
