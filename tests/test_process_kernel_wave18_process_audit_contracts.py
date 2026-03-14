"""
Wave-18 Contract Tests: Process Audit Contracts

AP3: Neutrale Audit-Typen fuer Prozessdefinition, Workflow-Version, Policy und Evidenz
"""

from __future__ import annotations

import pytest

from app.core.process_audit_contracts import (
    PolicySnapshot,
    ProcessAuditEntry,
    ProcessAuditEvidenceRef,
    ProcessDecisionReason,
    build_process_audit_entry,
    validate_process_audit_entry,
)
from app.core.workflow_versioning import WorkflowDefinitionRef


def test_build_process_audit_entry_uses_active_workflow_version_for_process_definition():
    entry = build_process_audit_entry(
        audit_entry_id="audit-1",
        tenant_id="t1",
        process_definition_key="settlement_to_finance",
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        action_name="ApproveAPInvoice",
        actor_type="human",
        actor_id="user-1",
        decision_reason=ProcessDecisionReason(
            code="APPROVED",
            summary="Freigabe innerhalb Richtlinie",
        ),
    )
    assert isinstance(entry, ProcessAuditEntry)
    assert entry.workflow_ref.process_definition_key == "settlement_to_finance"
    assert entry.workflow_ref.workflow_key == "ap_invoice_approval"
    assert entry.workflow_ref.version_number == 1


def test_build_process_audit_entry_accepts_policy_snapshot_and_evidence_refs():
    entry = build_process_audit_entry(
        audit_entry_id="audit-2",
        tenant_id="t1",
        process_definition_key="quality_to_settlement",
        aggregate_type="agrar_settlement",
        aggregate_id="SET-1",
        action_name="FinalizeAgrarSettlement",
        actor_type="ai_agent",
        actor_id="settlement_agent",
        decision_reason=ProcessDecisionReason(
            code="FINALIZED",
            summary="Abrechnung regelkonform finalisiert",
            detail="Qualitaet und Abzuege wurden bestaetigt.",
        ),
        policy_snapshot=PolicySnapshot(
            rule_id="settlement.post",
            effective_scope="tenant",
            effective_enabled=True,
            effective_params={"requires_human_confirmation": True},
            source="policy-engine",
        ),
        evidence_refs=[
            ProcessAuditEvidenceRef(
                evidence_id="ev-1",
                evidence_type="quality_lab_report",
                source_system="paperless_ngx",
                external_ref="DOC-1",
                verified=True,
            )
        ],
        reference_context={"settlement_id": "SET-1"},
    )
    assert entry.policy_snapshot is not None
    assert entry.policy_snapshot.rule_id == "settlement.post"
    assert entry.has_verified_evidence() is True
    assert entry.reference_context["settlement_id"] == "SET-1"


def test_build_process_audit_entry_rejects_aggregate_outside_process_definition():
    with pytest.raises(ValueError, match="nicht Teil der Prozessdefinition"):
        build_process_audit_entry(
            audit_entry_id="audit-3",
            tenant_id="t1",
            process_definition_key="contract_to_intake",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            action_name="ApproveAPInvoice",
            actor_type="human",
            actor_id="user-1",
            decision_reason=ProcessDecisionReason(
                code="WRONG_CHAIN",
                summary="Falsches Aggregat",
            ),
        )


def test_validate_process_audit_entry_accepts_consistent_entry():
    entry = build_process_audit_entry(
        audit_entry_id="audit-4",
        tenant_id="t1",
        process_definition_key="contract_to_intake",
        aggregate_type="harvest_acceptance",
        aggregate_id="HA-1",
        action_name="FinalizeHarvestAcceptance",
        actor_type="human",
        actor_id="acceptance-manager",
        decision_reason=ProcessDecisionReason(
            code="COMPLETED",
            summary="Annahme finalisiert",
        ),
    )
    assert validate_process_audit_entry(entry) == []


def test_validate_process_audit_entry_detects_mismatched_workflow_ref():
    entry = build_process_audit_entry(
        audit_entry_id="audit-5",
        tenant_id="t1",
        process_definition_key="settlement_to_finance",
        aggregate_type="ap_invoice",
        aggregate_id="INV-2",
        action_name="PostAPInvoice",
        actor_type="human",
        actor_id="finance-manager",
        decision_reason=ProcessDecisionReason(
            code="POSTED",
            summary="Buchung freigegeben",
        ),
    ).model_copy(
        update={
            "workflow_ref": WorkflowDefinitionRef(
                process_definition_key="quality_to_settlement",
                workflow_key="settlement",
                version_number=1,
                version_tag="settlement-v1",
            )
        }
    )
    errors = validate_process_audit_entry(entry)
    assert any("workflow_ref.process_definition_key passt nicht" in error for error in errors)


def test_validate_process_audit_entry_detects_non_active_workflow_version():
    entry = build_process_audit_entry(
        audit_entry_id="audit-6",
        tenant_id="t1",
        process_definition_key="quality_to_settlement",
        aggregate_type="agrar_settlement",
        aggregate_id="SET-2",
        action_name="CreateAgrarSettlement",
        actor_type="system",
        actor_id="scheduler",
        decision_reason=ProcessDecisionReason(
            code="CREATED",
            summary="Settlement angelegt",
        ),
    ).model_copy(
        update={
            "workflow_ref": WorkflowDefinitionRef(
                process_definition_key="quality_to_settlement",
                workflow_key="settlement",
                version_number=2,
                version_tag="settlement-v2",
            )
        }
    )
    errors = validate_process_audit_entry(entry)
    assert any("ist nicht die aktive Version" in error for error in errors)


def test_process_audit_entry_schema_version_contract():
    entry = build_process_audit_entry(
        audit_entry_id="audit-7",
        tenant_id="t1",
        process_definition_key="intake_to_quality",
        aggregate_type="quality_protocol",
        aggregate_id="QP-1",
        action_name="ReleaseQualityProtocol",
        actor_type="human",
        actor_id="lab-manager",
        decision_reason=ProcessDecisionReason(
            code="RELEASED",
            summary="Laborfreigabe erteilt",
        ),
    )
    assert entry.schema_version == 1
    assert entry.workflow_ref.schema_version == 1
    assert entry.decision_reason.schema_version == 1
