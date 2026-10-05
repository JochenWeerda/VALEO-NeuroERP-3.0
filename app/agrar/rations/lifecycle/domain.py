"""Pure lifecycle rules for immutable ration versions."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any


class RationStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    RETIRED = "retired"
    ARCHIVED = "archived"


class TransitionError(ValueError):
    """Raised when a lifecycle transition violates the state machine."""


ALLOWED_TRANSITIONS: dict[RationStatus, frozenset[RationStatus]] = {
    RationStatus.DRAFT: frozenset({RationStatus.IN_REVIEW, RationStatus.ARCHIVED}),
    RationStatus.IN_REVIEW: frozenset({RationStatus.DRAFT, RationStatus.APPROVED}),
    RationStatus.APPROVED: frozenset({RationStatus.SCHEDULED, RationStatus.ACTIVE, RationStatus.ARCHIVED}),
    RationStatus.SCHEDULED: frozenset({RationStatus.APPROVED, RationStatus.ACTIVE}),
    RationStatus.ACTIVE: frozenset({RationStatus.RETIRED}),
    RationStatus.RETIRED: frozenset({RationStatus.ARCHIVED}),
    RationStatus.ARCHIVED: frozenset(),
}


def canonical_snapshot(snapshot: dict[str, Any]) -> str:
    """Stable JSON representation used for content identity and audit."""
    return json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def snapshot_checksum(snapshot: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_snapshot(snapshot).encode("utf-8")).hexdigest()


def validate_transition(
    current: RationStatus | str,
    target: RationStatus | str,
    *,
    reason: str | None,
    feeding_start: datetime | None = None,
    now: datetime | None = None,
) -> tuple[RationStatus, RationStatus]:
    source = RationStatus(current)
    destination = RationStatus(target)
    if destination not in ALLOWED_TRANSITIONS[source]:
        raise TransitionError(f"Ungueltiger Rationsstatus: {source.value} -> {destination.value}")
    if destination in {RationStatus.DRAFT, RationStatus.ARCHIVED, RationStatus.RETIRED} and not (reason or "").strip():
        raise TransitionError(f"Fuer den Wechsel nach {destination.value} ist ein Grund erforderlich.")
    if destination is RationStatus.SCHEDULED and feeding_start is None:
        raise TransitionError("Ein geplanter Fuetterungsbeginn ist erforderlich.")
    if destination is RationStatus.ACTIVE and feeding_start is not None:
        reference = now or datetime.now(timezone.utc)
        normalized = feeding_start if feeding_start.tzinfo else feeding_start.replace(tzinfo=timezone.utc)
        if normalized > reference:
            raise TransitionError("Eine Ration mit zukuenftigem Fuetterungsbeginn kann noch nicht aktiviert werden.")
    return source, destination

