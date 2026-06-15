"""WM-AGRI-CHAIN-002 — Materialfluss ↔ Lieferketten-Log + Outbox.

Hängt Agrar-Silo-/Materialfluss-Mutationen an `domain_inventory.supply_chain_events`
(append-only, ticket_id optional) und schreibt parallele IntegrationEvents in die
Outbox (transaktional mit dem Aufrufer-Commit).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.domains.shared.events import IntegrationEvent, get_event_publisher
from app.infrastructure.eventbus.outbox import OutboxPublisher
from app.services.supply_chain_event_service import SupplyChainEventService

logger = logging.getLogger(__name__)

# DOM-SUPPLY-004: freie Stufe für Lager-interne Förder-/Anlagenereignisse (kein Wiegeschein nötig).
MATERIAL_FLOW_STAGE = "materialfluss"


def append_material_flow_supply_chain_event(
    db: Session,
    tenant_id: str,
    *,
    event_type: str,
    ref_type: str | None,
    ref_id: str | None,
    ref_label: str | None = None,
    status_from: str | None = None,
    status_to: str | None = None,
    payload: dict[str, Any] | None = None,
    ticket_id: str | None = None,
) -> None:
    """Schreibt ein Kettenereignis in dieselbe Session wie der Aufrufer (commit=False)."""
    SupplyChainEventService(db, tenant_id).record(
        ticket_id=ticket_id,
        stage=MATERIAL_FLOW_STAGE,
        event_type=event_type,
        ref_type=ref_type,
        ref_id=ref_id,
        ref_label=ref_label,
        status_from=status_from,
        status_to=status_to,
        payload=payload,
        bediener="wm-agri-silo-api",
        source="auto",
        commit=False,
    )


def store_material_flow_outbox_best_effort(
    db: Session,
    tenant_id: str,
    *,
    event_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
) -> None:
    """Outbox-Eintrag (best-effort); bei Fehler nur loggen — Aufrufer committed danach."""

    async def _store() -> None:
        outbox = OutboxPublisher(db, get_event_publisher())
        await outbox.store_event(
            IntegrationEvent(
                aggregate_id=aggregate_id,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                payload=payload,
            ),
            tenant_id=tenant_id,
        )

    try:
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if running_loop is None:
            asyncio.run(_store())
            return

        task = running_loop.create_task(_store())

        def _log_task_failure(completed_task: asyncio.Task[None]) -> None:
            try:
                completed_task.result()
            except Exception as exc:
                logger.warning(
                    "Materialfluss-Outbox asynchron fehlgeschlagen (best-effort): %s",
                    exc,
                )

        task.add_done_callback(_log_task_failure)
    except Exception as exc:
        logger.warning("Materialfluss-Outbox fehlgeschlagen (best-effort): %s", exc)
