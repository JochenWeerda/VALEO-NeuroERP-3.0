"""Domain vocabulary and invariants for versioned feeding groups."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any


class GroupProfile(str, Enum):
    CUSTOM = "custom"
    FRESH_COW = "fresh_cow"
    HIGH_YIELD_COW = "high_yield_cow"
    MID_LACTATION_COW = "mid_lactation_cow"
    LATE_LACTATION_COW = "late_lactation_cow"
    DRY_FAR_OFF = "dry_far_off"
    DRY_CLOSE_UP = "dry_close_up"
    HEIFER = "heifer"
    CALF = "calf"
    BEEF_CATTLE = "beef_cattle"


class PregnancyStatus(str, Enum):
    UNKNOWN = "unknown"
    OPEN = "open"
    PREGNANT = "pregnant"


class GroupRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def validate_group_parameters(
    *,
    profile: GroupProfile | str,
    pregnancy_status: PregnancyStatus | str,
    gestation_day: int | None,
    milk_fat_pct: float | None,
    milk_protein_pct: float | None,
    valid_from: date,
    valid_until: date | None,
) -> dict[str, Any]:
    """Validate cross-field rules independent of API and persistence."""
    profile_value = GroupProfile(profile)
    pregnancy_value = PregnancyStatus(pregnancy_status)
    if gestation_day is not None:
        if pregnancy_value is not PregnancyStatus.PREGNANT:
            raise ValueError("Traechtigkeitstag ist nur fuer traechtige Gruppen zulaessig.")
        if not 0 <= gestation_day <= 305:
            raise ValueError("Traechtigkeitstag muss zwischen 0 und 305 liegen.")
    if valid_until is not None and valid_until < valid_from:
        raise ValueError("Gueltigkeitsende darf nicht vor dem Gueltigkeitsbeginn liegen.")
    if milk_fat_pct is not None and not 0 <= milk_fat_pct <= 15:
        raise ValueError("Milchfett muss zwischen 0 und 15 Prozent liegen.")
    if milk_protein_pct is not None and not 0 <= milk_protein_pct <= 10:
        raise ValueError("Milchprotein muss zwischen 0 und 10 Prozent liegen.")
    return {
        "profile": profile_value.value,
        "pregnancy_status": pregnancy_value.value,
        "gestation_day": gestation_day,
        "milk_fat_pct": milk_fat_pct,
        "milk_protein_pct": milk_protein_pct,
        "valid_from": valid_from,
        "valid_until": valid_until,
    }
