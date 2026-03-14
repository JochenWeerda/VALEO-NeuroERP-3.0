"""
Dunning/Mahnwesen-Modell — Wave 12 AP5/AP6

Mahnwesen-Positionen, Stufenregeln und Berechnung der wirksamen Mahnstufe.
Baut auf finance_followup.py-Contracts (Wave 4 AP5) auf.
"""
from __future__ import annotations

from datetime import date, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DunningLevelAction(str, Enum):
    REMINDER = "reminder"
    WARNING = "warning"
    FINAL_NOTICE = "final_notice"
    LEGAL = "legal"


class DunningLevelRule(BaseModel):
    level: int = Field(ge=1, le=4)
    overdue_days_min: int
    action: DunningLevelAction
    fee: float = 0.0
    description: str


class MahnwesenItem(BaseModel):
    """Einzelne offene Position im Mahnwesen."""

    item_id: str
    tenant_id: str
    debtor_id: str
    invoice_id: str
    invoice_date: date
    due_date: date
    open_amount: float
    currency: str = "EUR"
    current_dunning_level: int = 0
    blocked: bool = False
    block_reason: Optional[str] = None
    schema_version: int = 1


DEFAULT_DUNNING_RULES: list[DunningLevelRule] = [
    DunningLevelRule(
        level=1,
        overdue_days_min=7,
        action=DunningLevelAction.REMINDER,
        fee=0.0,
        description="Freundliche Erinnerung",
    ),
    DunningLevelRule(
        level=2,
        overdue_days_min=21,
        action=DunningLevelAction.WARNING,
        fee=5.0,
        description="Mahnung mit Mahngebühr",
    ),
    DunningLevelRule(
        level=3,
        overdue_days_min=35,
        action=DunningLevelAction.FINAL_NOTICE,
        fee=15.0,
        description="Letzte Mahnung vor Inkasso",
    ),
    DunningLevelRule(
        level=4,
        overdue_days_min=50,
        action=DunningLevelAction.LEGAL,
        fee=50.0,
        description="Übergabe an Inkasso/Rechtsabteilung",
    ),
]


def compute_dunning_level(
    item: MahnwesenItem,
    *,
    reference_date: date | None = None,
    rules: list[DunningLevelRule] | None = None,
) -> tuple[int, DunningLevelRule | None]:
    """Berechnet die wirksame Mahnstufe fuer eine offene Position.

    Gibt ``(level, rule)`` zurueck; level == 0 und rule == None bedeutet:
    noch kein Mahnlauf erforderlich.
    """
    if item.blocked:
        return (0, None)
    today = reference_date or date.today()
    overdue_days = (today - item.due_date).days
    if overdue_days <= 0:
        return (0, None)
    active_rules = sorted(rules or DEFAULT_DUNNING_RULES, key=lambda r: r.level, reverse=True)
    for rule in active_rules:
        if overdue_days >= rule.overdue_days_min:
            return (rule.level, rule)
    return (0, None)


def build_dunning_level_counts(
    items: list[MahnwesenItem],
    *,
    reference_date: date | None = None,
    rules: list[DunningLevelRule] | None = None,
) -> dict[str, int]:
    """Baut ein ``dunning_level_counts``-Dict fuer MahnwesenPreview."""
    counts: dict[str, int] = {}
    for item in items:
        level, _ = compute_dunning_level(item, reference_date=reference_date, rules=rules)
        if level > 0:
            counts[str(level)] = counts.get(str(level), 0) + 1
    return counts
