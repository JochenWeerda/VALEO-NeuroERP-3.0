"""FEED-CONS-032 red contract for the measure lifecycle."""

from datetime import date

import pytest


def test_measure_lifecycle_requires_explicit_human_transitions() -> None:
    from app.agrar.rations.measure_lifecycle import transition_measure

    started = transition_measure(
        current_status="open",
        target_status="in_progress",
        reason="Waagenkontrolle wurde dem Stallteam verbindlich zugewiesen",
    )
    assert started == "in_progress"

    review = transition_measure(
        current_status="in_progress",
        target_status="review_due",
        reason="Umsetzung erfolgt, Wirksamkeitskontrolle nach drei Tagen",
    )
    assert review == "review_due"


def test_measure_cannot_complete_without_effectiveness_result() -> None:
    from app.agrar.rations.measure_lifecycle import (
        MeasureLifecycleError,
        transition_measure,
    )

    with pytest.raises(MeasureLifecycleError, match="Wirksamkeitskontrolle"):
        transition_measure(
            current_status="review_due",
            target_status="completed",
            reason="Kontrolle abgeschlossen und fachlich bewertet",
        )

    assert (
        transition_measure(
            current_status="review_due",
            target_status="completed",
            reason="Kontrolle abgeschlossen und fachlich bewertet",
            effectiveness="effective",
            effectiveness_result="Abweichung liegt an drei Folgetagen unter der Warnschwelle",
        )
        == "completed"
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [("open", "completed"), ("completed", "in_progress"), ("cancelled", "open")],
)
def test_measure_rejects_illegal_or_reopening_transitions(
    current: str, target: str
) -> None:
    from app.agrar.rations.measure_lifecycle import (
        MeasureLifecycleError,
        transition_measure,
    )

    with pytest.raises(MeasureLifecycleError):
        transition_measure(
            current_status=current,
            target_status=target,
            reason="Dieser direkte Statuswechsel ist fachlich nicht erlaubt",
            effectiveness="effective",
            effectiveness_result="Nur fuer den Completion-Negativfall vorhanden",
        )


def test_overdue_key_is_stable_per_measure_version_and_due_date() -> None:
    from app.agrar.rations.measure_lifecycle import overdue_notification_key

    assert overdue_notification_key("m-1", 3, date(2026, 7, 16)) == (
        "feeding-measure-overdue:m-1:v3:2026-07-16"
    )
