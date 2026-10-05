"""Persistent feeding-group and ration-version lifecycle."""

from .domain import (
    RationStatus,
    TransitionError,
    canonical_snapshot,
    snapshot_checksum,
    validate_transition,
)

__all__ = [
    "RationStatus",
    "TransitionError",
    "canonical_snapshot",
    "snapshot_checksum",
    "validate_transition",
]

