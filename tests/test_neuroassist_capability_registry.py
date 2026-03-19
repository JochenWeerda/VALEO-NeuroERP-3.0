from __future__ import annotations

from app.agents import (
    get_neuroassist_capabilities,
    get_productive_neuroassist_capabilities,
    resolve_neuroassist_capability,
    validate_neuroassist_capabilities,
)


def test_neuroassist_registry_has_stable_business_anchor():
    capabilities = get_neuroassist_capabilities()

    assert any(cap.capability_key == "bestellvorschlag_assistant" for cap in capabilities)
    assert any(cap.kind == "business_workflow" for cap in capabilities)
    assert any(cap.kind == "operational_assistant" for cap in capabilities)


def test_neuroassist_registry_exposes_productive_and_assisted_capabilities():
    productive = get_productive_neuroassist_capabilities()

    assert {cap.capability_key for cap in productive} == {
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
        "data_quality_assistant",
        "operations_exception_assistant",
    }


def test_neuroassist_registry_resolves_capability_to_existing_workflow_module():
    capability = resolve_neuroassist_capability("compliance_copilot")

    assert capability.workflow_module == "app.agents.workflows.compliance_copilot"
    assert capability.workflow_builder == "build_compliance_workflow"
    assert capability.role_key == "compliance_review_assistant"
    assert capability.orchestration_pattern == "review_workflow"


def test_neuroassist_registry_reads_default_stage_sequence_from_neuroassist_model():
    capability = resolve_neuroassist_capability("bestellvorschlag_assistant")

    assert capability.default_stage_sequence == (
        "intake",
        "analysis",
        "proposal",
        "approval",
        "execution",
        "verification",
        "closure",
    )
    assert capability.capability_pack.capability_key == capability.capability_key
    assert capability.role_contract.role_key == capability.role_key


def test_neuroassist_registry_exposes_ingestion_and_exception_runtime_families():
    dq_capability = resolve_neuroassist_capability("data_quality_assistant")
    ops_capability = resolve_neuroassist_capability("operations_exception_assistant")

    assert dq_capability.workflow_module == "app.agents.workflows.data_quality_assistant"
    assert dq_capability.orchestration_pattern == "ingestion_workflow"
    assert dq_capability.workflow_schema_key == "ingestion_workflow"
    assert ops_capability.workflow_module == "app.agents.workflows.operations_exception_assistant"
    assert ops_capability.orchestration_pattern == "exception_workflow"
    assert ops_capability.workflow_schema_key == "exception_workflow"


def test_neuroassist_registry_validation_stays_clean():
    assert validate_neuroassist_capabilities() == []
