from __future__ import annotations

from app.agents import (
    build_case_run,
    build_neuroassist_audit_record,
    build_neuroassist_process_audit_entry,
    resolve_neuroassist_capability,
    resolve_neuroassist_context,
)


def test_neuroassist_audit_record_captures_explainability_and_handover_contracts():
    capability = resolve_neuroassist_capability("bestellvorschlag_assistant")
    case_run = build_case_run(
        run_id="run-1",
        capability_key="bestellvorschlag_assistant",
        workflow_schema_key="decision_workflow",
        tenant_id="tenant-1",
        status="pending_approval",
        current_stage_key="approval",
        result_refs=["bestellvorschlag_assistant"],
    )

    audit_record = build_neuroassist_audit_record(
        capability=capability,
        case_run=case_run,
        output_schema="BestellvorschlagState",
    )

    assert audit_record.capability_key == "bestellvorschlag_assistant"
    assert audit_record.workflow_schema_key == "decision_workflow"
    assert audit_record.process_definition_key == "contract_to_intake"
    assert "decision_reason" in audit_record.explainability_requirements
    assert "workflow_status" in audit_record.handover_requirements
    assert "bestellvorschlag_assistant" in audit_record.evidence_refs


def test_neuroassist_process_audit_bridge_maps_exception_run_to_kernel_contract():
    capability = resolve_neuroassist_capability("operations_exception_assistant")
    case_run = build_case_run(
        run_id="run-ops-1",
        capability_key="operations_exception_assistant",
        workflow_schema_key="exception_workflow",
        tenant_id="tenant-1",
        status="pending_approval",
        current_stage_key="approval",
        result_refs=["operations_exception_assistant", "quality_to_settlement"],
    )

    audit_record = build_neuroassist_audit_record(
        capability=capability,
        case_run=case_run,
        output_schema="OperationsExceptionState",
        reference_context={
            "process_definition_key": "quality_to_settlement",
            "aggregate_type": "agrar_settlement",
            "aggregate_id": "SET-1",
        },
    )
    process_audit_entry = build_neuroassist_process_audit_entry(
        capability=capability,
        case_run=case_run,
        audit_record=audit_record,
        context_resolution=resolve_neuroassist_context(
            capability,
            tenant_id="tenant-1",
            reference_context={
                "process_definition_key": "quality_to_settlement",
                "aggregate_type": "agrar_settlement",
                "aggregate_id": "SET-1",
            },
        ),
    )

    assert process_audit_entry is not None
    assert process_audit_entry.process_definition_key == "quality_to_settlement"
    assert process_audit_entry.aggregate_type == "agrar_settlement"
    assert process_audit_entry.workflow_ref.process_definition_key == "quality_to_settlement"
    assert process_audit_entry.action_name == "neuroassist.operations_exception_assistant.approval"


def test_neuroassist_process_audit_bridge_stays_conservative_without_process_context():
    capability = resolve_neuroassist_capability("bestellvorschlag_assistant")
    case_run = build_case_run(
        run_id="run-bv-1",
        capability_key="bestellvorschlag_assistant",
        workflow_schema_key="decision_workflow",
        tenant_id="tenant-1",
        status="pending_approval",
        current_stage_key="approval",
        result_refs=["bestellvorschlag_assistant"],
    )

    audit_record = build_neuroassist_audit_record(
        capability=capability,
        case_run=case_run,
        output_schema="BestellvorschlagState",
    )

    assert (
        build_neuroassist_process_audit_entry(
            capability=capability,
            case_run=case_run,
            audit_record=audit_record,
            context_resolution=resolve_neuroassist_context(
                capability,
                tenant_id="tenant-1",
                reference_context={},
            ),
        )
        is None
    )
