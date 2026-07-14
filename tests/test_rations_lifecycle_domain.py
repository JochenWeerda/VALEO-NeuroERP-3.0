from datetime import datetime, timedelta, timezone

import pytest

from app.agrar.rations.lifecycle import (
    RationStatus,
    TransitionError,
    canonical_snapshot,
    snapshot_checksum,
    validate_transition,
)


def test_snapshot_identity_is_order_independent() -> None:
    left = {"feeds": [{"id": "mais", "kg_dm": 8.5}], "group": {"id": "g1", "count": 42}}
    right = {"group": {"count": 42, "id": "g1"}, "feeds": [{"kg_dm": 8.5, "id": "mais"}]}

    assert canonical_snapshot(left) == canonical_snapshot(right)
    assert snapshot_checksum(left) == snapshot_checksum(right)


def test_release_path_and_required_reason() -> None:
    assert validate_transition("draft", "in_review", reason=None) == (
        RationStatus.DRAFT,
        RationStatus.IN_REVIEW,
    )
    assert validate_transition("in_review", "approved", reason="Fachlich geprueft")[1] is RationStatus.APPROVED

    with pytest.raises(TransitionError, match="Grund"):
        validate_transition("in_review", "draft", reason="")


def test_schedule_requires_start_and_future_start_cannot_be_activated() -> None:
    future = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(TransitionError, match="Fuetterungsbeginn"):
        validate_transition("approved", "scheduled", reason=None)

    assert validate_transition("approved", "scheduled", reason=None, feeding_start=future)[1] is RationStatus.SCHEDULED
    with pytest.raises(TransitionError, match="zukuenftig"):
        validate_transition("scheduled", "active", reason=None, feeding_start=future)


def test_invalid_shortcut_is_rejected() -> None:
    with pytest.raises(TransitionError, match="draft -> active"):
        validate_transition("draft", "active", reason="shortcut")

