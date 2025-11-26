"""NATS-Topic-Subscriptions für eingehende Domain-Events."""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db import models
from app.schemas import ReceiptCreate
from app.services import InventoryService

from .event_bus import EventBus
from .notifier import notify_ops

logger = logging.getLogger(__name__)


class InventoryEventSubscribers:
    """Registriert NATS-Subscriptions und triggert Inventory-Service-Funktionen."""

    def __init__(self, bus: EventBus, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._bus = bus
        self._session_factory = session_factory
        self._subscription_ids: list[int] = []

    async def start(self) -> None:
        """Subscriptions aktivieren."""
        purchase_sid = await self._bus.subscribe("purchase.receipt.posted", self._handle_purchase_receipt)
        shipment_sid = await self._bus.subscribe("sales.shipment.confirmed", self._handle_sales_shipment)
        self._subscription_ids.extend([purchase_sid, shipment_sid])

    async def stop(self) -> None:
        """Subscriptions wieder lösen."""
        for sid in list(self._subscription_ids):
            await self._bus.unsubscribe(sid)
        self._subscription_ids.clear()

    async def _handle_purchase_receipt(self, message: dict[str, Any]) -> None:
        payload = message.get("data") or {}
        lines = payload.get("lines") or []
        warehouse_id = payload.get("warehouseId")
        location_id = payload.get("locationId") or payload.get("defaultLocationId")
        reference = payload.get("purchaseOrderId") or payload.get("reference")

        if not warehouse_id or not location_id:
            logger.warning("purchase.receipt.posted ohne Warehouse/Location ignoriert: %s", json.dumps(payload))
            return

        async with self._session_factory() as session:
            service = InventoryService(session)
            for line in lines:
                try:
                    receipt = ReceiptCreate(
                        warehouse_id=UUID(warehouse_id),
                        location_id=UUID(location_id),
                        sku=line["sku"],
                        lot_number=line.get("lot") or line.get("lotNumber") or line["sku"],
                        quantity=float(line.get("quantity") or line.get("qty") or 0),
                        production_date=None,
                        expiry_date=None,
                        reference=reference,
                    )
                    await service.receive_stock(receipt)
                    await self._create_epcis_object_event(
                        session=session,
                        biz_step="receiving",
                        read_point=payload.get("dock") or payload.get("readPoint") or "RECEIVING",
                        sku=receipt.sku,
                        quantity=receipt.quantity,
                        lot_number=receipt.lot_number,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Konnte purchase.receipt.posted nicht verarbeiten: %s", exc)

    async def _handle_sales_shipment(self, message: dict[str, Any]) -> None:
        payload = message.get("data") or {}
        warehouse_id = payload.get("warehouseId")
        location_id = payload.get("locationId")
        shipments = payload.get("lines") or payload.get("items") or []

        if not warehouse_id:
            logger.warning("sales.shipment.confirmed ohne WarehouseId ignoriert: %s", json.dumps(payload))
            return

        async with self._session_factory() as session:
            service = InventoryService(session)
            for line in shipments:
                try:
                    await service.issue_stock(
                        warehouse_id=UUID(warehouse_id),
                        location_id=UUID(location_id) if location_id else None,
                        sku=line.get("sku") or line.get("articleNumber"),
                        lot_id=UUID(line["lotId"]) if line.get("lotId") else None,
                        lot_number=line.get("lotNumber"),
                        quantity=float(line.get("quantity") or line.get("qty") or 0),
                        reference=line.get("reference") or payload.get("shipmentId"),
                    )
                    await self._create_epcis_object_event(
                        session=session,
                        biz_step="shipping",
                        read_point=payload.get("dock") or payload.get("readPoint") or "SHIPPING",
                        sku=line.get("sku") or line.get("articleNumber"),
                        quantity=float(line.get("quantity") or line.get("qty") or 0),
                        lot_number=line.get("lotNumber"),
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Konnte sales.shipment.confirmed nicht verarbeiten: %s", exc)

    async def _create_epcis_object_event(
        self,
        *,
        session: AsyncSession,
        biz_step: str,
        read_point: str | None,
        sku: str | None,
        quantity: float | None,
        lot_number: str | None,
    ) -> None:
        lot: models.Lot | None = None
        if lot_number:
            lot = (
                await session.execute(
                    models.select(models.Lot).where(models.Lot.lot_number == lot_number)  # type: ignore[attr-defined]
                )
            )  # pragma: no cover
        # Bestimme lot_id falls verfügbar
        lot_id = None
        if lot and hasattr(lot, "scalar_one_or_none"):
            lot_row = lot.scalar_one_or_none()
            lot_id = getattr(lot_row, "id", None)
        event = models.EpcisEvent(  # type: ignore[attr-defined]
            event_type=models.EpcisEventType.OBJECT,  # type: ignore[attr-defined]
            biz_step=biz_step,
            read_point=read_point,
            lot_id=lot_id,
            sku=sku,
            quantity=quantity,
            extensions=None,
        )
        # Auto-Remediation: bis zu 3 Versuche mit Eskalation
        for attempt in range(1, 4):
            try:
                session.add(event)
                await session.flush()
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 3:
                    await notify_ops(
                        "EPCIS-Event Persistenz fehlgeschlagen",
                        {"bizStep": biz_step, "readPoint": read_point or "", "error": str(exc)[:200]},
                    )
                else:
                    continue
