"""Pure component actual-feeding variance and value-consequence rules."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


class ActualFeedingValidationError(ValueError):
    pass


def _decimal(raw: Any, label: str) -> Decimal:
    try:
        value = Decimal(str(raw))
    except Exception as exc:
        raise ActualFeedingValidationError(f"{label} ist keine gueltige Zahl.") from exc
    if not value.is_finite():
        raise ActualFeedingValidationError(f"{label} muss endlich sein.")
    return value


@dataclass(frozen=True)
class ComponentActual:
    target_kg: Decimal
    actual_kg: Decimal
    delta_kg: Decimal
    delta_pct: Decimal | None


def calculate_component_actual(*, target_kg: Any, actual_kg: Any) -> ComponentActual:
    target, actual = _decimal(target_kg, "Sollmenge"), _decimal(actual_kg, "Istmenge")
    if target < 0 or actual < 0:
        raise ActualFeedingValidationError("Soll- und Istmenge duerfen nicht negativ sein.")
    delta = actual - target
    pct = None if target == 0 else (delta / target * Decimal(100)).quantize(Decimal("0.001"))
    return ComponentActual(target, actual, delta, pct)


def calculate_value_consequences(
    *, target_kg: Any, actual_kg: Any, price_eur_t: Any | None,
    nutrient_values: list[dict[str, Any]],
) -> dict[str, Any]:
    variance = calculate_component_actual(target_kg=target_kg, actual_kg=actual_kg)
    missing: list[str] = []
    if price_eur_t is None:
        cost = None
        missing.append("price")
    else:
        price = _decimal(price_eur_t, "Preis")
        if price < 0:
            raise ActualFeedingValidationError("Preis darf nicht negativ sein.")
        cost = {
            "target_eur": variance.target_kg * price / Decimal(1000),
            "actual_eur": variance.actual_kg * price / Decimal(1000),
            "delta_eur": variance.delta_kg * price / Decimal(1000),
            "price_eur_t": price,
        }
    nutrients: list[dict[str, Any]] = []
    units = {"g_per_kg": "g", "MJ_per_kg": "MJ"}
    for item in nutrient_values:
        code, unit = str(item["code"]), str(item["unit"])
        if item.get("basis") != "fresh_matter":
            missing.append(f"nutrient:{code}:unsupported_basis")
            continue
        if unit not in units:
            missing.append(f"nutrient:{code}:unsupported_unit")
            continue
        value = _decimal(item["value"], f"Naehrstoff {code}")
        nutrients.append({
            "code": code, "source_value": value, "source_unit": unit,
            "basis": item.get("basis"), "result_unit": units[unit],
            "target": variance.target_kg * value,
            "actual": variance.actual_kg * value,
            "delta": variance.delta_kg * value,
        })
    return {"cost": cost, "nutrients": nutrients, "missing": missing}


def validate_components(components: list[dict[str, Any]], planned_feed_ids: set[str]) -> None:
    feed_ids = [str(item.get("feed_id") or "") for item in components]
    if not feed_ids or any(not feed_id for feed_id in feed_ids):
        raise ActualFeedingValidationError("Mindestens eine Komponente mit Feed-ID ist erforderlich.")
    if len(feed_ids) != len(set(feed_ids)):
        raise ActualFeedingValidationError("Eine Ist-Komponente wurde doppelt angegeben.")
    unknown = sorted(set(feed_ids) - planned_feed_ids)
    if unknown:
        raise ActualFeedingValidationError(f"Komponente ist nicht im Plan: {', '.join(unknown)}")
    missing = sorted(planned_feed_ids - set(feed_ids))
    if missing:
        raise ActualFeedingValidationError(f"Plankomponente fehlt in der Ist-Erfassung: {', '.join(missing)}")
