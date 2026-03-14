"""
Tenant Governance Models — Wave 2 AP3-AP6

Covers:
  AP3: Tenant-/Verbundmodell (TenantStructure, VerbundMember)
  AP4: Rollen- und Berechtigungsvererbung (RoleInheritanceChain)
  AP5: Agenten- und Delegationssicherheitsmodell (AgentManifest, DelegationPolicy)
  AP6: Export- und Datenresidenzregeln (DataResidencyRule, ExportGovern)
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# AP3: Tenant-/Verbundmodell
# ---------------------------------------------------------------------------

class TenantTier(str, Enum):
    ROOT = "root"          # Verbund-Zentrale (e.g. Genossenschaft)
    BRANCH = "branch"      # Filialbetrieb / Standort
    PARTNER = "partner"    # externer Partner mit eingeschränktem Zugriff


class VerbundMember(BaseModel):
    """Ein Mitglied im Verbund (Mandant oder Betrieb)."""

    tenant_id: str
    name: str
    tier: TenantTier
    parent_tenant_id: str | None = None
    inherits_policies_from_parent: bool = True
    inherits_roles_from_parent: bool = True
    data_scope: Literal["own", "verbund", "all"] = "own"
    active: bool = True


class TenantStructure(BaseModel):
    """Vollständige Verbundstruktur mit allen Mitgliedern und Vererbungsregeln."""

    root_tenant_id: str
    members: list[VerbundMember] = Field(default_factory=list)
    schema_version: int = 1

    def get_member(self, tenant_id: str) -> VerbundMember | None:
        return next((m for m in self.members if m.tenant_id == tenant_id), None)

    def get_children(self, parent_tenant_id: str) -> list[VerbundMember]:
        return [m for m in self.members if m.parent_tenant_id == parent_tenant_id]

    def get_ancestors(self, tenant_id: str) -> list[VerbundMember]:
        """Returns the inheritance chain from tenant up to root."""
        result: list[VerbundMember] = []
        member = self.get_member(tenant_id)
        while member and member.parent_tenant_id:
            parent = self.get_member(member.parent_tenant_id)
            if parent:
                result.append(parent)
            member = parent
        return result


# ---------------------------------------------------------------------------
# AP4: Rollen- und Berechtigungsvererbung
# ---------------------------------------------------------------------------

class RoleScope(str, Enum):
    GLOBAL = "global"      # plattformweit gültig
    VERBUND = "verbund"    # gilt für ganzen Verbund
    TENANT = "tenant"      # nur für diesen Mandanten
    PROCESS = "process"    # nur für spezifischen Prozesskontext


class RoleDefinition(BaseModel):
    """Definition einer Rolle mit Herkunft und Geltungsbereich."""

    role_id: str
    label: str
    scope: RoleScope
    source_tenant_id: str | None = None   # None = global/platform
    permissions: list[str] = Field(default_factory=list)
    inheritable: bool = True              # ob diese Rolle vererbt werden darf


class RoleInheritanceChain(BaseModel):
    """Berechtigungsvererbungskette für einen Mandanten."""

    tenant_id: str
    effective_roles: list[RoleDefinition] = Field(default_factory=list)
    inherited_from: list[str] = Field(default_factory=list)  # tenant_ids
    schema_version: int = 1

    def has_permission(self, permission: str) -> bool:
        return any(permission in r.permissions for r in self.effective_roles)

    def get_roles_by_scope(self, scope: RoleScope) -> list[RoleDefinition]:
        return [r for r in self.effective_roles if r.scope == scope]


# ---------------------------------------------------------------------------
# AP5: Agenten- und Delegationssicherheitsmodell
# ---------------------------------------------------------------------------

class AgentCapabilityScope(str, Enum):
    READ = "read"                  # Daten lesen
    WRITE = "write"                # Daten schreiben
    APPROVE = "approve"            # Freigaben erteilen (eingeschränkt)
    DELEGATE = "delegate"          # Aufgaben weiterdelegieren
    EXECUTE_PAYMENT = "execute_payment"  # Zahlungen auslösen (höchste Stufe)


class AgentManifest(BaseModel):
    """Manifest eines Agenten mit zulässigen Capabilities und Grenzen."""

    agent_id: str
    agent_type: Literal["automation", "ai_assistant", "integration", "human_delegate"]
    label: str
    allowed_scopes: list[AgentCapabilityScope] = Field(default_factory=list)
    denied_scopes: list[AgentCapabilityScope] = Field(default_factory=list)
    max_delegation_depth: int = 1         # wie tief darf dieser Agent delegieren?
    requires_human_confirmation_for: list[str] = Field(default_factory=list)
    audit_all_actions: bool = True
    active: bool = True
    schema_version: int = 1


class DelegationEntry(BaseModel):
    """Einzelne Delegation von einem Principal an einen Agenten."""

    delegation_id: str
    principal_id: str                     # wer delegiert
    agent_id: str                         # an wen wird delegiert
    scope: AgentCapabilityScope
    process_context: str | None = None    # z.B. "ap_approval", "payment_run"
    tenant_id: str
    valid_from: str                       # ISO date
    valid_until: str | None = None        # None = unbegrenzt
    reason: str
    revoked: bool = False


class DelegationPolicy(BaseModel):
    """Delegationsrichtlinie für einen Mandanten."""

    tenant_id: str
    entries: list[DelegationEntry] = Field(default_factory=list)
    max_depth: int = 2                    # maximale Delegationstiefe
    require_audit_trail: bool = True
    schema_version: int = 1

    def active_delegations(self, agent_id: str) -> list[DelegationEntry]:
        return [e for e in self.entries if e.agent_id == agent_id and not e.revoked]


# ---------------------------------------------------------------------------
# AP6: Export- und Datenresidenzregeln
# ---------------------------------------------------------------------------

class DataResidencyZone(str, Enum):
    EU = "eu"              # EU-Datenraum (DSGVO)
    DE = "de"              # Deutschland (GoBD, HGB)
    CH = "ch"              # Schweiz
    AT = "at"              # Österreich
    UNRESTRICTED = "unrestricted"  # keine geografische Einschränkung


class ExportClassification(str, Enum):
    PUBLIC = "public"           # unkritisch, frei exportierbar
    INTERNAL = "internal"       # intern, eingeschränkt exportierbar
    CONFIDENTIAL = "confidential"  # vertraulich, nur mit Freigabe
    RESTRICTED = "restricted"   # gesperrt (z.B. personenbezogene Daten ohne Einwilligung)


class DataResidencyRule(BaseModel):
    """Datenresidenz- und Exportregel für einen Datentyp oder Prozesskontext."""

    rule_id: str
    label: str
    data_type: str                        # z.B. "ap_invoice", "customer_master", "harvest_weight"
    residency_zone: DataResidencyZone
    export_classification: ExportClassification
    allowed_export_targets: list[str] = Field(default_factory=list)  # Systeme/Endpunkte
    requires_approval_for_export: bool = False
    audit_on_export: bool = True
    retention_years: int | None = None    # GoBD: 10 Jahre für Buchungsbelege
    schema_version: int = 1


class ExportGovernancePolicy(BaseModel):
    """Vollständige Export-/Datenresidenzpolitik eines Mandanten."""

    tenant_id: str
    rules: list[DataResidencyRule] = Field(default_factory=list)
    default_residency_zone: DataResidencyZone = DataResidencyZone.EU
    default_export_classification: ExportClassification = ExportClassification.INTERNAL
    schema_version: int = 1

    def get_rule(self, data_type: str) -> DataResidencyRule | None:
        return next((r for r in self.rules if r.data_type == data_type), None)

    def effective_classification(self, data_type: str) -> ExportClassification:
        rule = self.get_rule(data_type)
        return rule.export_classification if rule else self.default_export_classification


# ---------------------------------------------------------------------------
# Default governance setup for a standard agricultural cooperative tenant
# ---------------------------------------------------------------------------

def build_default_governance(tenant_id: str) -> ExportGovernancePolicy:
    """Liefert Standard-Datenresidenz-Regeln für einen Landhandel-Mandanten (GoBD-konform)."""
    return ExportGovernancePolicy(
        tenant_id=tenant_id,
        rules=[
            DataResidencyRule(
                rule_id="gobd.buchungsbeleg",
                label="Buchungsbelege (GoBD §14b)",
                data_type="ap_invoice",
                residency_zone=DataResidencyZone.DE,
                export_classification=ExportClassification.CONFIDENTIAL,
                requires_approval_for_export=True,
                audit_on_export=True,
                retention_years=10,
            ),
            DataResidencyRule(
                rule_id="gobd.ernte_annahme",
                label="Ernte-Annahme und Warenbeleg",
                data_type="harvest_acceptance",
                residency_zone=DataResidencyZone.DE,
                export_classification=ExportClassification.INTERNAL,
                audit_on_export=True,
                retention_years=10,
            ),
            DataResidencyRule(
                rule_id="dsgvo.kundenstamm",
                label="Kundenstammdaten (DSGVO Art. 17)",
                data_type="customer_master",
                residency_zone=DataResidencyZone.EU,
                export_classification=ExportClassification.RESTRICTED,
                requires_approval_for_export=True,
                audit_on_export=True,
                retention_years=7,
            ),
            DataResidencyRule(
                rule_id="internal.qualitaetsprotokoll",
                label="Qualitätsprotokolle",
                data_type="quality_protocol",
                residency_zone=DataResidencyZone.DE,
                export_classification=ExportClassification.INTERNAL,
                audit_on_export=True,
                retention_years=5,
            ),
        ],
    )


def build_default_agent_manifest(agent_id: str, agent_type: str = "ai_assistant") -> AgentManifest:
    """Standard-Agenten-Manifest mit eingeschränkten Capabilities."""
    return AgentManifest(
        agent_id=agent_id,
        agent_type=agent_type,  # type: ignore[arg-type]
        label=f"Agent {agent_id}",
        allowed_scopes=[AgentCapabilityScope.READ, AgentCapabilityScope.WRITE],
        denied_scopes=[AgentCapabilityScope.EXECUTE_PAYMENT],
        max_delegation_depth=1,
        requires_human_confirmation_for=["approve", "execute_payment"],
        audit_all_actions=True,
    )
