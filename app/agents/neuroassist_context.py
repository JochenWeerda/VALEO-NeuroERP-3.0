"""Central Process-Kernel context resolver for NeuroASSIST runs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.aggregate_registry import get_aggregate_definition
from app.core.canonical_process_definitions import (
    get_canonical_process_definition,
    get_canonical_processes_for_aggregate,
)
from app.core.data_quality_rules import get_default_dq_rulesets
from app.core.process_sla import build_default_sla_policies
from app.core.workflow_versioning import WorkflowDefinitionRef, get_active_workflow_version

from .neuroassist import NeuroAssistCapability


NeuroAssistContextStatus = Literal["resolved", "partially_resolved", "unmappable"]


class ConsentContext(BaseModel):
    """Consent-Status fuer den aktuellen Kanal/Zweck (DSGVO)."""
    entity_id: str | None = None
    channel: str | None = None
    has_consent: bool = True
    consent_purposes: list[str] = Field(default_factory=list)
    missing_consents: list[str] = Field(default_factory=list)


class ChannelContext(BaseModel):
    """Kanal-Kontext fuer Multi-Channel-Routing."""
    channel_type: str | None = None
    sender_id: str | None = None
    interaction_state: str | None = None
    message_count: int = 0
    last_intent: str | None = None


class NeuroAssistContextResolution(BaseModel):
    """Validated Process-Kernel context for a NeuroASSIST run."""

    capability_key: str = Field(min_length=3)
    tenant_id: str = Field(min_length=1)
    status: NeuroAssistContextStatus
    process_definition_key: str | None = None
    aggregate_type: str | None = None
    aggregate_id: str | None = None
    workflow_ref: WorkflowDefinitionRef | None = None
    policy_ids: list[str] = Field(default_factory=list)
    policy_resolver_keys: list[str] = Field(default_factory=list)
    dq_ruleset_ids: list[str] = Field(default_factory=list)
    read_model_keys: list[str] = Field(default_factory=list)
    action_command_names: list[str] = Field(default_factory=list)
    consent: ConsentContext = Field(default_factory=ConsentContext)
    channel: ChannelContext = Field(default_factory=ChannelContext)
    errors: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    schema_version: int = 2


_DQ_RULESET_NAME_ALIASES = {
    "artikel": "Artikel",
    "article": "Artikel",
    "articles": "Artikel",
    "lieferant": "Lieferant",
    "creditor": "Lieferant",
    "debitor": "Debitor",
    "debtor": "Debitor",
    "aprechnung": "APRechnung",
    "ap_invoice": "APRechnung",
    "abrechnung": "Abrechnung",
    "settlement": "Abrechnung",
    "agrar_settlement": "Abrechnung",
    "ernteannahme": "ErnteAnnahme",
    "harvest_acceptance": "ErnteAnnahme",
    "qualitaetsprotokoll": "Qualitaetsprotokoll",
    "quality_protocol": "Qualitaetsprotokoll",
    "selfbilling": "SelfBilling",
    "feldbuchmassnahme": "FeldbuchMassnahme",
    "dailypriceimport": "DailyPriceImport",
}


def _normalize_dq_entity_name(entity_name: str | None) -> str | None:
    if entity_name is None:
        return None
    normalized = (
        entity_name.strip()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
    )
    normalized = "".join(ch for ch in normalized if ch.isalnum() or ch == "_").lower()
    return _DQ_RULESET_NAME_ALIASES.get(normalized)


def _resolve_dq_ruleset_ids(
    capability: NeuroAssistCapability,
    context: dict[str, Any],
) -> list[str]:
    rulesets = get_default_dq_rulesets()
    candidates: list[str | None] = [
        context.get("dq_entity_type"),
        context.get("entity_type"),
        context.get("aggregate_type"),
    ]

    if capability.capability_key == "data_quality_assistant":
        candidates.append(context.get("entity_type"))

    resolved_ruleset_ids: list[str] = []
    for candidate in candidates:
        canonical_name = _normalize_dq_entity_name(
            str(candidate) if candidate is not None else None
        )
        if canonical_name and canonical_name in rulesets:
            resolved_ruleset_ids.append(rulesets[canonical_name].ruleset_id)

    return sorted(set(resolved_ruleset_ids))


def resolve_neuroassist_context(
    capability: NeuroAssistCapability,
    *,
    tenant_id: str,
    reference_context: dict[str, Any] | None = None,
) -> NeuroAssistContextResolution:
    context = dict(reference_context or {})
    errors: list[str] = []
    hints: list[str] = []
    read_model_keys: list[str] = []
    action_command_names: list[str] = []
    policy_ids: list[str] = []

    process_definition_key = context.get("process_definition_key")
    aggregate_type = context.get("aggregate_type")
    aggregate_id = context.get("aggregate_id")

    if process_definition_key is None and len(capability.role_contract.process_definitions) == 1:
        process_definition_key = capability.role_contract.process_definitions[0]
        hints.append(
            f"process_definition_key from role contract fallback: {process_definition_key}"
        )

    if process_definition_key is None and aggregate_type:
        candidate_processes = get_canonical_processes_for_aggregate(str(aggregate_type))
        if len(candidate_processes) == 1:
            process_definition_key = candidate_processes[0].process_definition_key
            hints.append(
                f"process_definition_key inferred from aggregate_type '{aggregate_type}'"
            )
        elif len(candidate_processes) > 1:
            errors.append(
                f"aggregate_type '{aggregate_type}' is ambiguous across multiple process definitions"
            )

    canonical_process = None
    if process_definition_key is not None:
        try:
            canonical_process = get_canonical_process_definition(str(process_definition_key))
            read_model_keys.extend(canonical_process.read_model_keys)
            action_command_names.extend(canonical_process.action_command_names)
            policy_ids.extend(canonical_process.default_sla_policy_ids)
        except KeyError as exc:
            errors.append(str(exc))

    if canonical_process is not None and aggregate_type is None and context.get("allow_primary_process_bridge") is True:
        aggregate_type = canonical_process.primary_aggregate_type
        hints.append(
            f"aggregate_type fell back to process primary aggregate '{aggregate_type}'"
        )

    if aggregate_type is not None:
        try:
            aggregate_definition = get_aggregate_definition(str(aggregate_type))
            read_model_keys.extend(aggregate_definition.read_model_keys)
        except KeyError as exc:
            errors.append(str(exc))
            aggregate_definition = None
        if canonical_process is not None and str(aggregate_type) not in canonical_process.aggregate_sequence:
            errors.append(
                f"aggregate_type '{aggregate_type}' is not part of process '{canonical_process.process_definition_key}'"
            )

    workflow_ref = None
    if canonical_process is not None:
        active_workflow_version = get_active_workflow_version(canonical_process.process_definition_key)
        if active_workflow_version is None:
            errors.append(
                f"No active workflow version for process '{canonical_process.process_definition_key}'"
            )
        else:
            workflow_ref = active_workflow_version.definition_ref
            for policy in build_default_sla_policies():
                if (
                    policy.process_definition_key == canonical_process.process_definition_key
                    and (
                        policy.workflow_key is None
                        or policy.workflow_key == workflow_ref.workflow_key
                    )
                    and (
                        policy.workflow_version_number is None
                        or policy.workflow_version_number == workflow_ref.version_number
                    )
                ):
                    policy_ids.append(policy.policy_id)

    read_model_keys.extend(capability.execution_pack.read_models)
    read_model_keys = sorted(set(read_model_keys))
    action_command_names.extend(capability.capability_pack.allowed_commands)
    action_command_names = sorted(set(action_command_names))
    policy_ids = sorted(set(policy_ids))
    dq_ruleset_ids = _resolve_dq_ruleset_ids(capability, context)

    if errors:
        status: NeuroAssistContextStatus = "unmappable"
    elif workflow_ref is not None and aggregate_type is not None and aggregate_id is not None:
        status = "resolved"
    elif workflow_ref is not None:
        status = "partially_resolved"
        if aggregate_type is None:
            hints.append("aggregate_type missing for full Process-Kernel mapping")
        if aggregate_id is None:
            hints.append("aggregate_id missing for full Process-Kernel mapping")
    else:
        status = "unmappable"

    consent_ctx = _resolve_consent_context(context, tenant_id)
    channel_ctx = _resolve_channel_context(context)

    if not consent_ctx.has_consent and consent_ctx.missing_consents:
        hints.append(f"Fehlende Consents: {', '.join(consent_ctx.missing_consents)}")

    return NeuroAssistContextResolution(
        capability_key=capability.capability_key,
        tenant_id=tenant_id,
        status=status,
        process_definition_key=(
            canonical_process.process_definition_key if canonical_process is not None else None
        ),
        aggregate_type=str(aggregate_type) if aggregate_type is not None else None,
        aggregate_id=str(aggregate_id) if aggregate_id is not None else None,
        workflow_ref=workflow_ref,
        policy_ids=policy_ids,
        policy_resolver_keys=list(capability.execution_pack.policy_resolvers),
        dq_ruleset_ids=dq_ruleset_ids,
        read_model_keys=read_model_keys,
        action_command_names=action_command_names,
        consent=consent_ctx,
        channel=channel_ctx,
        errors=errors,
        hints=hints,
    )


def _resolve_consent_context(context: dict[str, Any], tenant_id: str) -> ConsentContext:
    entity_id = context.get("entity_id") or context.get("sender_id") or context.get("from_number")
    channel = context.get("channel") or context.get("channel_type")

    if not entity_id:
        return ConsentContext()

    consent_ctx = ConsentContext(entity_id=entity_id, channel=channel)

    required_purposes = ["data_processing"]
    if channel in ("whatsapp", "email", "voice"):
        required_purposes.append(f"{channel}_communication")

    try:
        from app.services.consent_engine import check_consent
        db = context.get("_db")
        if db:
            granted = []
            missing = []
            for purpose in required_purposes:
                if check_consent(db, entity_id, purpose, tenant_id):
                    granted.append(purpose)
                else:
                    missing.append(purpose)
            consent_ctx.consent_purposes = granted
            consent_ctx.missing_consents = missing
            consent_ctx.has_consent = len(missing) == 0
        else:
            consent_ctx.has_consent = True
            consent_ctx.consent_purposes = required_purposes
    except Exception:
        consent_ctx.has_consent = True
        consent_ctx.consent_purposes = required_purposes

    return consent_ctx


def _resolve_channel_context(context: dict[str, Any]) -> ChannelContext:
    channel_type = context.get("channel") or context.get("channel_type")
    sender_id = context.get("sender_id") or context.get("from_number") or context.get("from_address")

    channel_ctx = ChannelContext(
        channel_type=channel_type,
        sender_id=sender_id,
        last_intent=context.get("last_intent"),
    )

    try:
        from app.services.interaction_state_manager import get_interaction
        interaction_id = context.get("interaction_id")
        db = context.get("_db")
        if interaction_id and db:
            interaction = get_interaction(db, interaction_id)
            if interaction:
                channel_ctx.interaction_state = interaction.get("state")
                channel_ctx.message_count = interaction.get("message_count", 0)
    except Exception:
        pass

    return channel_ctx
