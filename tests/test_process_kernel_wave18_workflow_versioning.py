"""
Wave-18 Contract Tests: Workflow Versioning

AP2: WorkflowVersion und WorkflowDefinitionRef als versionsfaehiger Vertrag
"""

from __future__ import annotations

import pytest

from app.core.workflow_versioning import (
    WorkflowDefinitionRef,
    WorkflowVersion,
    activate_workflow_version,
    build_next_workflow_version,
    get_active_workflow_version,
    get_workflow_version_registry,
    get_workflow_versions_for_process_definition,
    plan_workflow_activation,
    validate_workflow_version,
    validate_workflow_version_registry,
)


def test_workflow_version_registry_is_valid():
    assert validate_workflow_version_registry() == []


def test_active_workflow_version_exists_for_each_wave18_process_definition():
    assert get_active_workflow_version("contract_to_intake") is not None
    assert get_active_workflow_version("intake_to_quality") is not None
    assert get_active_workflow_version("quality_to_settlement") is not None
    assert get_active_workflow_version("settlement_to_finance") is not None


def test_quality_to_settlement_uses_canonical_agrar_settlement_name():
    version = get_active_workflow_version("quality_to_settlement")
    assert version is not None
    assert version.definition_ref.workflow_key == "settlement"
    assert version.aggregate_sequence == ["quality_protocol", "agrar_settlement"]


def test_build_next_workflow_version_returns_new_draft_without_overwriting_active():
    draft = build_next_workflow_version(
        process_definition_key="quality_to_settlement",
        workflow_key="settlement",
        step_names=["erfassung", "freigabe", "buchung"],
        change_summary="Verdichtete Freigabe fuer Settlement.",
    )
    active = get_active_workflow_version("quality_to_settlement")
    assert active is not None
    assert draft.status == "draft"
    assert draft.definition_ref.version_number == 2
    assert draft.supersedes_version_number == 1
    assert active.definition_ref.version_number == 1
    assert active.status == "active"


def test_build_next_workflow_version_rejects_unknown_workflow_key_for_process_definition():
    with pytest.raises(ValueError, match="nicht zugelassen"):
        build_next_workflow_version(
            process_definition_key="settlement_to_finance",
            workflow_key="settlement",
            step_names=["submit"],
            change_summary="Falscher Workflow-Key.",
        )


def test_validate_workflow_version_rejects_aggregate_sequence_drift():
    invalid = WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key="contract_to_intake",
            workflow_key="annahme",
            version_number=2,
            version_tag="annahme-v2",
        ),
        status="draft",
        step_names=["foo"],
        aggregate_sequence=["contract", "shadow_acceptance"],
        supersedes_version_number=1,
        change_summary="Fehlerhafte Sequenz.",
    )
    errors = validate_workflow_version(invalid)
    assert any("aggregate_sequence weicht" in error for error in errors)


def test_plan_workflow_activation_requires_strictly_higher_version_number():
    conflicting_candidate = WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key="settlement_to_finance",
            workflow_key="ap_invoice_approval",
            version_number=1,
            version_tag="ap-approval-v1-copy",
        ),
        status="draft",
        step_names=["submit", "waiting_approval", "post"],
        aggregate_sequence=["agrar_settlement", "ap_invoice", "journal_entry"],
        supersedes_version_number=1,
        change_summary="Darf nicht Version 1 wiederverwenden.",
    )
    decision = plan_workflow_activation(conflicting_candidate)
    assert decision.can_activate is False
    assert any("hoehere version_number" in error for error in decision.errors)


def test_plan_workflow_activation_accepts_valid_successor():
    candidate = build_next_workflow_version(
        process_definition_key="settlement_to_finance",
        workflow_key="ap_invoice_approval",
        step_names=["submit", "waiting_approval", "second_approval", "post"],
        change_summary="Vier-Augen-Pfad als neue Version.",
    )
    decision = plan_workflow_activation(candidate)
    assert decision.can_activate is True
    assert decision.deprecated_version_number == 1
    assert decision.candidate_version_number == 2


def test_activate_workflow_version_deprecates_previous_active_version():
    candidate = build_next_workflow_version(
        process_definition_key="contract_to_intake",
        workflow_key="annahme",
        step_names=["lkw-registrierung", "warteschlange", "annahme-freigabe", "abschluss"],
        change_summary="Expliziter Abschluss-Schritt.",
    )
    updated_registry = activate_workflow_version(candidate)
    relevant_versions = [
        version
        for version in updated_registry
        if version.definition_ref.process_definition_key == "contract_to_intake"
    ]
    active_versions = [version for version in relevant_versions if version.status == "active"]
    deprecated_versions = [
        version for version in relevant_versions if version.status == "deprecated"
    ]
    assert len(active_versions) == 1
    assert active_versions[0].definition_ref.version_number == 2
    assert len(deprecated_versions) == 1
    assert deprecated_versions[0].successor_version_number == 2


def test_get_workflow_versions_for_process_definition_returns_only_matching_versions():
    versions = get_workflow_versions_for_process_definition("quality_to_settlement")
    assert len(versions) == 1
    assert versions[0].definition_ref.process_definition_key == "quality_to_settlement"


def test_registry_entries_use_schema_version_1():
    registry = get_workflow_version_registry()
    assert registry
    for version in registry:
        assert version.schema_version == 1
        assert version.definition_ref.schema_version == 1
