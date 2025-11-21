from decimal import Decimal

from finance_shared.auth import (
    ApprovalPolicyConfig,
    ApprovalRule,
    FiBuAccessPolicy,
    FiBuPermission,
    FiBuRole,
    RoleAssignment,
)


def test_access_policy_permission_check():
    assignment = RoleAssignment(tenant_id="t1", user_id="u1", roles=[FiBuRole.SACHBEARBEITER])
    policy = FiBuAccessPolicy(assignment)

    assert policy.has_permission(FiBuPermission.JOURNAL_CREATE)
    assert not policy.has_permission(FiBuPermission.JOURNAL_APPROVE)


def test_access_policy_requires_approval():
    assignment = RoleAssignment(tenant_id="t1", user_id="u1", roles=[FiBuRole.SACHBEARBEITER])
    config = ApprovalPolicyConfig(
        rules=[ApprovalRule(min_amount=Decimal("1000.00"), currency="EUR", required_role=FiBuRole.FREIGEBER)]
    )
    policy = FiBuAccessPolicy(assignment, config)

    assert policy.require_approval(amount=Decimal("1200.00"), currency="EUR") is True


