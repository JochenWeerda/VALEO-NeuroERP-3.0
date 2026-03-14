"""
Workflow Versioning - Wave 18 AP2

Versionsfaehige Workflow-Definitionen auf Basis der kanonischen
Prozessdefinitionen. Aktive Definitionen werden nicht still ueberschrieben;
neue Logik entsteht immer als neue Version mit explizitem Nachfolgerbezug.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.core.canonical_process_definitions import (
    get_canonical_process_definition,
    get_canonical_process_definitions,
)


WorkflowVersionStatus = Literal["draft", "active", "deprecated"]


class WorkflowDefinitionRef(BaseModel):
    """Stabiler Referenzanker fuer eine versionierte Workflow-Definition."""

    process_definition_key: str = Field(min_length=3)
    workflow_key: str = Field(min_length=1)
    version_number: int = Field(ge=1)
    version_tag: str = Field(min_length=2)
    tenant_id: str | None = None
    origin: str = Field(default="default", min_length=1)
    schema_version: int = 1


class WorkflowVersion(BaseModel):
    """Konkrete Version einer Workflow-Definition fuer einen Prozesspfad."""

    definition_ref: WorkflowDefinitionRef
    status: WorkflowVersionStatus = "draft"
    step_names: list[str] = Field(default_factory=list)
    aggregate_sequence: list[str] = Field(default_factory=list)
    supersedes_version_number: int | None = Field(default=None, ge=1)
    successor_version_number: int | None = Field(default=None, ge=1)
    change_summary: str = Field(min_length=1)
    activation_reason: str | None = None
    activated_at: datetime | None = None
    deprecated_at: datetime | None = None
    schema_version: int = 1


class WorkflowActivationDecision(BaseModel):
    """Ergebnis der Aktivierungspruefung fuer eine neue Workflow-Version."""

    can_activate: bool
    process_definition_key: str
    workflow_key: str
    candidate_version_number: int
    deprecated_version_number: int | None = None
    errors: list[str] = Field(default_factory=list)
    schema_version: int = 1


_WORKFLOW_VERSION_REGISTRY: list[WorkflowVersion] = [
    WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key="contract_to_intake",
            workflow_key="annahme",
            version_number=1,
            version_tag="annahme-v1",
        ),
        status="active",
        step_names=["lkw-registrierung", "warteschlange", "annahme-freigabe"],
        aggregate_sequence=["contract", "harvest_acceptance"],
        change_summary="Initiale kanonische Annahme-Version fuer Kontrakt zu Annahme.",
        activation_reason="Wave-18-Initialisierung",
        activated_at=datetime(2026, 3, 14, 0, 0, tzinfo=timezone.utc),
    ),
    WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key="intake_to_quality",
            workflow_key="annahme",
            version_number=1,
            version_tag="annahme-quality-v1",
        ),
        status="active",
        step_names=["qualitaets-check", "qualitaets-freigabe"],
        aggregate_sequence=["harvest_acceptance", "quality_protocol"],
        change_summary="Initiale kanonische Annahme-zu-Qualitaet-Version.",
        activation_reason="Wave-18-Initialisierung",
        activated_at=datetime(2026, 3, 14, 0, 0, tzinfo=timezone.utc),
    ),
    WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key="quality_to_settlement",
            workflow_key="settlement",
            version_number=1,
            version_tag="settlement-v1",
        ),
        status="active",
        step_names=["erfassung", "trocknung", "abzuege", "freigabe", "buchung"],
        aggregate_sequence=["quality_protocol", "agrar_settlement"],
        change_summary="Initiale kanonische Settlement-Version fuer Qualitaet zu Abrechnung.",
        activation_reason="Wave-18-Initialisierung",
        activated_at=datetime(2026, 3, 14, 0, 0, tzinfo=timezone.utc),
    ),
    WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key="settlement_to_finance",
            workflow_key="ap_invoice_approval",
            version_number=1,
            version_tag="ap-approval-v1",
        ),
        status="active",
        step_names=["submit", "waiting_approval", "post"],
        aggregate_sequence=["agrar_settlement", "ap_invoice", "journal_entry"],
        change_summary="Initiale kanonische Finance-Version fuer Settlement zu AP-Freigabe.",
        activation_reason="Wave-18-Initialisierung",
        activated_at=datetime(2026, 3, 14, 0, 0, tzinfo=timezone.utc),
    ),
]


def get_workflow_version_registry() -> list[WorkflowVersion]:
    """Gibt das vollstaendige Workflow-Versionsregister zurueck."""

    return list(_WORKFLOW_VERSION_REGISTRY)


def get_workflow_versions_for_process_definition(
    process_definition_key: str,
) -> list[WorkflowVersion]:
    """Alle Versionen fuer eine kanonische Prozessdefinition."""

    return [
        version
        for version in _WORKFLOW_VERSION_REGISTRY
        if version.definition_ref.process_definition_key == process_definition_key
    ]


def get_active_workflow_version(
    process_definition_key: str,
) -> WorkflowVersion | None:
    """Die aktuell aktive Workflow-Version einer Prozessdefinition."""

    versions = get_workflow_versions_for_process_definition(process_definition_key)
    for version in versions:
        if version.status == "active":
            return version
    return None


def validate_workflow_version(version: WorkflowVersion) -> list[str]:
    """Validiert eine einzelne Workflow-Version gegen Canonical-Process-Contracts."""

    errors: list[str] = []

    try:
        canonical_process = get_canonical_process_definition(
            version.definition_ref.process_definition_key
        )
    except KeyError as exc:
        return [str(exc)]

    if version.definition_ref.workflow_key not in canonical_process.workflow_process_keys:
        errors.append(
            f"{version.definition_ref.process_definition_key}: workflow_key "
            f"'{version.definition_ref.workflow_key}' ist fuer diesen Prozess nicht erlaubt"
        )

    if version.aggregate_sequence != canonical_process.aggregate_sequence:
        errors.append(
            f"{version.definition_ref.process_definition_key}: aggregate_sequence weicht "
            "vom Canonical Process ab"
        )

    if version.status == "active" and version.activated_at is None:
        errors.append(
            f"{version.definition_ref.process_definition_key}: aktive Version braucht activated_at"
        )

    if (
        version.successor_version_number is not None
        and version.successor_version_number <= version.definition_ref.version_number
    ):
        errors.append(
            f"{version.definition_ref.process_definition_key}: successor_version_number "
            "muss groesser als die aktuelle Version sein"
        )

    if (
        version.supersedes_version_number is not None
        and version.supersedes_version_number >= version.definition_ref.version_number
    ):
        errors.append(
            f"{version.definition_ref.process_definition_key}: supersedes_version_number "
            "muss kleiner als die aktuelle Version sein"
        )

    return errors


def validate_workflow_version_registry(
    registry: list[WorkflowVersion] | None = None,
) -> list[str]:
    """Validiert das gesamte Register inklusive Aktivierungsregeln."""

    versions = list(registry or _WORKFLOW_VERSION_REGISTRY)
    errors: list[str] = []
    allowed_process_keys = {
        definition.process_definition_key
        for definition in get_canonical_process_definitions()
    }

    grouped: dict[tuple[str, str], list[WorkflowVersion]] = {}
    for version in versions:
        errors.extend(validate_workflow_version(version))
        key = (
            version.definition_ref.process_definition_key,
            version.definition_ref.workflow_key,
        )
        grouped.setdefault(key, []).append(version)

    for (process_definition_key, workflow_key), items in grouped.items():
        if process_definition_key not in allowed_process_keys:
            errors.append(
                f"{process_definition_key}: unbekannte Prozessdefinition im Register"
            )

        active_versions = [item for item in items if item.status == "active"]
        if len(active_versions) > 1:
            errors.append(
                f"{process_definition_key}/{workflow_key}: mehr als eine aktive Version"
            )

        version_numbers = [item.definition_ref.version_number for item in items]
        if len(version_numbers) != len(set(version_numbers)):
            errors.append(
                f"{process_definition_key}/{workflow_key}: doppelte version_number"
            )

    return errors


def build_next_workflow_version(
    *,
    process_definition_key: str,
    workflow_key: str,
    step_names: list[str],
    change_summary: str,
    tenant_id: str | None = None,
    origin: str = "default",
) -> WorkflowVersion:
    """
    Baut die naechste Draft-Version fuer eine Prozessdefinition.

    Aktive Versionen werden dabei nicht ueberschrieben. Die Rueckgabe ist
    bewusst eine neue Draft-Version mit supersedes-Verweis.
    """

    canonical_process = get_canonical_process_definition(process_definition_key)
    if workflow_key not in canonical_process.workflow_process_keys:
        raise ValueError(
            f"workflow_key '{workflow_key}' ist fuer Prozessdefinition "
            f"'{process_definition_key}' nicht zugelassen"
        )

    existing_versions = get_workflow_versions_for_process_definition(
        process_definition_key
    )
    matching_versions = [
        version
        for version in existing_versions
        if version.definition_ref.workflow_key == workflow_key
    ]
    latest_version_number = max(
        (version.definition_ref.version_number for version in matching_versions),
        default=0,
    )
    active_version = get_active_workflow_version(process_definition_key)

    next_version_number = latest_version_number + 1
    return WorkflowVersion(
        definition_ref=WorkflowDefinitionRef(
            process_definition_key=process_definition_key,
            workflow_key=workflow_key,
            version_number=next_version_number,
            version_tag=f"{workflow_key}-v{next_version_number}",
            tenant_id=tenant_id,
            origin=origin,
        ),
        status="draft",
        step_names=step_names,
        aggregate_sequence=canonical_process.aggregate_sequence,
        supersedes_version_number=(
            active_version.definition_ref.version_number if active_version else None
        ),
        change_summary=change_summary,
    )


def plan_workflow_activation(
    candidate: WorkflowVersion,
    registry: list[WorkflowVersion] | None = None,
) -> WorkflowActivationDecision:
    """Prueft, ob eine neue Version aktiv geschaltet werden darf."""

    versions = list(registry or _WORKFLOW_VERSION_REGISTRY)
    errors = validate_workflow_version(candidate)
    matching_versions = [
        version
        for version in versions
        if version.definition_ref.process_definition_key
        == candidate.definition_ref.process_definition_key
        and version.definition_ref.workflow_key == candidate.definition_ref.workflow_key
    ]
    active_versions = [version for version in matching_versions if version.status == "active"]
    deprecated_version_number = (
        active_versions[0].definition_ref.version_number if active_versions else None
    )

    if candidate.status != "draft":
        errors.append("nur Draft-Versionen duerfen ueber plan_workflow_activation aktiviert werden")

    latest_version_number = max(
        (version.definition_ref.version_number for version in matching_versions),
        default=0,
    )
    if candidate.definition_ref.version_number <= latest_version_number:
        errors.append("neue Version muss eine hoehere version_number als bestehende Versionen haben")

    if active_versions and candidate.supersedes_version_number != deprecated_version_number:
        errors.append(
            "candidate.supersedes_version_number muss auf die aktuell aktive Version zeigen"
        )

    return WorkflowActivationDecision(
        can_activate=not errors,
        process_definition_key=candidate.definition_ref.process_definition_key,
        workflow_key=candidate.definition_ref.workflow_key,
        candidate_version_number=candidate.definition_ref.version_number,
        deprecated_version_number=deprecated_version_number,
        errors=errors,
    )


def activate_workflow_version(
    candidate: WorkflowVersion,
    registry: list[WorkflowVersion] | None = None,
) -> list[WorkflowVersion]:
    """
    Aktiviert eine neue Version und markiert die bisher aktive Version als deprecated.

    Die Funktion ist rein und liefert ein neues Register zurueck.
    """

    versions = list(registry or _WORKFLOW_VERSION_REGISTRY)
    decision = plan_workflow_activation(candidate, versions)
    if not decision.can_activate:
        raise ValueError("; ".join(decision.errors))

    activated_candidate = candidate.model_copy(
        update={
            "status": "active",
            "activated_at": datetime.now(timezone.utc),
            "activation_reason": candidate.activation_reason or "planned activation",
        }
    )

    updated_registry: list[WorkflowVersion] = []
    for version in versions:
        same_workflow = (
            version.definition_ref.process_definition_key
            == candidate.definition_ref.process_definition_key
            and version.definition_ref.workflow_key == candidate.definition_ref.workflow_key
        )
        if same_workflow and version.status == "active":
            updated_registry.append(
                version.model_copy(
                    update={
                        "status": "deprecated",
                        "successor_version_number": candidate.definition_ref.version_number,
                        "deprecated_at": datetime.now(timezone.utc),
                    }
                )
            )
            continue
        updated_registry.append(version)

    updated_registry.append(activated_candidate)
    return updated_registry
