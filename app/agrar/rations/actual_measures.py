"""Pure deviation-policy and IOFC rules for actual feeding."""

from __future__ import annotations

from decimal import Decimal
from typing import Any


class DeviationPolicyError(ValueError):
    pass


def _decimal(raw: Any, label: str) -> Decimal:
    try:
        value = Decimal(str(raw))
    except Exception as exc:
        raise DeviationPolicyError(f"{label} ist keine gueltige Zahl.") from exc
    if not value.is_finite():
        raise DeviationPolicyError(f"{label} muss endlich sein.")
    return value


def validate_thresholds(warning_pct: Any, critical_pct: Any) -> tuple[Decimal, Decimal]:
    warning = _decimal(warning_pct, "Warnschwelle")
    critical = _decimal(critical_pct, "Kritisch-Schwelle")
    if warning <= 0 or critical <= warning or critical > 100:
        raise DeviationPolicyError(
            "Warnschwelle muss groesser null und Kritisch-Schwelle groesser als Warnschwelle bis 100 Prozent sein."
        )
    return warning, critical


def evaluate_deviation(
    *,
    target_kg: Any,
    actual_kg: Any,
    warning_pct: Any,
    critical_pct: Any,
    feed_class: str,
    policy_version: int,
) -> dict[str, Any] | None:
    warning, critical = validate_thresholds(warning_pct, critical_pct)
    target, actual = _decimal(target_kg, "Sollmenge"), _decimal(actual_kg, "Istmenge")
    if target < 0 or actual < 0:
        raise DeviationPolicyError("Soll- und Istmenge duerfen nicht negativ sein.")
    if target == 0:
        return None
    delta = actual - target
    pct = (abs(delta) / target * Decimal(100)).quantize(Decimal("0.001"))
    if pct < warning:
        return None
    severity, threshold = (
        ("critical", critical) if pct >= critical else ("warning", warning)
    )
    return {
        "severity": severity,
        "feed_class": feed_class,
        "policy_version": policy_version,
        "target_kg": target,
        "actual_kg": actual,
        "delta_kg": delta,
        "delta_pct": pct,
        "threshold_pct": threshold,
        "remedy": "Dosierung, Waage, Futterverfuegbarkeit und dokumentierte Ursache pruefen.",
    }


def calculate_iofc(
    *,
    milk_kg: Any | None,
    milk_price_eur_kg: Any | None,
    feed_cost_eur: Any | None,
) -> dict[str, Any] | None:
    if milk_kg is None or milk_price_eur_kg is None or feed_cost_eur is None:
        return None
    milk = _decimal(milk_kg, "Milchmenge")
    price = _decimal(milk_price_eur_kg, "Milchpreis")
    cost = _decimal(feed_cost_eur, "Futterkosten")
    if milk < 0 or price < 0 or cost < 0:
        raise DeviationPolicyError("IOFC-Eingaben duerfen nicht negativ sein.")
    revenue = milk * price
    return {
        "milk_revenue_eur": revenue,
        "feed_cost_eur": cost,
        "iofc_eur": revenue - cost,
        "formula": "milk_kg * milk_price_eur_kg - feed_cost_eur",
    }
