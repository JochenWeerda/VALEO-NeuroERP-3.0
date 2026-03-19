from __future__ import annotations

from app.agents import resolve_neuroassist_capability, resolve_neuroassist_context


def test_neuroassist_context_resolver_marks_finance_run_as_resolved_with_primary_process_bridge():
    capability = resolve_neuroassist_capability("finance_skonto_assistant")

    resolution = resolve_neuroassist_context(
        capability,
        tenant_id="tenant-1",
        reference_context={"allow_primary_process_bridge": True, "aggregate_id": "AP-1"},
    )

    assert resolution.status == "resolved"
    assert resolution.process_definition_key == "settlement_to_finance"
    assert resolution.aggregate_type == "ap_invoice"
    assert resolution.workflow_ref is not None
    assert resolution.workflow_ref.workflow_key == "ap_invoice_approval"
    assert "finance.cash_position" in resolution.read_model_keys
    assert "ap-invoice-cockpit" in resolution.read_model_keys
    assert "policy_gate" in resolution.policy_resolver_keys
    assert "sla-ap-approval" in resolution.policy_ids


def test_neuroassist_context_resolver_keeps_bestellvorschlag_partial_without_kernel_aggregate():
    capability = resolve_neuroassist_capability("bestellvorschlag_assistant")

    resolution = resolve_neuroassist_context(
        capability,
        tenant_id="tenant-1",
        reference_context={},
    )

    assert resolution.status == "partially_resolved"
    assert resolution.process_definition_key == "contract_to_intake"
    assert resolution.aggregate_type is None
    assert "aggregate_type missing for full Process-Kernel mapping" in resolution.hints
    assert "CreatePurchaseOrder" in resolution.action_command_names


def test_neuroassist_context_resolver_rejects_aggregate_outside_process_sequence():
    capability = resolve_neuroassist_capability("operations_exception_assistant")

    resolution = resolve_neuroassist_context(
        capability,
        tenant_id="tenant-1",
        reference_context={
            "process_definition_key": "quality_to_settlement",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "AP-1",
        },
    )

    assert resolution.status == "unmappable"
    assert any("not part of process" in error for error in resolution.errors)


def test_neuroassist_context_resolver_collects_dq_rulesets_for_data_quality_runs():
    capability = resolve_neuroassist_capability("data_quality_assistant")

    resolution = resolve_neuroassist_context(
        capability,
        tenant_id="tenant-1",
        reference_context={
            "entity_type": "Artikel",
            "dq_entity_type": "article",
        },
    )

    assert "DQ-ARTIKEL-001" in resolution.dq_ruleset_ids
    assert "dq.findings" in resolution.read_model_keys
    assert "dq_gate" in resolution.policy_resolver_keys
