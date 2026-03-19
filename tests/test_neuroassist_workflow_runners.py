from __future__ import annotations

from app.agents.neuroassist_workflow_runners import (
    list_workflow_runner_registrations,
    resolve_workflow_runner_for_capability,
    validate_workflow_runner_registrations,
)


def test_workflow_runner_registry_exposes_bestellvorschlag_runner():
    registrations = list_workflow_runner_registrations()

    assert [entry.capability_key for entry in registrations] == ["bestellvorschlag_assistant"]
    assert registrations[0].runner_key == "bestellvorschlag_workflow_runner"


def test_workflow_runner_registry_resolves_runner_for_capability():
    runner = resolve_workflow_runner_for_capability("bestellvorschlag_assistant")

    assert hasattr(runner, "trigger")
    assert hasattr(runner, "resume")
    assert hasattr(runner, "get_status")


def test_workflow_runner_registry_is_consistent_with_capability_registry():
    assert validate_workflow_runner_registrations() == []
