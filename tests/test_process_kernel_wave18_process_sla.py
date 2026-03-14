"""
Wave-18 Contract Tests: Process SLA Alignment

AP4: SLA-Policies und Violations tragen kanonische Prozess- und Workflow-Metadaten
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.process_sla import (
    EscalationTarget,
    ProcessSLAPolicy,
    SLASeverity,
    build_default_sla_policies,
    evaluate_sla,
)


def test_default_sla_policies_expose_wave18_process_definition_metadata():
    policies = build_default_sla_policies()
    ap_policy = next(
        policy for policy in policies if policy.policy_id == "sla-ap-approval"
    )
    harvest_policy = next(
        policy for policy in policies if policy.policy_id == "sla-harvest-acceptance"
    )
    assert ap_policy.process_definition_key == "settlement_to_finance"
    assert ap_policy.workflow_key == "ap_invoice_approval"
    assert ap_policy.workflow_version_number == 1
    assert harvest_policy.process_definition_key == "contract_to_intake"
    assert harvest_policy.workflow_key == "annahme"
    assert harvest_policy.workflow_version_number == 1


def test_evaluate_sla_carries_process_definition_and_workflow_metadata_from_policy():
    policies = build_default_sla_policies()
    violation = evaluate_sla(
        instance_id="wf-1",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=datetime.now(timezone.utc) - timedelta(hours=80),
        policies=policies,
    )
    assert violation is not None
    assert violation.severity == SLASeverity.CRITICAL
    assert violation.process_definition_key == "settlement_to_finance"
    assert violation.workflow_key == "ap_invoice_approval"
    assert violation.workflow_version_number == 1
    assert violation.escalation_target == EscalationTarget.PROCESS_OWNER


def test_evaluate_sla_accepts_explicit_wave18_metadata_filter():
    policies = build_default_sla_policies()
    violation = evaluate_sla(
        instance_id="wf-2",
        tenant_id="t1",
        process_key="harvest_acceptance",
        process_definition_key="contract_to_intake",
        workflow_key="annahme",
        workflow_version_number=1,
        step_name="pending",
        started_at=datetime.now(timezone.utc) - timedelta(hours=5),
        policies=policies,
    )
    assert violation is not None
    assert violation.severity == SLASeverity.WARNING
    assert violation.process_definition_key == "contract_to_intake"
    assert violation.workflow_key == "annahme"
    assert violation.workflow_version_number == 1


def test_evaluate_sla_returns_none_for_mismatched_workflow_version():
    policies = build_default_sla_policies()
    violation = evaluate_sla(
        instance_id="wf-3",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        process_definition_key="settlement_to_finance",
        workflow_key="ap_invoice_approval",
        workflow_version_number=2,
        step_name="waiting_approval",
        started_at=datetime.now(timezone.utc) - timedelta(hours=80),
        policies=policies,
    )
    assert violation is None


def test_process_sla_policy_schema_version_stays_stable_with_wave18_fields():
    policy = ProcessSLAPolicy(
        policy_id="sla-custom",
        process_key="custom",
        process_definition_key="quality_to_settlement",
        workflow_key="settlement",
        workflow_version_number=2,
        step_name="freigabe",
        warning_after_hours=2.0,
        critical_after_hours=4.0,
    )
    assert policy.schema_version == 1
