"""
Canonical Process Definitions - Wave 18 AP1

Maschinenlesbares Register fuer die verbindlichen Kernprozesspfade im
Landhandel. Die Definitionen referenzieren bestehende Aggregate, Commands
und SLA-Policies und erzeugen keine zweite fachliche Wahrheit.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.aggregate_registry import get_aggregate_definition
from app.core.business_commands import build_core_command_catalog
from app.core.process_commands import get_process_command_catalog
from app.core.process_sla import build_default_sla_policies


class CanonicalProcessDefinition(BaseModel):
    """Verbindlicher Vertrag fuer einen kanonischen Prozesspfad."""

    process_definition_key: str = Field(min_length=3)
    business_domain: str = Field(min_length=1)
    label: str = Field(min_length=3)
    description: str = Field(min_length=3)
    aggregate_sequence: list[str] = Field(default_factory=list)
    primary_aggregate_type: str = Field(min_length=1)
    process_command_ids: list[str] = Field(default_factory=list)
    action_command_names: list[str] = Field(default_factory=list)
    workflow_process_keys: list[str] = Field(default_factory=list)
    default_sla_policy_ids: list[str] = Field(default_factory=list)
    read_model_keys: list[str] = Field(default_factory=list)
    schema_version: int = 1


_CANONICAL_PROCESS_REGISTRY: list[CanonicalProcessDefinition] = [
    CanonicalProcessDefinition(
        process_definition_key="contract_to_intake",
        business_domain="agrar",
        label="Kontrakt zu Annahme",
        description=(
            "Vom Agrar-Kontrakt ueber Zuweisung und Registrierung bis zur "
            "finalen Ernte-Annahme."
        ),
        aggregate_sequence=["contract", "harvest_acceptance"],
        primary_aggregate_type="harvest_acceptance",
        process_command_ids=[
            "contract.allocate",
            "acceptance.register",
            "acceptance.capture",
            "acceptance.release",
        ],
        action_command_names=["FinalizeHarvestAcceptance"],
        workflow_process_keys=["annahme", "harvest_acceptance"],
        default_sla_policy_ids=["sla-harvest-acceptance"],
    ),
    CanonicalProcessDefinition(
        process_definition_key="intake_to_quality",
        business_domain="agrar",
        label="Annahme zu Qualitaet",
        description=(
            "Qualitaetspruefung als verbindlicher Folgeschritt einer "
            "Ernte-Annahme inklusive Freigabe des Protokolls."
        ),
        aggregate_sequence=["harvest_acceptance", "quality_protocol"],
        primary_aggregate_type="quality_protocol",
        process_command_ids=["quality.record", "quality.finalize"],
        action_command_names=["ReleaseQualityProtocol"],
        workflow_process_keys=["annahme", "quality_protocol"],
        default_sla_policy_ids=["sla-quality-protocol"],
    ),
    CanonicalProcessDefinition(
        process_definition_key="quality_to_settlement",
        business_domain="agrar",
        label="Qualitaet zu Settlement",
        description=(
            "Von freigegebener Qualitaet zur Agrar-Abrechnung mit Vorschau, "
            "Erstellung und verbindlicher Finalisierung."
        ),
        aggregate_sequence=["quality_protocol", "agrar_settlement"],
        primary_aggregate_type="agrar_settlement",
        process_command_ids=[
            "settlement.preview",
            "settlement.create",
            "settlement.post",
        ],
        action_command_names=[
            "CreateAgrarSettlement",
            "FinalizeAgrarSettlement",
        ],
        workflow_process_keys=["settlement"],
        default_sla_policy_ids=[],
    ),
    CanonicalProcessDefinition(
        process_definition_key="settlement_to_finance",
        business_domain="finance",
        label="Settlement zu Finance",
        description=(
            "Uebergang von der Agrar-Abrechnung in die Finanzkette mit "
            "Freigabe und Buchungsabschluss."
        ),
        aggregate_sequence=["agrar_settlement", "ap_invoice", "journal_entry"],
        primary_aggregate_type="ap_invoice",
        process_command_ids=[],
        action_command_names=[
            "ApproveAPInvoice",
            "RejectAPInvoice",
            "PostAPInvoice",
        ],
        workflow_process_keys=["ap_invoice_approval"],
        default_sla_policy_ids=["sla-ap-approval"],
        read_model_keys=["ap-invoice-cockpit"],
    ),
]

_REGISTRY_INDEX: dict[str, CanonicalProcessDefinition] = {
    definition.process_definition_key: definition
    for definition in _CANONICAL_PROCESS_REGISTRY
}


def get_canonical_process_definitions() -> list[CanonicalProcessDefinition]:
    """Gibt das vollstaendige Register der kanonischen Prozessdefinitionen zurueck."""

    return list(_CANONICAL_PROCESS_REGISTRY)


def get_canonical_process_definition(process_definition_key: str) -> CanonicalProcessDefinition:
    """Gibt eine Prozessdefinition zurueck oder wirft KeyError bei unbekanntem Schluessel."""

    if process_definition_key not in _REGISTRY_INDEX:
        raise KeyError(
            f"Prozessdefinition '{process_definition_key}' ist nicht im Register. "
            "Neue Kernprozesse muessen explizit in canonical_process_definitions.py eingetragen werden."
        )
    return _REGISTRY_INDEX[process_definition_key]


def get_canonical_processes_by_domain(domain: str) -> list[CanonicalProcessDefinition]:
    """Alle kanonischen Prozesse eines fachlichen Bereichs."""

    return [
        definition
        for definition in _CANONICAL_PROCESS_REGISTRY
        if definition.business_domain == domain
    ]


def get_canonical_processes_for_aggregate(
    aggregate_type: str,
) -> list[CanonicalProcessDefinition]:
    """Alle Prozesse, die ein bestimmtes Aggregat in ihrer Kette referenzieren."""

    return [
        definition
        for definition in _CANONICAL_PROCESS_REGISTRY
        if aggregate_type in definition.aggregate_sequence
    ]


def get_canonical_processes_by_workflow_key(
    workflow_key: str,
) -> list[CanonicalProcessDefinition]:
    """Alle Prozesse, die einen vorhandenen Workflow-Prozessschluessel nutzen."""

    return [
        definition
        for definition in _CANONICAL_PROCESS_REGISTRY
        if workflow_key in definition.workflow_process_keys
    ]


def validate_canonical_process_registry() -> list[str]:
    """
    Validiert Referenzen auf Aggregate, Commands, SLA-Policies und Read Models.

    Rueckgabe:
        Liste mit Fehlertexten. Leere Liste bedeutet konsistentes Register.
    """

    process_command_ids = {
        command.command_id for command in get_process_command_catalog()
    }
    action_command_names = {
        command.command_name for command in build_core_command_catalog()
    }
    sla_policy_ids = {
        policy.policy_id for policy in build_default_sla_policies()
    }
    errors: list[str] = []

    for definition in _CANONICAL_PROCESS_REGISTRY:
        try:
            get_aggregate_definition(definition.primary_aggregate_type)
        except KeyError as exc:
            errors.append(
                f"{definition.process_definition_key}: primary_aggregate_type invalid: {exc}"
            )

        for aggregate_type in definition.aggregate_sequence:
            try:
                get_aggregate_definition(aggregate_type)
            except KeyError as exc:
                errors.append(
                    f"{definition.process_definition_key}: aggregate_sequence invalid: {exc}"
                )

        for command_id in definition.process_command_ids:
            if command_id not in process_command_ids:
                errors.append(
                    f"{definition.process_definition_key}: process_command_id '{command_id}' unbekannt"
                )

        for command_name in definition.action_command_names:
            if command_name not in action_command_names:
                errors.append(
                    f"{definition.process_definition_key}: action_command '{command_name}' unbekannt"
                )

        for policy_id in definition.default_sla_policy_ids:
            if policy_id not in sla_policy_ids:
                errors.append(
                    f"{definition.process_definition_key}: sla_policy '{policy_id}' unbekannt"
                )

        for read_model_key in definition.read_model_keys:
            owner = get_aggregate_definition(definition.primary_aggregate_type)
            if read_model_key not in owner.read_model_keys:
                errors.append(
                    f"{definition.process_definition_key}: read_model '{read_model_key}' nicht am primaeren Aggregat verankert"
                )

    return errors
