from __future__ import annotations

from app.agents import (
    get_genxais_capabilities,
    get_productive_genxais_capabilities,
    resolve_genxais_capability,
    validate_genxais_capabilities,
)


def test_genxais_registry_has_stable_business_anchor():
    capabilities = get_genxais_capabilities()

    assert any(cap.capability_key == "bestellvorschlag_assistant" for cap in capabilities)
    assert any(cap.kind == "business_workflow" for cap in capabilities)
    assert any(cap.kind == "operational_assistant" for cap in capabilities)


def test_genxais_registry_exposes_productive_and_assisted_capabilities():
    productive = get_productive_genxais_capabilities()

    assert {cap.capability_key for cap in productive} == {
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
    }


def test_genxais_registry_resolves_capability_to_existing_workflow_module():
    capability = resolve_genxais_capability("compliance_copilot")

    assert capability.workflow_module == "app.agents.workflows.compliance_copilot"
    assert capability.workflow_builder == "build_compliance_workflow"


def test_genxais_registry_validation_stays_clean():
    assert validate_genxais_capabilities() == []
