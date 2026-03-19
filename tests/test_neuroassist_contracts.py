from __future__ import annotations

from app.agents import (
    build_case_run,
    get_capability_packs,
    get_execution_packs,
    get_prompt_packs,
    get_role_contracts,
    get_stage_definitions,
    get_workflow_schemas,
    resolve_capability_pack,
    resolve_execution_pack,
    resolve_prompt_pack,
    resolve_role_contract,
    resolve_workflow_schema,
    validate_neuroassist_contracts,
)


def test_neuroassist_stage_model_is_complete_and_ordered():
    stages = get_stage_definitions()

    assert [stage.stage_key for stage in stages] == [
        "intake",
        "analysis",
        "proposal",
        "approval",
        "execution",
        "verification",
        "closure",
        "improvement",
    ]
    assert next(stage for stage in stages if stage.stage_key == "execution").allows_side_effects is True


def test_neuroassist_role_contracts_include_procurement_and_finance():
    roles = get_role_contracts()

    role_keys = {role.role_key for role in roles}
    assert "procurement_assistant" in role_keys
    assert "finance_action_assistant" in role_keys

    procurement = resolve_role_contract("procurement_assistant")
    assert "CreatePurchaseOrder" in procurement.allowed_commands
    assert "approval_gate" in procurement.required_gates


def test_neuroassist_capability_pack_maps_bestellvorschlag_to_procurement_contract():
    pack = resolve_capability_pack("bestellvorschlag_assistant")

    assert pack.role_key == "procurement_assistant"
    assert pack.workflow_schema_key == "decision_workflow"
    assert pack.prompt_pack_key == "procurement_decision_prompt"
    assert pack.execution_pack_key == "bestellvorschlag_execution"
    assert pack.orchestration_pattern == "decision_workflow"
    assert pack.default_stage_sequence[-1] == "closure"
    assert pack.allowed_commands == ["CreatePurchaseOrder"]


def test_neuroassist_workflow_schema_registers_decision_and_ingestion_patterns():
    schemas = get_workflow_schemas()

    assert {schema.workflow_schema_key for schema in schemas} == {
        "decision_workflow",
        "review_workflow",
        "exception_workflow",
        "ingestion_workflow",
        "improvement_runbook",
    }

    decision_schema = resolve_workflow_schema("decision_workflow")
    assert decision_schema.default_stage_sequence == [
        "intake",
        "analysis",
        "proposal",
        "approval",
        "execution",
        "verification",
        "closure",
    ]


def test_neuroassist_case_run_contract_captures_stage_and_gate_state():
    case_run = build_case_run(
        run_id="run-1",
        capability_key="bestellvorschlag_assistant",
        workflow_schema_key="decision_workflow",
        tenant_id="tenant-1",
        status="pending_approval",
        current_stage_key="approval",
        result_refs=["bestellvorschlag_assistant"],
    )

    assert case_run.workflow_schema_key == "decision_workflow"
    assert case_run.current_stage_key == "approval"
    assert case_run.result_refs == ["bestellvorschlag_assistant"]


def test_neuroassist_prompt_and_execution_packs_bind_role_and_capability():
    prompt_packs = get_prompt_packs()
    execution_packs = get_execution_packs()

    assert len(prompt_packs) == 6
    assert len(execution_packs) == 6

    prompt_pack = resolve_prompt_pack("procurement_decision_prompt")
    execution_pack = resolve_execution_pack("bestellvorschlag_execution")
    dq_prompt_pack = resolve_prompt_pack("data_quality_exception_prompt")
    ops_execution_pack = resolve_execution_pack("operations_exception_execution")

    assert prompt_pack.role_key == "procurement_assistant"
    assert "No invented fallback identifiers." in prompt_pack.constraints
    assert execution_pack.capability_key == "bestellvorschlag_assistant"
    assert execution_pack.audit_sinks == ["neuroassist.audit.default"]
    assert execution_pack.commands == ["CreatePurchaseOrder"]
    assert dq_prompt_pack.role_key == "data_quality_assistant"
    assert "No silent skipping of invalid data." in dq_prompt_pack.constraints
    assert ops_execution_pack.capability_key == "operations_exception_assistant"
    assert "process_gate" in ops_execution_pack.policy_resolvers


def test_neuroassist_contract_validation_stays_clean():
    assert validate_neuroassist_contracts() == []


def test_neuroassist_all_capabilities_have_distinct_contracts():
    packs = get_capability_packs()

    assert {pack.capability_key for pack in packs} == {
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
        "data_quality_assistant",
        "operations_exception_assistant",
        "system_optimizer",
    }
