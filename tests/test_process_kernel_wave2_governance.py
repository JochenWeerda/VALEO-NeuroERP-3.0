"""
Wave-2 Contract-Tests: AP3-AP6 Tenant Governance Models

Prueft:
  AP3: TenantStructure und Verbundmodell
  AP4: RoleInheritanceChain und Berechtigungsvererbung
  AP5: AgentManifest und DelegationPolicy
  AP6: DataResidencyRule und ExportGovernancePolicy
"""
from __future__ import annotations

from app.core.tenant_governance import (
    TenantStructure,
    TenantTier,
    VerbundMember,
    RoleInheritanceChain,
    RoleDefinition,
    RoleScope,
    AgentManifest,
    AgentCapabilityScope,
    DelegationPolicy,
    DelegationEntry,
    DataResidencyRule,
    DataResidencyZone,
    ExportClassification,
    ExportGovernancePolicy,
    build_default_governance,
    build_default_agent_manifest,
)


# ---------------------------------------------------------------------------
# AP3: Tenant-/Verbundmodell
# ---------------------------------------------------------------------------

def test_verbund_member_has_tier_and_inherits_flags():
    member = VerbundMember(
        tenant_id="branch-1",
        name="Filiale Nord",
        tier=TenantTier.BRANCH,
        parent_tenant_id="root-tenant",
        inherits_policies_from_parent=True,
        inherits_roles_from_parent=True,
    )
    assert member.tier == TenantTier.BRANCH
    assert member.inherits_policies_from_parent is True
    assert member.parent_tenant_id == "root-tenant"


def test_tenant_structure_get_member_returns_none_for_unknown():
    structure = TenantStructure(root_tenant_id="root", members=[])
    assert structure.get_member("nonexistent") is None


def test_tenant_structure_get_children():
    root = VerbundMember(tenant_id="root", name="Root", tier=TenantTier.ROOT)
    branch1 = VerbundMember(tenant_id="b1", name="B1", tier=TenantTier.BRANCH, parent_tenant_id="root")
    branch2 = VerbundMember(tenant_id="b2", name="B2", tier=TenantTier.BRANCH, parent_tenant_id="root")
    structure = TenantStructure(root_tenant_id="root", members=[root, branch1, branch2])
    children = structure.get_children("root")
    assert len(children) == 2
    assert {c.tenant_id for c in children} == {"b1", "b2"}


def test_tenant_structure_get_ancestors_returns_chain():
    root = VerbundMember(tenant_id="root", name="Root", tier=TenantTier.ROOT)
    branch = VerbundMember(tenant_id="branch", name="Branch", tier=TenantTier.BRANCH, parent_tenant_id="root")
    leaf = VerbundMember(tenant_id="leaf", name="Leaf", tier=TenantTier.PARTNER, parent_tenant_id="branch")
    structure = TenantStructure(root_tenant_id="root", members=[root, branch, leaf])
    # leaf -> branch -> root: get_ancestors("leaf") returns [branch, root]
    ancestors = structure.get_ancestors("leaf")
    assert len(ancestors) == 2
    assert ancestors[0].tenant_id == "branch"
    assert ancestors[1].tenant_id == "root"


def test_tenant_structure_schema_version():
    structure = TenantStructure(root_tenant_id="root", members=[])
    assert structure.schema_version == 1


# ---------------------------------------------------------------------------
# AP4: Rollen- und Berechtigungsvererbung
# ---------------------------------------------------------------------------

def test_role_definition_has_scope_and_permissions():
    role = RoleDefinition(
        role_id="fibu.admin",
        label="Finanzbuchhaltung Admin",
        scope=RoleScope.TENANT,
        permissions=["finance:admin", "ap_invoice:approve"],
    )
    assert role.scope == RoleScope.TENANT
    assert "finance:admin" in role.permissions


def test_role_inheritance_chain_has_permission():
    chain = RoleInheritanceChain(
        tenant_id="t1",
        effective_roles=[
            RoleDefinition(
                role_id="agrar.manager",
                label="Agrar Manager",
                scope=RoleScope.TENANT,
                permissions=["harvest:write", "quality:write"],
            )
        ],
    )
    assert chain.has_permission("harvest:write") is True
    assert chain.has_permission("payment_run:execute") is False


def test_role_inheritance_chain_get_roles_by_scope():
    chain = RoleInheritanceChain(
        tenant_id="t1",
        effective_roles=[
            RoleDefinition(role_id="r1", label="R1", scope=RoleScope.TENANT, permissions=[]),
            RoleDefinition(role_id="r2", label="R2", scope=RoleScope.GLOBAL, permissions=[]),
            RoleDefinition(role_id="r3", label="R3", scope=RoleScope.TENANT, permissions=[]),
        ],
    )
    tenant_roles = chain.get_roles_by_scope(RoleScope.TENANT)
    assert len(tenant_roles) == 2


def test_role_inheritance_chain_schema_version():
    chain = RoleInheritanceChain(tenant_id="t1")
    assert chain.schema_version == 1


# ---------------------------------------------------------------------------
# AP5: Agenten- und Delegationssicherheitsmodell
# ---------------------------------------------------------------------------

def test_agent_manifest_denied_scopes_block_execute_payment():
    manifest = build_default_agent_manifest("test-agent")
    assert AgentCapabilityScope.EXECUTE_PAYMENT in manifest.denied_scopes
    assert AgentCapabilityScope.READ in manifest.allowed_scopes


def test_agent_manifest_requires_human_confirmation_for_approve():
    manifest = build_default_agent_manifest("test-agent")
    assert "approve" in manifest.requires_human_confirmation_for


def test_agent_manifest_audit_all_actions_is_true():
    manifest = build_default_agent_manifest("test-agent")
    assert manifest.audit_all_actions is True


def test_delegation_policy_active_delegations_filters_revoked():
    entry_active = DelegationEntry(
        delegation_id="d1",
        principal_id="user1",
        agent_id="agent-a",
        scope=AgentCapabilityScope.WRITE,
        tenant_id="t1",
        valid_from="2026-01-01",
        reason="Urlaub",
        revoked=False,
    )
    entry_revoked = DelegationEntry(
        delegation_id="d2",
        principal_id="user1",
        agent_id="agent-a",
        scope=AgentCapabilityScope.READ,
        tenant_id="t1",
        valid_from="2026-01-01",
        reason="Alteintrag",
        revoked=True,
    )
    policy = DelegationPolicy(tenant_id="t1", entries=[entry_active, entry_revoked])
    active = policy.active_delegations("agent-a")
    assert len(active) == 1
    assert active[0].delegation_id == "d1"


def test_agent_manifest_schema_version():
    manifest = AgentManifest(
        agent_id="x",
        agent_type="automation",
        label="X",
        allowed_scopes=[AgentCapabilityScope.READ],
    )
    assert manifest.schema_version == 1


# ---------------------------------------------------------------------------
# AP6: Export- und Datenresidenzregeln
# ---------------------------------------------------------------------------

def test_data_residency_rule_has_retention_and_residency():
    rule = DataResidencyRule(
        rule_id="gobd.test",
        label="Test",
        data_type="ap_invoice",
        residency_zone=DataResidencyZone.DE,
        export_classification=ExportClassification.CONFIDENTIAL,
        retention_years=10,
    )
    assert rule.residency_zone == DataResidencyZone.DE
    assert rule.retention_years == 10
    assert rule.export_classification == ExportClassification.CONFIDENTIAL


def test_export_governance_policy_get_rule_returns_match():
    policy = build_default_governance("tenant1")
    rule = policy.get_rule("ap_invoice")
    assert rule is not None
    assert rule.retention_years == 10
    assert rule.requires_approval_for_export is True


def test_export_governance_policy_effective_classification_fallback():
    policy = ExportGovernancePolicy(
        tenant_id="t1",
        rules=[],
        default_export_classification=ExportClassification.INTERNAL,
    )
    cls = policy.effective_classification("unknown_data_type")
    assert cls == ExportClassification.INTERNAL


def test_export_governance_policy_gobd_customer_restricted():
    policy = build_default_governance("tenant1")
    rule = policy.get_rule("customer_master")
    assert rule is not None
    assert rule.export_classification == ExportClassification.RESTRICTED
    assert rule.requires_approval_for_export is True


def test_export_governance_policy_schema_version():
    policy = build_default_governance("tenant1")
    assert policy.schema_version == 1
