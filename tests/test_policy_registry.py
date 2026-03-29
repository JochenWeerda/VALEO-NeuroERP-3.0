"""
Tests for NC-G4 policy registry enhancements.
"""

from app.services.policy_registry import (
    register_policy,
    get_active_policy,
    list_active_variants,
    select_policy_variant,
    rollback_policy,
)


def test_register_and_get_active_policy():
    register_policy("risk_policy", "Risk Policy", {"threshold": 0.9}, "1.0", "t-001")
    active = get_active_policy("risk_policy", "t-001")
    assert active is not None
    assert active["policy_id"] == "risk_policy"


def test_variant_selection_prefers_nonzero_weight():
    register_policy(
        "risk_policy_ab",
        "Risk A",
        {"threshold": 0.8},
        "1.0",
        "t-001",
        variant_key="A",
        traffic_weight=1.0,
    )
    register_policy(
        "risk_policy_ab",
        "Risk B",
        {"threshold": 0.9},
        "1.0",
        "t-001",
        variant_key="B",
        traffic_weight=0.0,
    )

    selected = select_policy_variant("risk_policy_ab", "t-001", seed="user-123")
    assert selected is not None
    assert selected["variant_key"] == "A"

    variants = list_active_variants("risk_policy_ab", "t-001")
    assert len(variants) == 2


def test_rollback_policy():
    register_policy("rollback_policy", "Policy v1", {"rule": 1}, "1.0", "t-002")
    register_policy("rollback_policy", "Policy v2", {"rule": 2}, "2.0", "t-002")
    rolled = rollback_policy("rollback_policy", "t-002")
    assert rolled is not None
    assert rolled["version"] == "1.0"
