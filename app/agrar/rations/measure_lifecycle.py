"""Pure lifecycle rules for human-owned feeding measures."""

from __future__ import annotations

from datetime import date
from typing import Literal


MeasureStatus = Literal["open", "in_progress", "review_due", "completed", "cancelled"]
Effectiveness = Literal["effective", "partial", "ineffective"]


class MeasureLifecycleError(ValueError):
    pass


_TRANSITIONS: dict[str, frozenset[str]] = {
    "open": frozenset({"in_progress", "cancelled"}),
    "in_progress": frozenset({"review_due", "cancelled"}),
    "review_due": frozenset({"in_progress", "completed", "cancelled"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
}


def transition_measure(
    *,
    current_status: str,
    target_status: str,
    reason: str,
    effectiveness: Effectiveness | None = None,
    effectiveness_result: str | None = None,
) -> MeasureStatus:
    if current_status not in _TRANSITIONS or target_status not in _TRANSITIONS:
        raise MeasureLifecycleError("Unbekannter Massnahmenstatus.")
    if target_status not in _TRANSITIONS[current_status]:
        raise MeasureLifecycleError(
            f"Statuswechsel {current_status} -> {target_status} ist nicht erlaubt."
        )
    if len(reason.strip()) < 10:
        raise MeasureLifecycleError("Statuswechsel erfordert einen fachlichen Grund.")
    if target_status == "completed" and (
        effectiveness not in {"effective", "partial", "ineffective"}
        or len((effectiveness_result or "").strip()) < 10
    ):
        raise MeasureLifecycleError(
            "Abschluss erfordert Wirksamkeitskontrolle und dokumentiertes Ergebnis."
        )
    return target_status  # type: ignore[return-value]


def overdue_notification_key(measure_id: str, version: int, due_date: date) -> str:
    if not measure_id or version < 1:
        raise MeasureLifecycleError(
            "Massnahme und Version sind fuer die Wiedervorlage erforderlich."
        )
    return f"feeding-measure-overdue:{measure_id}:v{version}:{due_date.isoformat()}"


__all__ = [
    "Effectiveness",
    "MeasureLifecycleError",
    "MeasureStatus",
    "overdue_notification_key",
    "transition_measure",
]
