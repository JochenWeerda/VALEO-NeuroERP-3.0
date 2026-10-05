"""Pure feeding-plan scaling and dosing rules."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
from typing import Any, Literal

RoundingMode = Literal["nearest", "up", "down"]


class FeedingPlanValidationError(ValueError):
    pass


@dataclass(frozen=True)
class MixingInstruction:
    sequence: int
    feed_id: str
    feed_name: str | None
    kg_fm_per_animal: Decimal | None
    raw_batch_kg: Decimal | None
    target_batch_kg: Decimal | None
    rounding_delta_kg: Decimal | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise FeedingPlanValidationError(f"{label} ist keine gueltige Zahl.") from exc
    if not result.is_finite():
        raise FeedingPlanValidationError(f"{label} muss endlich sein.")
    return result


def round_to_dosing_step(value: Decimal, step: Decimal, mode: RoundingMode) -> Decimal:
    if step <= 0:
        raise FeedingPlanValidationError("Dosierschritt muss groesser als null sein.")
    rounding = {"nearest": ROUND_HALF_UP, "up": ROUND_CEILING, "down": ROUND_FLOOR}.get(mode)
    if rounding is None:
        raise FeedingPlanValidationError("Unbekannter Rundungsmodus.")
    return (value / step).to_integral_value(rounding=rounding) * step


def build_mixing_instructions(
    snapshot: dict[str, Any], *, animal_count: int, dosing_step_kg: Any,
    rounding_mode: RoundingMode,
) -> list[MixingInstruction]:
    if animal_count <= 0:
        raise FeedingPlanValidationError("Tierzahl muss groesser als null sein.")
    step = _decimal(dosing_step_kg, "Dosierschritt")
    if step <= 0:
        raise FeedingPlanValidationError("Dosierschritt muss groesser als null sein.")
    components = snapshot.get("ration") or snapshot.get("components") or []
    if not isinstance(components, list) or not components:
        raise FeedingPlanValidationError("Rationssnapshot enthaelt keine Komponenten.")
    result: list[MixingInstruction] = []
    for index, component in enumerate(components):
        if not isinstance(component, dict) or not component.get("feed_id"):
            raise FeedingPlanValidationError(f"Komponente {index + 1} besitzt keine Futtermittel-ID.")
        amount = component.get("kg_fm")
        if amount is None:
            per_animal = raw = target = delta = None
        else:
            per_animal = _decimal(amount, f"FM-Menge Komponente {index + 1}")
            if per_animal < 0:
                raise FeedingPlanValidationError("FM-Menge darf nicht negativ sein.")
            raw = per_animal * Decimal(animal_count)
            target = round_to_dosing_step(raw, step, rounding_mode)
            delta = target - raw
        sequence = component.get("mixing_sequence", component.get("sequence", index + 1))
        try:
            sequence = int(sequence)
        except (TypeError, ValueError) as exc:
            raise FeedingPlanValidationError("Mischreihenfolge muss ganzzahlig sein.") from exc
        result.append(MixingInstruction(
            sequence=sequence, feed_id=str(component["feed_id"]),
            feed_name=component.get("feed_name") or component.get("name"),
            kg_fm_per_animal=per_animal, raw_batch_kg=raw,
            target_batch_kg=target, rounding_delta_kg=delta,
        ))
    sequences = [item.sequence for item in result]
    if any(sequence < 1 for sequence in sequences) or len(set(sequences)) != len(sequences):
        raise FeedingPlanValidationError("Mischreihenfolge muss positiv und eindeutig sein.")
    return sorted(result, key=lambda item: item.sequence)
