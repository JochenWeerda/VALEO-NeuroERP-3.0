"""GENXAIS capability registry for business workflows and operational assistants."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Literal


GenxaisCapabilityKind = Literal["business_workflow", "operational_assistant"]
GenxaisReadiness = Literal["productive", "assisted", "prototype"]


@dataclass(frozen=True)
class GenxaisCapability:
    capability_key: str
    title: str
    kind: GenxaisCapabilityKind
    domain: str
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    readiness: GenxaisReadiness
    description: str
    process_scopes: tuple[str, ...]


_GENXAIS_CAPABILITIES: tuple[GenxaisCapability, ...] = (
    GenxaisCapability(
        capability_key="bestellvorschlag_assistant",
        title="Bestellvorschlag Assistant",
        kind="business_workflow",
        domain="einkauf",
        workflow_module="app.agents.workflows.bestellvorschlag",
        workflow_builder="build_bestellvorschlag_workflow",
        workflow_entrypoint="run_bestellvorschlag_workflow",
        readiness="productive",
        description="Erzeugt Bestellvorschlaege mit Analyse, Approval-Checkpoint und Bestellanlage.",
        process_scopes=("disposition", "purchase_order", "human_approval"),
    ),
    GenxaisCapability(
        capability_key="finance_skonto_assistant",
        title="Finance Skonto Assistant",
        kind="operational_assistant",
        domain="finance",
        workflow_module="app.agents.workflows.skonto_optimizer",
        workflow_builder="build_skonto_workflow",
        workflow_entrypoint="run_skonto_optimization",
        readiness="assisted",
        description="Bereitet Skonto- und Liquiditaetsentscheidungen als Finance-Assistent vor.",
        process_scopes=("ap_invoice", "payment_planning", "cash_discount"),
    ),
    GenxaisCapability(
        capability_key="compliance_copilot",
        title="Compliance Copilot",
        kind="operational_assistant",
        domain="compliance",
        workflow_module="app.agents.workflows.compliance_copilot",
        workflow_builder="build_compliance_workflow",
        workflow_entrypoint="run_compliance_workflow",
        readiness="assisted",
        description="Prueft regelbasierte Compliance-Sachverhalte und erzeugt erklaerbare Handlungsempfehlungen.",
        process_scopes=("compliance_review", "quality_gate", "article_validation"),
    ),
    GenxaisCapability(
        capability_key="system_optimizer",
        title="System Optimizer",
        kind="operational_assistant",
        domain="operations",
        workflow_module="app.agents.workflows.system_optimizer",
        workflow_builder="build_system_optimizer_workflow",
        workflow_entrypoint="get_optimizer_agent",
        readiness="prototype",
        description="Bewertet technische Systemsignale fuer operative Optimierungsablaeufe.",
        process_scopes=("ops_monitoring", "resource_planning"),
    ),
)


def get_genxais_capabilities() -> tuple[GenxaisCapability, ...]:
    """Return all registered GENXAIS capabilities."""

    return _GENXAIS_CAPABILITIES


def get_productive_genxais_capabilities() -> tuple[GenxaisCapability, ...]:
    """Return capabilities that are fit to anchor the productive GENXAIS module."""

    return tuple(cap for cap in _GENXAIS_CAPABILITIES if cap.readiness in {"productive", "assisted"})


def resolve_genxais_capability(capability_key: str) -> GenxaisCapability:
    """Resolve a capability by its stable key."""

    for capability in _GENXAIS_CAPABILITIES:
        if capability.capability_key == capability_key:
            return capability
    raise KeyError(f"Unbekannte GENXAIS-Capability: {capability_key}")


def validate_genxais_capabilities() -> list[str]:
    """Validate that GENXAIS capability declarations point to importable workflow modules."""

    errors: list[str] = []
    seen_keys: set[str] = set()
    for capability in _GENXAIS_CAPABILITIES:
        if capability.capability_key in seen_keys:
            errors.append(f"Doppelte GENXAIS-Capability registriert: {capability.capability_key}")
        seen_keys.add(capability.capability_key)
        if find_spec(capability.workflow_module) is None:
            errors.append(
                f"Workflow-Modul fuer GENXAIS-Capability nicht importierbar: "
                f"{capability.capability_key} -> {capability.workflow_module}"
            )
    return errors
