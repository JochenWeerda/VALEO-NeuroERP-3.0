"""
Tests for NC-G5 prompt pack registry.
"""

from app.agents.neuroassist_contracts import PromptPack
from app.services.prompt_pack_registry import (
    register_prompt_pack,
    get_active_prompt_pack,
    list_active_variants,
    select_prompt_pack_variant,
    rollback_prompt_pack,
)


def _make_pack(key: str, role: str) -> PromptPack:
    return PromptPack(
        prompt_pack_key=key,
        role_key=role,
        mission="Test mission",
        scope="Test scope",
        constraints=["c1"],
        inputs=["input1"],
        decision_policy=["p1"],
        output_schema="schema-v1",
        handover_rules=["handover"],
    )


def test_register_and_get_active_prompt_pack():
    pack = _make_pack("pp-1", "role-1")
    register_prompt_pack(pack, "1.0", "t-001")
    active = get_active_prompt_pack("pp-1", "t-001")
    assert active is not None
    assert active["prompt_pack_key"] == "pp-1"


def test_variant_selection_prefers_nonzero_weight():
    pack_a = _make_pack("pp-ab", "role-1")
    pack_b = _make_pack("pp-ab", "role-1")

    register_prompt_pack(pack_a, "1.0", "t-002", variant_key="A", traffic_weight=1.0)
    register_prompt_pack(pack_b, "1.0", "t-002", variant_key="B", traffic_weight=0.0)

    selected = select_prompt_pack_variant("pp-ab", "t-002", seed="user-123")
    assert selected is not None
    assert selected["variant_key"] == "A"

    variants = list_active_variants("pp-ab", "t-002")
    assert len(variants) == 2


def test_rollback_prompt_pack():
    pack_v1 = _make_pack("pp-rollback", "role-1")
    pack_v2 = _make_pack("pp-rollback", "role-1")

    register_prompt_pack(pack_v1, "1.0", "t-003")
    register_prompt_pack(pack_v2, "2.0", "t-003")
    rolled = rollback_prompt_pack("pp-rollback", "t-003")
    assert rolled is not None
    assert rolled["version"] == "1.0"
