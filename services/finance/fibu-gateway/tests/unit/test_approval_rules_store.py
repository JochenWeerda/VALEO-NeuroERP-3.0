from decimal import Decimal

from finance_shared.auth import FiBuRole

from app.storage.approval_rules import ApprovalRuleStore


def test_store_returns_tenant_specific_rules(tmp_path):
    db_path = tmp_path / "rules.db"
    store = ApprovalRuleStore(
        str(db_path),
        default_min_amount=Decimal("750.00"),
        default_currency="EUR",
        default_role=FiBuRole.FREIGEBER,
    )

    store.upsert_rule(
        tenant_id="tenant-a",
        currency="EUR",
        min_amount=Decimal("1500"),
        required_role=FiBuRole.ADMIN,
    )

    rules = store.list_rules("tenant-a")
    assert len(rules) == 1
    assert rules[0].required_role == FiBuRole.ADMIN


def test_store_falls_back_to_default_rule(tmp_path):
    db_path = tmp_path / "rules.db"
    store = ApprovalRuleStore(str(db_path))

    rules = store.list_rules("unknown-tenant")
    assert len(rules) == 1
    assert rules[0].tenant_id == "*"

