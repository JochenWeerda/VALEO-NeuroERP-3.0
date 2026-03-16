"""
UI Density Manifest derived from productive command, policy and approval contracts.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.ap_approval_status import APPROVAL_STATUS_TO_INSTANCE_STATUS, build_approval_status_response
from app.core.business_commands import CommandDefinition, build_core_command_catalog
from app.core.settlement_approval import SettlementActorType, SettlementApprovalStatus


class UIDensityManifestEntry(BaseModel):
    page_domain: str
    aggregate_types: list[str] = Field(default_factory=list)
    command_names: list[str] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=list)
    approval_roles: list[str] = Field(default_factory=list)
    approval_actor_types: list[str] = Field(default_factory=list)
    approval_statuses: list[str] = Field(default_factory=list)
    explainability_statuses: list[str] = Field(default_factory=list)
    policy_rule_ids: list[str] = Field(default_factory=list)
    source_contracts: list[str] = Field(default_factory=list)
    requires_human_confirmation: bool = False
    requires_explainability: bool = False
    restricted_command_count: int = 0
    recommended_density: str
    schema_version: int = 1


class UIDensityManifest(BaseModel):
    entries: list[UIDensityManifestEntry]
    schema_version: int = 1


_AGGREGATE_DOMAIN_MAP: dict[str, str] = {
    "ap_invoice": "finance-approval",
    "payment_run": "finance",
    "direct_debit_run": "finance",
    "harvest_acceptance": "agrar",
    "quality_protocol": "agrar-quality",
    "agrar_settlement": "agrar-settlement",
}


def _domain_for_command(definition: CommandDefinition) -> str:
    return _AGGREGATE_DOMAIN_MAP.get(definition.aggregate_type, definition.aggregate_type)


def _recommended_density(
    restricted_command_count: int,
    requires_human_confirmation: bool,
    requires_explainability: bool,
    has_policy_contracts: bool,
    allowed_roles: set[str],
    page_domain: str,
) -> str:
    finance_like = any(token in page_domain for token in ("finance", "approval", "fibu", "settlement"))
    if (
        requires_human_confirmation
        or requires_explainability
        or has_policy_contracts
        or restricted_command_count >= 2
        or finance_like
    ):
        return "dense"
    if len(allowed_roles) >= 2:
        return "standard"
    return "focused"


def _merge_entry(base: UIDensityManifestEntry, incoming: UIDensityManifestEntry) -> UIDensityManifestEntry:
    allowed_roles = sorted(set(base.allowed_roles) | set(incoming.allowed_roles) | set(incoming.approval_roles))

    recommended_density = _recommended_density(
        max(base.restricted_command_count, incoming.restricted_command_count),
        base.requires_human_confirmation or incoming.requires_human_confirmation,
        base.requires_explainability or incoming.requires_explainability,
        bool(base.source_contracts or incoming.source_contracts),
        set(allowed_roles),
        base.page_domain,
    )

    return UIDensityManifestEntry(
        page_domain=base.page_domain,
        aggregate_types=sorted(set(base.aggregate_types) | set(incoming.aggregate_types)),
        command_names=sorted(set(base.command_names) | set(incoming.command_names)),
        allowed_roles=allowed_roles,
        approval_roles=sorted(set(base.approval_roles) | set(incoming.approval_roles)),
        approval_actor_types=sorted(set(base.approval_actor_types) | set(incoming.approval_actor_types)),
        approval_statuses=sorted(set(base.approval_statuses) | set(incoming.approval_statuses)),
        explainability_statuses=sorted(set(base.explainability_statuses) | set(incoming.explainability_statuses)),
        policy_rule_ids=sorted(set(base.policy_rule_ids) | set(incoming.policy_rule_ids)),
        source_contracts=sorted(set(base.source_contracts) | set(incoming.source_contracts)),
        requires_human_confirmation=base.requires_human_confirmation or incoming.requires_human_confirmation,
        requires_explainability=base.requires_explainability or incoming.requires_explainability,
        restricted_command_count=max(base.restricted_command_count, incoming.restricted_command_count),
        recommended_density=recommended_density,
    )


def _build_command_entries(definitions: list[CommandDefinition]) -> list[UIDensityManifestEntry]:
    grouped: dict[str, list[CommandDefinition]] = {}

    for definition in definitions:
        page_domain = _domain_for_command(definition)
        grouped.setdefault(page_domain, []).append(definition)

    entries: list[UIDensityManifestEntry] = []
    for page_domain, commands in grouped.items():
        aggregate_types = sorted({command.aggregate_type for command in commands})
        command_names = sorted(command.command_name for command in commands)
        allowed_roles = sorted({role for command in commands for role in command.allowed_roles})
        restricted_command_count = sum(1 for command in commands if command.requires_human_confirmation)
        requires_human_confirmation = restricted_command_count > 0

        entries.append(
            UIDensityManifestEntry(
                page_domain=page_domain,
                aggregate_types=aggregate_types,
                command_names=command_names,
                allowed_roles=allowed_roles,
                requires_human_confirmation=requires_human_confirmation,
                restricted_command_count=restricted_command_count,
                recommended_density=_recommended_density(
                    restricted_command_count,
                    requires_human_confirmation,
                    False,
                    False,
                    set(allowed_roles),
                    page_domain,
                ),
            )
        )
    return entries


def _build_policy_entries() -> list[UIDensityManifestEntry]:
    ap_status = build_approval_status_response(
        invoice_id="preview-ap-invoice",
        tenant_id="tenant-density-preview",
        status="pending",
        required_approvals=2,
        approvals=[{"approved_by": "approver-a"}],
        rejections=[],
        applicable_rule={
            "id": "ap.approval.rule",
            "name": "AP Approval Rule",
            "required_approvals": 2,
            "approval_roles": ["approver", "manager"],
        },
    )

    settlement_actor_types = [
        actor_type.value.lower() for actor_type in SettlementActorType if actor_type is not SettlementActorType.SYSTEM
    ]
    settlement_statuses = [status.value for status in SettlementApprovalStatus]
    finance_approval_statuses = ["draft", "pending", "approved", "completed", "executed", "submitted"]

    return [
        UIDensityManifestEntry(
            page_domain="finance-approval",
            aggregate_types=["ap_invoice"],
            allowed_roles=sorted(set(ap_status.override_resolution.effective_params.get("approval_roles", []))),
            approval_roles=sorted(set(ap_status.override_resolution.effective_params.get("approval_roles", []))),
            approval_statuses=sorted(APPROVAL_STATUS_TO_INSTANCE_STATUS.keys()),
            explainability_statuses=[ap_status.explainability.status],
            policy_rule_ids=[ap_status.override_resolution.rule_id],
            source_contracts=["ap_approval_status", "explainability", "policy_decisions"],
            requires_human_confirmation=True,
            requires_explainability=True,
            restricted_command_count=1,
            recommended_density="dense",
        ),
        UIDensityManifestEntry(
            page_domain="finance-closing",
            aggregate_types=["closing_checklist"],
            approval_roles=["accountant", "controller"],
            approval_statuses=["draft", "in_progress", "approved", "completed", "blocked"],
            explainability_statuses=["approval-required", "allowed"],
            policy_rule_ids=["finance.closing.period"],
            source_contracts=["closing_checklists", "explainability", "policy_decisions"],
            requires_human_confirmation=True,
            requires_explainability=True,
            recommended_density="dense",
        ),
        UIDensityManifestEntry(
            page_domain="finance-vat",
            aggregate_types=["vat_return"],
            approval_roles=["accountant", "controller", "tax_advisor"],
            approval_statuses=["draft", "calculated", "validated", "approved", "submitted"],
            explainability_statuses=["approval-required", "allowed"],
            policy_rule_ids=["finance.vat_return.submission"],
            source_contracts=["vat_return_export", "explainability", "policy_decisions"],
            requires_human_confirmation=True,
            requires_explainability=True,
            recommended_density="dense",
        ),
        UIDensityManifestEntry(
            page_domain="finance-payment-run",
            aggregate_types=["payment_run"],
            approval_roles=["accountant", "controller"],
            approval_statuses=finance_approval_statuses,
            explainability_statuses=["approval-required", "allowed"],
            policy_rule_ids=["finance.payment_run.execution"],
            source_contracts=["payment_runs", "explainability", "policy_decisions"],
            requires_human_confirmation=True,
            requires_explainability=True,
            recommended_density="dense",
        ),
        UIDensityManifestEntry(
            page_domain="finance-direct-debit",
            aggregate_types=["direct_debit_run"],
            approval_roles=["accountant", "controller"],
            approval_statuses=finance_approval_statuses,
            explainability_statuses=["approval-required", "allowed"],
            policy_rule_ids=["finance.direct_debit.execution"],
            source_contracts=["direct_debits", "explainability", "policy_decisions"],
            requires_human_confirmation=True,
            requires_explainability=True,
            recommended_density="dense",
        ),
        UIDensityManifestEntry(
            page_domain="agrar-settlement",
            aggregate_types=["agrar_settlement"],
            approval_actor_types=settlement_actor_types,
            approval_statuses=settlement_statuses,
            policy_rule_ids=["settlement.approval.flow", "settlement.approval.human-gate"],
            source_contracts=["settlement_approval"],
            requires_human_confirmation=True,
            recommended_density="dense",
        ),
    ]


def build_ui_density_manifest(
    catalog: list[CommandDefinition] | None = None,
) -> UIDensityManifest:
    definitions = catalog or build_core_command_catalog()
    grouped: dict[str, UIDensityManifestEntry] = {}

    for entry in [*_build_command_entries(definitions), *_build_policy_entries()]:
        existing = grouped.get(entry.page_domain)
        grouped[entry.page_domain] = _merge_entry(existing, entry) if existing else entry

    entries = sorted(grouped.values(), key=lambda entry: entry.page_domain)
    return UIDensityManifest(entries=entries)


def get_ui_density_entry(
    page_domain: str,
    catalog: list[CommandDefinition] | None = None,
) -> UIDensityManifestEntry | None:
    manifest = build_ui_density_manifest(catalog)
    normalized = (page_domain or "").strip().lower()
    for entry in manifest.entries:
        if entry.page_domain == normalized:
            return entry
    return None
