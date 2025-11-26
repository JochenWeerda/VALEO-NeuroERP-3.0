from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest
from nats.aio.client import Client as NATS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Base, EpcisEvent
from app.db.session import get_engine, get_session_factory
from app.integration.subscribers import InventoryEventSubscribers
from app.integration.event_bus import EventBus


pytestmark = pytest.mark.asyncio


async def _init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _publish(nc: NATS, subject: str, payload: dict[str, Any]) -> None:
    import json

    await nc.publish(subject, json.dumps({"data": payload}).encode("utf-8"))


async def _count_epcis(session: AsyncSession) -> int:
    result = await session.execute(select(EpcisEvent))
    return len(result.scalars().all())


async def test_epcis_created_from_nats_events():
    # DB url is provided by CI services (postgres)
    await _init_db()
    session_factory = get_session_factory()

    # Start bus + subscribers
    nats_url = os.environ.get("INVENTORY_EVENT_BUS_URL", "nats://localhost:4222")
    bus = EventBus(url=nats_url, subject_prefix="inventory")
    await bus.connect()
    subs = InventoryEventSubscribers(bus, session_factory)
    await subs.start()

    # Publish sample purchase receipt (receiving)
    nc = NATS()
    await nc.connect(nats_url)
    await _publish(
        nc,
        "purchase.receipt.posted",
        {
            "warehouseId": "00000000-0000-0000-0000-000000000001",
            "defaultLocationId": "00000000-0000-0000-0000-000000000002",
            "dock": "DOCK-1",
            "lines": [{"sku": "SKU-IT-NATS", "quantity": 1}],
        },
    )
    # Publish sample sales shipment (shipping)
    await _publish(
        nc,
        "sales.shipment.confirmed",
        {
            "warehouseId": "00000000-0000-0000-0000-000000000001",
            "locationId": "00000000-0000-0000-0000-000000000002",
            "shipmentId": "SHP-1",
            "lines": [{"sku": "SKU-IT-NATS", "quantity": 1, "lotNumber": "SKU-IT-NATS"}],
        },
    )
    await asyncio.sleep(0.5)  # allow subscriber to process

    async with session_factory() as session:
        assert (await _count_epcis(session)) >= 1

    await nc.drain()
    await bus.close()

