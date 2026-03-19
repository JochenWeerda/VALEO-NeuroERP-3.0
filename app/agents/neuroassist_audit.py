"""Generic audit and explainability sink for NeuroASSIST runs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.process_audit_contracts import (
    ProcessAuditEntry,
    ProcessAuditEvidenceRef,
    ProcessDecisionReason,
    build_process_audit_entry,
)

from .neuroassist_context import NeuroAssistContextResolution
from .neuroassist import NeuroAssistCapability
from .neuroassist_contracts import CaseRun


NeuroAssistAuditActorType = Literal["ai_agent", "human", "system"]


class NeuroAssistAuditRecord(BaseModel):
    """Persistable audit/explainability record for one NeuroASSIST case run."""

    audit_record_id: str = Field(min_length=3)
    run_id: str = Field(min_length=3)
    tenant_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=3)
    workflow_schema_key: str = Field(min_length=3)
    role_key: str = Field(min_length=3)
    process_definition_key: str | None = None
    actor_type: NeuroAssistAuditActorType = "ai_agent"
    actor_id: str = Field(min_length=3)
    current_stage_key: str = Field(min_length=3)
    status: str = Field(min_length=3)
    summary: str = Field(min_length=3)
    explainability_requirements: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    handover_requirements: list[str] = Field(default_factory=list)
    output_schema: str = Field(min_length=3)
    reference_context: dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


def build_neuroassist_audit_record(
    *,
    capability: NeuroAssistCapability,
    case_run: CaseRun,
    output_schema: str,
    actor_id: str = "neuroassist.runtime",
    actor_type: NeuroAssistAuditActorType = "ai_agent",
    summary: str | None = None,
    reference_context: dict[str, Any] | None = None,
) -> NeuroAssistAuditRecord:
    """Build a generic audit/explainability record for one NeuroASSIST run."""

    process_definition_key = None
    if capability.role_contract.process_definitions:
        process_definition_key = capability.role_contract.process_definitions[0]

    resolved_summary = summary or (
        f"NeuroASSIST run '{case_run.run_id}' for capability '{capability.capability_key}' "
        f"is in status '{case_run.status}' at stage '{case_run.current_stage_key}'."
    )

    evidence_refs = [capability.capability_key, capability.role_key, case_run.workflow_schema_key]
    evidence_refs.extend(case_run.result_refs)

    return NeuroAssistAuditRecord(
        audit_record_id=f"audit-{case_run.run_id}",
        run_id=case_run.run_id,
        tenant_id=case_run.tenant_id,
        capability_key=capability.capability_key,
        workflow_schema_key=case_run.workflow_schema_key,
        role_key=capability.role_key,
        process_definition_key=process_definition_key,
        actor_type=actor_type,
        actor_id=actor_id,
        current_stage_key=case_run.current_stage_key,
        status=case_run.status,
        summary=resolved_summary,
        explainability_requirements=list(capability.role_contract.explainability_requirements),
        evidence_refs=evidence_refs,
        handover_requirements=list(capability.role_contract.handover_requirements),
        output_schema=output_schema,
        reference_context=dict(reference_context or {}),
    )


def build_neuroassist_process_audit_entry(
    *,
    capability: NeuroAssistCapability,
    case_run: CaseRun,
    audit_record: NeuroAssistAuditRecord,
    context_resolution: NeuroAssistContextResolution,
    action_name: str | None = None,
) -> ProcessAuditEntry | None:
    """Bridge a NeuroASSIST audit record into the Process-Kernel audit contract when context is sufficient."""

    reference_context = dict(audit_record.reference_context or {})
    if context_resolution.status != "resolved":
        return None

    process_definition_key = context_resolution.process_definition_key
    aggregate_type = context_resolution.aggregate_type
    aggregate_id = context_resolution.aggregate_id
    if process_definition_key is None or aggregate_type is None or aggregate_id is None:
        return None

    evidence_refs = [
        ProcessAuditEvidenceRef(
            evidence_id=f"neuroassist-{index + 1}",
            evidence_type="neuroassist_ref",
            source_system="neuroassist",
            external_ref=evidence_ref,
            verified=False,
        )
        for index, evidence_ref in enumerate(audit_record.evidence_refs)
    ]

    return build_process_audit_entry(
        audit_entry_id=audit_record.audit_record_id,
        tenant_id=case_run.tenant_id,
        process_definition_key=process_definition_key,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        action_name=action_name or f"neuroassist.{capability.capability_key}.{case_run.current_stage_key}",
        actor_type=audit_record.actor_type,
        actor_id=audit_record.actor_id,
        decision_reason=ProcessDecisionReason(
            code=case_run.status.upper(),
            summary=audit_record.summary,
            detail=f"NeuroASSIST capability '{capability.capability_key}' reached stage '{case_run.current_stage_key}'.",
        ),
        evidence_refs=evidence_refs,
        reference_context=reference_context,
    )
