"""
Wave-18 Follow-up Contract Tests: Action Execution Audit Bridge

Naechster logischer Schritt nach AP1-AP6:
ActionExecution -> ProcessAuditEntry ohne API-Kopplung
"""

from __future__ import annotations

import pytest

from app.core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ActionExecutionService,
    ActionExecutionStatus,
)
from app.core.process_audit_contracts import (
    ProcessAuditEvidenceRef,
    build_action_execution_audit_entry,
    validate_process_audit_entry,
)


def test_build_action_execution_audit_entry_from_successful_result():
    service = ActionExecutionService()
    request = ActionExecutionRequest(
        command_name="ApproveAPInvoice",
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        payload={"status": "ZUR_FREIGABE"},
        tenant_id="t1",
        issuer_role="ap_approver",
        issuer_type="human",
        idempotency_key="idem-audit-1",
        process_definition_key="settlement_to_finance",
    )
    result = service.execute(request)
    entry = build_action_execution_audit_entry(request, result)
    assert entry.process_definition_key == "settlement_to_finance"
    assert entry.workflow_ref.workflow_key == "ap_invoice_approval"
    assert entry.action_name == "ApproveAPInvoice"
    assert entry.actor_type == "human"
    assert entry.actor_id == "ap_approver"
    assert validate_process_audit_entry(entry) == []


def test_build_action_execution_audit_entry_from_rejected_result_uses_error_reason():
    service = ActionExecutionService()
    request = ActionExecutionRequest(
        command_name="ApproveAPInvoice",
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        payload={"status": "ZUR_FREIGABE"},
        tenant_id="t1",
        issuer_role="ap_approver",
        issuer_type="human",
        idempotency_key="idem-audit-2",
        process_definition_key="settlement_to_finance",
        workflow_version_number=2,
    )
    result = service.execute(request)
    assert result.status == ActionExecutionStatus.REJECTED
    entry = build_action_execution_audit_entry(request, result)
    assert entry.decision_reason.code == "PROCESS_CONTRACT_INVALID"
    assert "nicht aktiv" in entry.decision_reason.summary


def test_build_action_execution_audit_entry_accepts_evidence_refs():
    service = ActionExecutionService()
    request = ActionExecutionRequest(
        command_name="ReleaseQualityProtocol",
        aggregate_type="quality_protocol",
        aggregate_id="QP-1",
        payload={"approved_by": "lab-user"},
        tenant_id="t1",
        issuer_role="quality_manager",
        issuer_type="human",
        idempotency_key="idem-audit-3",
        process_definition_key="intake_to_quality",
    )
    result = service.execute(request)
    entry = build_action_execution_audit_entry(
        request,
        result,
        evidence_refs=[
            ProcessAuditEvidenceRef(
                evidence_id="ev-qp-1",
                evidence_type="quality_lab_report",
                source_system="paperless_ngx",
                external_ref="DOC-QP-1",
                verified=True,
            )
        ],
    )
    assert entry.has_verified_evidence() is True


def test_build_action_execution_audit_entry_requires_process_definition_metadata():
    request = ActionExecutionRequest(
        command_name="ApproveAPInvoice",
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        payload={"status": "ZUR_FREIGABE"},
        tenant_id="t1",
        issuer_role="ap_approver",
        issuer_type="human",
        idempotency_key="idem-audit-4",
    )
    result = ActionExecutionResult(
        execution_id="exec-1",
        command_id="cmd-1",
        status=ActionExecutionStatus.ACCEPTED,
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        aggregate_owner="finance",
        command_name="ApproveAPInvoice",
        idempotency_key="idem-audit-4",
    )
    with pytest.raises(ValueError, match="process_definition_key"):
        build_action_execution_audit_entry(request, result)
