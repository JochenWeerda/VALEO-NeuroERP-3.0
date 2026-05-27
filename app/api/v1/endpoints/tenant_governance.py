"""
Tenant Governance API — Wave 2 AP3-AP6

Endpoints:
  AP3: GET /tenant/structure
  AP4: GET /tenant/role-inheritance
  AP5: GET /tenant/agent-manifests, POST /tenant/agent-manifests/{agent_id}/delegate
  AP6: GET /tenant/data-residency
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id
from ....core.tenant_governance import (
    TenantStructure,
    TenantTier,
    VerbundMember,
    RoleInheritanceChain,
    RoleDefinition,
    RoleScope,
    AgentManifest,
    AgentCapabilityScope,
    DelegationPolicy,
    ExportGovernancePolicy,
    build_default_governance,
    build_default_agent_manifest,
)
from ....core.tenant_rate_limits import get_default_cache_configs, get_default_rate_limit_policies

router = APIRouter(prefix="/tenant", tags=["tenant", "governance"])


# ---------------------------------------------------------------------------
# AP3: Tenant-/Verbundmodell
# ---------------------------------------------------------------------------

@router.get("/structure", response_model=TenantStructure, summary="Tenant structure abrufen")
async def get_tenant_structure(tenant_id: str = Depends(get_tenant_id)):
    """AP3: Liefert die Verbundstruktur für den aktuellen Mandanten."""
    # Default: single-tenant structure (no verbund)
    return TenantStructure(
        root_tenant_id=tenant_id,
        members=[
            VerbundMember(
                tenant_id=tenant_id,
                name=tenant_id,
                tier=TenantTier.ROOT,
                parent_tenant_id=None,
                inherits_policies_from_parent=False,
                inherits_roles_from_parent=False,
                data_scope="own",
                active=True,
            )
        ],
        schema_version=1,
    )


# ---------------------------------------------------------------------------
# AP4: Rollen- und Berechtigungsvererbung
# ---------------------------------------------------------------------------

@router.get("/role-inheritance", response_model=RoleInheritanceChain, summary="Role inheritance abrufen")
async def get_role_inheritance(tenant_id: str = Depends(get_tenant_id)):
    """AP4: Liefert die effektive Rollenvererbungskette für den Mandanten."""
    return RoleInheritanceChain(
        tenant_id=tenant_id,
        effective_roles=[
            RoleDefinition(
                role_id="fibu.read",
                label="Finanzbuchhaltung Lesen",
                scope=RoleScope.TENANT,
                source_tenant_id=tenant_id,
                permissions=["finance:read", "ap_invoice:read", "payment_run:read"],
                inheritable=True,
            ),
            RoleDefinition(
                role_id="fibu.write",
                label="Finanzbuchhaltung Schreiben",
                scope=RoleScope.TENANT,
                source_tenant_id=tenant_id,
                permissions=["finance:write", "ap_invoice:create", "ap_invoice:update"],
                inheritable=True,
            ),
            RoleDefinition(
                role_id="fibu.admin",
                label="Finanzbuchhaltung Administration",
                scope=RoleScope.TENANT,
                source_tenant_id=tenant_id,
                permissions=["finance:admin", "ap_invoice:approve", "payment_run:execute"],
                inheritable=False,
            ),
            RoleDefinition(
                role_id="agrar.manager",
                label="Agrar Manager",
                scope=RoleScope.TENANT,
                source_tenant_id=tenant_id,
                permissions=["harvest:write", "quality:write", "settlement:read"],
                inheritable=True,
            ),
        ],
        inherited_from=[],
        schema_version=1,
    )


# ---------------------------------------------------------------------------
# AP5: Agenten- und Delegationssicherheitsmodell
# ---------------------------------------------------------------------------

@router.get("/agent-manifests", response_model=list[AgentManifest], summary="Agent manifests auflisten")
async def list_agent_manifests(tenant_id: str = Depends(get_tenant_id)):
    """AP5: Listet alle registrierten Agenten-Manifeste für den Mandanten."""
    return [
        build_default_agent_manifest("claude-code-assistant", "ai_assistant"),
        AgentManifest(
            agent_id="sepa-automation",
            agent_type="automation",
            label="SEPA Zahlungslauf-Automation",
            allowed_scopes=[AgentCapabilityScope.READ, AgentCapabilityScope.WRITE],
            denied_scopes=[AgentCapabilityScope.EXECUTE_PAYMENT, AgentCapabilityScope.APPROVE],
            max_delegation_depth=0,
            requires_human_confirmation_for=["execute_payment", "approve"],
            audit_all_actions=True,
        ),
        AgentManifest(
            agent_id="edi-integration",
            agent_type="integration",
            label="EDI/EDIFACT Integration",
            allowed_scopes=[AgentCapabilityScope.READ, AgentCapabilityScope.WRITE],
            denied_scopes=[AgentCapabilityScope.APPROVE, AgentCapabilityScope.EXECUTE_PAYMENT],
            max_delegation_depth=0,
            requires_human_confirmation_for=["approve"],
            audit_all_actions=True,
        ),
    ]


@router.get("/delegation-policy", response_model=DelegationPolicy, summary="Delegation policy abrufen")
async def get_delegation_policy(tenant_id: str = Depends(get_tenant_id)):
    """AP5: Liefert die aktive Delegationsrichtlinie des Mandanten."""
    return DelegationPolicy(
        tenant_id=tenant_id,
        entries=[],
        max_depth=2,
        require_audit_trail=True,
        schema_version=1,
    )


# ---------------------------------------------------------------------------
# AP6: Export- und Datenresidenzregeln
# ---------------------------------------------------------------------------

@router.get("/data-residency", response_model=ExportGovernancePolicy, summary="Data residency abrufen")
async def get_data_residency(tenant_id: str = Depends(get_tenant_id)):
    """AP6: Liefert die Export- und Datenresidenzregeln des Mandanten (GoBD-konform)."""
    return build_default_governance(tenant_id)


@router.get("/runtime-shield", response_model=dict, summary="Runtime shield abrufen")
async def get_runtime_shield(tenant_id: str = Depends(get_tenant_id)) -> dict:
    """Liefert tenant-isolierte Cache- und Rate-Limit-Defaults fuer Agenten und Workloads."""
    return {
        "tenant_id": tenant_id,
        "rate_limit_policies": [policy.as_dict() for policy in get_default_rate_limit_policies()],
        "cache_configs": [config.as_dict() for config in get_default_cache_configs()],
        "schema_version": 1,
    }
