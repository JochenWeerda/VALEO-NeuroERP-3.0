"""
Dunning-Run Execution Model — Wave 13 AP5/AP6

Batch-Ausführung eines Mahnlaufs auf Basis des dunning_model.py-Contracts (Wave 12).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.core.dunning_model import (
    DEFAULT_DUNNING_RULES,
    DunningLevelRule,
    MahnwesenItem,
    compute_dunning_level,
)


DunningRunStatus = Literal["pending", "completed", "partial", "failed"]


class DunningRunItem(BaseModel):
    """Ergebnis der Mahnstufenberechnung fuer eine einzelne Position."""

    item_id: str
    debtor_id: str
    invoice_id: str
    open_amount: float
    previous_dunning_level: int
    new_dunning_level: int
    level_changed: bool
    fee: float = 0.0
    action_required: str | None = None
    schema_version: int = 1


class DunningRunResult(BaseModel):
    """Ergebnis eines vollständigen Mahnlaufs."""

    run_id: str
    tenant_id: str
    reference_date: date
    status: DunningRunStatus
    processed_count: int
    escalated_count: int
    blocked_count: int
    total_fees: float
    items: list[DunningRunItem] = Field(default_factory=list)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


def execute_dunning_run(
    tenant_id: str,
    items: list[MahnwesenItem],
    *,
    reference_date: date | None = None,
    rules: list[DunningLevelRule] | None = None,
) -> DunningRunResult:
    """Führt einen Mahnlauf durch und gibt das Gesamtergebnis zurück."""
    today = reference_date or date.today()
    active_rules = rules or DEFAULT_DUNNING_RULES
    run_items: list[DunningRunItem] = []
    blocked_count = 0
    escalated_count = 0
    total_fees = 0.0

    for item in items:
        if item.blocked:
            blocked_count += 1
            run_items.append(DunningRunItem(
                item_id=item.item_id,
                debtor_id=item.debtor_id,
                invoice_id=item.invoice_id,
                open_amount=item.open_amount,
                previous_dunning_level=item.current_dunning_level,
                new_dunning_level=item.current_dunning_level,
                level_changed=False,
            ))
            continue

        new_level, rule = compute_dunning_level(item, reference_date=today, rules=active_rules)
        level_changed = new_level != item.current_dunning_level and new_level > 0
        fee = rule.fee if rule and level_changed else 0.0
        total_fees += fee

        if new_level == 4:
            escalated_count += 1

        run_items.append(DunningRunItem(
            item_id=item.item_id,
            debtor_id=item.debtor_id,
            invoice_id=item.invoice_id,
            open_amount=item.open_amount,
            previous_dunning_level=item.current_dunning_level,
            new_dunning_level=new_level,
            level_changed=level_changed,
            fee=fee,
            action_required=rule.action.value if rule and new_level > 0 else None,
        ))

    return DunningRunResult(
        run_id=f"dr-{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        reference_date=today,
        status="completed",
        processed_count=len(items),
        escalated_count=escalated_count,
        blocked_count=blocked_count,
        total_fees=total_fees,
        items=run_items,
    )
