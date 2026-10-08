"""Mask-action catalog merge into ki-usability ActionRegistry."""

from __future__ import annotations

from app.services.action_registry import (
    ACTIONS,
    ALL_ACTIONS,
    SCREEN_MASK_ACTIONS,
    action_registry,
)


def test_registry_merges_generated_screen_mask_actions() -> None:
    assert len(ACTIONS) >= 70
    assert len(SCREEN_MASK_ACTIONS) >= 80
    assert len(ALL_ACTIONS) == len(ACTIONS) + len(SCREEN_MASK_ACTIONS)
    assert len(action_registry.all_ids()) == len(ALL_ACTIONS)
    assert (
        action_registry.builtin_count() + action_registry.screen_mask_count()
        == len(ALL_ACTIONS)
    )
    sample = next(
        (a for a in SCREEN_MASK_ACTIONS if a.id.startswith("mask:")),
        None,
    )
    assert sample is not None
    assert action_registry.get(sample.id) is sample
    assert "mask-action" in {a.category for a in SCREEN_MASK_ACTIONS}
