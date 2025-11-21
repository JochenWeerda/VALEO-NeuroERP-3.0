"""Scheduler-Aufgaben für monatliche InfraStat-Meldungen."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.integration.event_bus import EventBus


def _previous_month_start(today: date) -> date:
    first_of_month = date(today.year, today.month, 1)
    prev_month_last_day = first_of_month - timedelta(days=1)
    return date(prev_month_last_day.year, prev_month_last_day.month, 1)


async def trigger_workflow_for_ready_batches(session: AsyncSession, event_bus: EventBus | None) -> None:
    """Findet Batches und stößt Workflow-Sagas an."""

    if not event_bus:
        return

    stmt = select(models.DeclarationBatch).where(
        models.DeclarationBatch.status.in_(
            [models.DeclarationStatus.VALIDATING, models.DeclarationStatus.READY]
        )
    )
    result = await session.execute(stmt)
    batches = result.scalars().all()

    for batch in batches:
        await event_bus.publish(
            event_type="intrastat.batch.ready",
            tenant=batch.tenant_id,
            data={
                "batch_id": str(batch.id),
                "reference_period": batch.reference_period.isoformat(),
                "flow_type": batch.flow_type,
            },
        )


async def ensure_periodic_batches(session: AsyncSession, today: date | None = None) -> None:
    """Legt sicherstellen, dass für den aktuellen Monat Sammel-Batches existieren."""

    today = today or date.today()
    target_period = _previous_month_start(today)

    stmt = select(models.DeclarationBatch).where(
        models.DeclarationBatch.reference_period == target_period,
        models.DeclarationBatch.status == models.DeclarationStatus.COLLECTING,
    )
    result = await session.execute(stmt)
    batches = result.scalars().all()

    for batch in batches:
        batch.status = models.DeclarationStatus.VALIDATING
        await session.flush()

