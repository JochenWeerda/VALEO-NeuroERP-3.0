from decimal import Decimal

from fastapi import Request
from finance_shared.auth import FiBuPermission, FiBuRole

from app.dependencies import get_access_policy, get_audit_trail
from app.storage.approval_rules import ApprovalRuleRecord


def _build_request(headers: dict[str, str] | None = None) -> Request:
    scope = {
        "type": "http",
        "headers": [
            (key.lower().encode("latin-1"), value.encode("latin-1")) for key, value in (headers or {}).items()
        ],
    }
    request = Request(scope)
    request.state.tenant_id = "tenant-1"
    return request


class _InMemoryRuleStore:
    def __init__(self) -> None:
        self._rules = [
            ApprovalRuleRecord(
                tenant_id="tenant-1",
                currency="EUR",
                min_amount=Decimal("500.00"),
                required_role=FiBuRole.FREIGEBER,
            )
        ]

    def list_rules(self, tenant_id: str):
        return self._rules


def test_access_policy_uses_roles_header():
    request = _build_request({"X-FIBU-ROLES": "freigeber", "X-User-ID": "user-1"})
    policy = get_access_policy(request, tenant="tenant-1", store=_InMemoryRuleStore())

    assert policy.has_permission(FiBuPermission.JOURNAL_APPROVE) is True
    assert policy.user_id == "user-1"


def test_audit_trail_is_scoped_per_tenant():
    trail = get_audit_trail(tenant="tenant-99")
    entry = trail.create_entry(
        entity_type="journal_entry",
        entity_id="J-1",
        action="create",
        payload={},
        user_id="system",
    )
    trail.append_entry(entry)

    assert len(trail.entries()) == 1
    assert trail.tenant_id == "tenant-99"


