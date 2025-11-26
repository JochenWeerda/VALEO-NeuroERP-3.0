"""Geschäftslogik für Mehrlager- & Chargenverwaltung."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db import models
from app.integration.event_bus import EventBus
from app.integration.workflow_client import emit_workflow_event
from app.schemas import (
    ArticleSummary,
    LocationCreate,
    LocationRead,
    LotListItem,
    LotListResponse,
    LotTraceResponse,
    ReceiptCreate,
    StockItemRead,
    StockMovementCreate,
    StockMovementRecord,
    TransactionRecord,
    TransferCreate,
    WarehouseCreate,
    WarehouseRead,
    WarehouseUpdate,
)


EVENT_VERSION_DEFAULT = 1


class InventoryService:
    def __init__(self, session: AsyncSession, *, event_bus: EventBus | None = None, tenant_id: Optional[str] = None) -> None:
        self._session = session
        self._event_bus = event_bus
        self._tenant_id = tenant_id or settings.DEFAULT_TENANT

    async def create_warehouse(self, payload: WarehouseCreate) -> WarehouseRead:
        warehouse = models.Warehouse(
            code=payload.code,
            name=payload.name,
            address=payload.address,
            is_active=payload.is_active,
            tenant_id=self._tenant_id,
        )
        self._session.add(warehouse)
        await self._session.flush()
        await self._publish_event(
            event_type="inventory.warehouse.created",
            aggregate_id=str(warehouse.id),
            aggregate_type="inventory.warehouse",
            data={
                "warehouseId": str(warehouse.id),
                "code": warehouse.code,
                "name": warehouse.name,
                "createdAt": warehouse.created_at.isoformat(),
            },
        )
        return WarehouseRead.model_validate(warehouse, from_attributes=True)

    async def list_warehouses(self, *, only_active: bool | None = None) -> list[WarehouseRead]:
        stmt = select(models.Warehouse)
        if only_active is not None:
            stmt = stmt.where(models.Warehouse.is_active.is_(only_active))
        result = await self._session.execute(stmt.order_by(models.Warehouse.code))
        warehouses = result.scalars().all()
        return [WarehouseRead.model_validate(item, from_attributes=True) for item in warehouses]

    async def get_warehouse(self, warehouse_id: UUID) -> WarehouseRead:
        warehouse = await self._session.get(models.Warehouse, warehouse_id)
        if not warehouse:
            raise ValueError("Warehouse not found")
        return WarehouseRead.model_validate(warehouse, from_attributes=True)

    async def update_warehouse(self, warehouse_id: UUID, payload: WarehouseUpdate) -> WarehouseRead:
        warehouse = await self._session.get(models.Warehouse, warehouse_id)
        if not warehouse:
            raise ValueError("Warehouse not found")
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(warehouse, key, value)
        await self._session.flush()
        return WarehouseRead.model_validate(warehouse, from_attributes=True)

    async def delete_warehouse(self, warehouse_id: UUID) -> None:
        warehouse = await self._session.get(models.Warehouse, warehouse_id)
        if not warehouse:
            raise ValueError("Warehouse not found")
        await self._session.delete(warehouse)

    async def add_location(self, warehouse_id: UUID, payload: LocationCreate) -> LocationRead:
        location = models.Location(
            warehouse_id=warehouse_id,
            code=payload.code,
            location_type=payload.location_type,
            capacity_units=payload.capacity_units,
        )
        self._session.add(location)
        await self._session.flush()
        await self._publish_event(
            event_type="inventory.location.created",
            aggregate_id=str(location.id),
            aggregate_type="inventory.location",
            data={
                "locationId": str(location.id),
                "warehouseId": str(location.warehouse_id),
                "code": location.code,
                "locationType": location.location_type,
            },
        )
        return LocationRead.model_validate(location, from_attributes=True)

    async def receive_stock(self, payload: ReceiptCreate) -> StockItemRead:
        lot = await self._get_or_create_lot(payload)
        stock_item = await self._get_or_create_stock_item(payload.warehouse_id, payload.location_id, lot.id)
        stock_item.quantity = float(stock_item.quantity) + payload.quantity

        transaction = models.InventoryTransaction(
            stock_item_id=stock_item.id,
            transaction_type=models.InventoryTransactionType.RECEIPT,
            quantity=payload.quantity,
            reference=payload.reference,
            to_location_id=payload.location_id,
        )
        self._session.add(transaction)
        await self._session.flush()
        await self._publish_event(
            event_type="inventory.goods.received",
            aggregate_id=str(stock_item.id),
            aggregate_type="inventory.stock_item",
            data={
                "stockItemId": str(stock_item.id),
                "lotId": str(stock_item.lot_id),
                "warehouseId": str(stock_item.warehouse_id),
                "locationId": str(stock_item.location_id),
                "quantity": payload.quantity,
                "reference": payload.reference,
                "receiptTimestamp": datetime.utcnow().isoformat(),
                "sku": lot.sku,
                "lotNumber": lot.lot_number,
            },
        )
        return await self._serialize_stock_item(stock_item)

    async def transfer_stock(self, payload: TransferCreate) -> StockItemRead:
        # Determine source stock item
        stock_item = None
        if payload.source_stock_item_id:
            stock_item = await self._session.get(models.StockItem, payload.source_stock_item_id, options=[selectinload(models.StockItem.lot)])
        else:
            query = (
                select(models.StockItem)
                .where(
                    models.StockItem.warehouse_id == payload.source_warehouse_id,
                    models.StockItem.location_id == payload.source_location_id,
                    models.StockItem.lot_id == payload.lot_id,
                )
                .options(selectinload(models.StockItem.lot))
            )
            stock_item = (await self._session.execute(query)).scalar_one_or_none()
        if not stock_item:
            raise ValueError("Source stock item not found")
        if float(stock_item.quantity) < payload.quantity:
            raise ValueError("Insufficient quantity")

        stock_item.quantity = float(stock_item.quantity) - payload.quantity

        destination_stock = await self._get_or_create_stock_item(
            payload.destination_warehouse_id,
            payload.destination_location_id,
            stock_item.lot_id,
        )
        destination_stock.quantity = float(destination_stock.quantity) + payload.quantity

        transaction = models.InventoryTransaction(
            stock_item_id=stock_item.id,
            transaction_type=models.InventoryTransactionType.TRANSFER,
            quantity=payload.quantity,
            reference=payload.reference,
            from_location_id=payload.source_location_id,
            to_location_id=payload.destination_location_id,
        )
        self._session.add(transaction)
        await self._session.flush()
        await self._publish_event(
            event_type="inventory.stock.transferred",
            aggregate_id=str(stock_item.id),
            aggregate_type="inventory.stock_item",
            data={
                "sourceStockItemId": str(stock_item.id),
                "lotId": str(stock_item.lot_id),
                "sourceWarehouseId": str(payload.source_warehouse_id),
                "destinationWarehouseId": str(payload.destination_warehouse_id),
                "sourceLocationId": str(payload.source_location_id) if payload.source_location_id else None,
                "destinationLocationId": str(payload.destination_location_id),
                "quantity": payload.quantity,
                "reference": payload.reference,
                "transferTimestamp": datetime.utcnow().isoformat(),
            },
        )
        return await self._serialize_stock_item(destination_stock)

    async def trace_lot(self, lot_id: UUID) -> LotTraceResponse:
        lot = await self._session.get(models.Lot, lot_id)
        if not lot:
            raise ValueError("Lot not found")
        query = (
            select(models.InventoryTransaction)
            .join(models.StockItem)
            .where(models.StockItem.lot_id == lot_id)
            .order_by(models.InventoryTransaction.created_at)
        )
        transactions = (await self._session.execute(query)).scalars().all()
        await self._publish_event(
            event_type="inventory.lot.trace.requested",
            aggregate_id=str(lot.id),
            aggregate_type="inventory.lot",
            data={
                "lotId": str(lot.id),
                "sku": lot.sku,
                "lotNumber": lot.lot_number,
                "transactionCount": len(transactions),
            },
        )
        return LotTraceResponse(
            lot_id=lot.id,
            sku=lot.sku,
            lot_number=lot.lot_number,
            transactions=[TransactionRecord.model_validate(txn, from_attributes=True) for txn in transactions],
        )

    async def list_lots(self, search: str | None = None) -> LotListResponse:
        stmt = (
            select(models.StockItem, models.Lot, models.Location, models.Warehouse)
            .join(models.Lot, models.StockItem.lot)
            .join(models.Location, models.StockItem.location)
            .join(models.Warehouse, models.Warehouse.id == models.StockItem.warehouse_id)
        )

        if search:
            like_pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(models.Lot.lot_number).like(like_pattern),
                    func.lower(models.Lot.sku).like(like_pattern),
                    func.lower(models.Location.code).like(like_pattern),
                    func.lower(models.Warehouse.code).like(like_pattern),
                )
            )

        result = await self._session.execute(stmt)
        rows = result.all()

        items: list[LotListItem] = []
        for stock_item, lot, location, warehouse in rows:
            items.append(
                LotListItem(
                    id=stock_item.id,
                    lot_number=lot.lot_number,
                    commodity=lot.sku,
                    quantity=float(stock_item.quantity),
                    unit="PCS",
                    location=f"{warehouse.code}/{location.code}",
                    quality_status="pending",
                    expiry_date=(lot.expiry_date or lot.production_date or datetime.utcnow()),
                    supplier="unbekannt",
                )
            )

        return LotListResponse(items=items, total=len(items))

    async def list_articles(self) -> list[ArticleSummary]:
        stmt = (
            select(
                models.Lot.sku,
                func.sum(models.StockItem.quantity).label("qty"),
                func.sum(models.StockItem.reserved_quantity).label("reserved"),
            )
            .join(models.StockItem.lot)
            .group_by(models.Lot.sku)
            .order_by(models.Lot.sku)
        )
        result = await self._session.execute(stmt)
        articles: list[ArticleSummary] = []
        for row in result.all():
            sku = row.sku
            quantity = float(row.qty or 0)
            reserved = float(row.reserved or 0)
            articles.append(
                ArticleSummary(
                    id=sku,
                    article_number=sku,
                    name=sku,
                    current_stock=quantity,
                    available_stock=max(quantity - reserved, 0),
                    reserved_stock=reserved,
                )
            )
        return articles

    async def list_stock_movements(self, *, limit: int = 100) -> list[StockMovementRecord]:
        stmt = (
            select(models.InventoryTransaction, models.StockItem)
            .join(models.StockItem, models.InventoryTransaction.stock_item_id == models.StockItem.id)
            .order_by(models.InventoryTransaction.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        movements: list[StockMovementRecord] = []
        for txn, stock_item in result.all():
            movements.append(self._map_transaction(txn, stock_item))
        return movements

    async def create_stock_movement(self, payload: StockMovementCreate) -> StockMovementRecord:
        movement = payload.movement_type.lower()
        transaction: models.InventoryTransaction | None = None

        if movement == "in":
            receipt = await self.receive_stock(
                ReceiptCreate(
                    warehouse_id=payload.warehouse_id,
                    location_id=payload.location_id,
                    sku=payload.article_id,
                    lot_number=payload.lot_number or payload.article_id,
                    quantity=payload.quantity,
                    reference=payload.reference_number,
                )
            )
            transaction = await self._latest_transaction_for_item(receipt.id)
        elif movement == "out":
            stock = await self.issue_stock(
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
                sku=payload.article_id,
                lot_id=payload.lot_id,
                lot_number=payload.lot_number,
                quantity=payload.quantity,
                reference=payload.reference_number,
            )
            transaction = await self._latest_transaction_for_item(stock.id)
        elif movement == "transfer":
            if not payload.destination_location_id or not payload.destination_warehouse_id:
                raise ValueError("Destination warehouse/location required for transfer movements")
            source_stock = await self._find_stock_item(
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
                sku=payload.article_id,
                lot_id=payload.lot_id,
                lot_number=payload.lot_number,
            )
            if not source_stock:
                raise ValueError("Source stock item not found for transfer")
            transfer_payload = TransferCreate(
                source_stock_item_id=source_stock.id,
                source_location_id=payload.location_id,
                source_warehouse_id=payload.warehouse_id,
                destination_location_id=payload.destination_location_id,
                destination_warehouse_id=payload.destination_warehouse_id,
                lot_id=source_stock.lot_id,
                quantity=payload.quantity,
                reference=payload.reference_number,
            )
            await self.transfer_stock(transfer_payload)
            transaction = await self._latest_transaction_for_item(source_stock.id)
        elif movement == "adjustment":
            stock = await self.adjust_stock(
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
                sku=payload.article_id,
                lot_id=payload.lot_id,
                lot_number=payload.lot_number,
                quantity=payload.quantity,
                reference=payload.reference_number,
            )
            transaction = await self._latest_transaction_for_item(stock.id)
        else:
            raise ValueError(f"Unsupported movement type: {payload.movement_type}")

        if transaction is None:
            raise ValueError("Could not create stock movement")

        stock_item = await self._session.get(models.StockItem, transaction.stock_item_id)
        return self._map_transaction(transaction, stock_item)

    async def issue_stock(
        self,
        *,
        warehouse_id: UUID,
        location_id: UUID | None,
        sku: str,
        lot_id: UUID | None,
        lot_number: str | None,
        quantity: float,
        reference: str | None = None,
    ) -> StockItemRead:
        stock_item = await self._find_stock_item(
            warehouse_id=warehouse_id,
            location_id=location_id,
            sku=sku,
            lot_id=lot_id,
            lot_number=lot_number,
        )
        if not stock_item:
            raise ValueError("Stock item not found for issue")
        if float(stock_item.quantity) < quantity:
            raise ValueError("Insufficient quantity for issue")

        stock_item.quantity = float(stock_item.quantity) - quantity

        txn = models.InventoryTransaction(
            stock_item_id=stock_item.id,
            transaction_type=models.InventoryTransactionType.ADJUSTMENT,
            quantity=quantity,
            reference=reference,
            from_location_id=stock_item.location_id,
        )
        self._session.add(txn)
        await self._session.flush()
        await self._publish_event(
            event_type="inventory.stock.issued",
            aggregate_id=str(stock_item.id),
            aggregate_type="inventory.stock_item",
            data={
                "stockItemId": str(stock_item.id),
                "warehouseId": str(stock_item.warehouse_id),
                "locationId": str(stock_item.location_id),
                "lotId": str(stock_item.lot_id),
                "sku": sku,
                "quantity": quantity,
                "reference": reference,
            },
        )
        return await self._serialize_stock_item(stock_item)

    async def adjust_stock(
        self,
        *,
        warehouse_id: UUID,
        location_id: UUID | None,
        sku: str,
        lot_id: UUID | None,
        lot_number: str | None,
        quantity: float,
        reference: str | None = None,
    ) -> StockItemRead:
        stock_item = await self._find_stock_item(
            warehouse_id=warehouse_id,
            location_id=location_id,
            sku=sku,
            lot_id=lot_id,
            lot_number=lot_number,
        )
        if not stock_item:
            raise ValueError("Stock item not found for adjustment")
        stock_item.quantity = max(float(stock_item.quantity) - quantity, 0)

        txn = models.InventoryTransaction(
            stock_item_id=stock_item.id,
            transaction_type=models.InventoryTransactionType.ADJUSTMENT,
            quantity=quantity,
            reference=reference or "inventory.adjustment",
            from_location_id=stock_item.location_id,
        )
        self._session.add(txn)
        await self._session.flush()
        await self._publish_event(
            event_type="inventory.stock.adjusted",
            aggregate_id=str(stock_item.id),
            aggregate_type="inventory.stock_item",
            data={
                "stockItemId": str(stock_item.id),
                "warehouseId": str(stock_item.warehouse_id),
                "locationId": str(stock_item.location_id),
                "lotId": str(stock_item.lot_id),
                "sku": sku,
                "quantity": quantity,
                "reference": reference,
            },
        )
        return await self._serialize_stock_item(stock_item)

    async def _latest_transaction_for_item(self, stock_item_id: UUID) -> models.InventoryTransaction | None:
        stmt = (
            select(models.InventoryTransaction)
            .where(models.InventoryTransaction.stock_item_id == stock_item_id)
            .order_by(models.InventoryTransaction.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    def _map_transaction(
        self,
        txn: models.InventoryTransaction,
        stock_item: models.StockItem,
    ) -> StockMovementRecord:
        movement_type = txn.transaction_type.value
        return StockMovementRecord(
            id=txn.id,
            movement_type=movement_type,
            quantity=float(txn.quantity),
            reference=txn.reference,
            warehouse_id=stock_item.warehouse_id,
            location_id=txn.to_location_id or txn.from_location_id,
            lot_id=stock_item.lot_id,
            created_at=txn.created_at,
        )

    async def _get_or_create_lot(self, payload: ReceiptCreate) -> models.Lot:
        query = select(models.Lot).where(models.Lot.sku == payload.sku, models.Lot.lot_number == payload.lot_number)
        lot = (await self._session.execute(query)).scalar_one_or_none()
        if lot:
            return lot
        lot = models.Lot(
            sku=payload.sku,
            lot_number=payload.lot_number,
            production_date=payload.production_date,
            expiry_date=payload.expiry_date,
        )
        self._session.add(lot)
        await self._session.flush()
        return lot

    async def _get_or_create_stock_item(self, warehouse_id: UUID, location_id: UUID, lot_id: UUID) -> models.StockItem:
        query = (
            select(models.StockItem)
            .where(
                models.StockItem.warehouse_id == warehouse_id,
                models.StockItem.location_id == location_id,
                models.StockItem.lot_id == lot_id,
            )
            .options(selectinload(models.StockItem.lot))
        )
        stock_item = (await self._session.execute(query)).scalar_one_or_none()
        if stock_item:
            return stock_item
        stock_item = models.StockItem(
            warehouse_id=warehouse_id,
            location_id=location_id,
            lot_id=lot_id,
            quantity=0,
            reserved_quantity=0,
        )
        self._session.add(stock_item)
        await self._session.flush()
        return stock_item

    async def _find_stock_item(
        self,
        *,
        warehouse_id: UUID,
        location_id: UUID | None,
        sku: str,
        lot_id: UUID | None,
        lot_number: str | None,
    ) -> models.StockItem | None:
        stmt = (
            select(models.StockItem)
            .join(models.Lot)
            .where(models.StockItem.warehouse_id == warehouse_id, models.Lot.sku == sku)
        )
        if location_id:
            stmt = stmt.where(models.StockItem.location_id == location_id)
        if lot_id:
            stmt = stmt.where(models.StockItem.lot_id == lot_id)
        elif lot_number:
            stmt = stmt.where(models.Lot.lot_number == lot_number)
        stmt = stmt.options(selectinload(models.StockItem.lot))
        result = await self._session.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def _serialize_stock_item(self, stock_item: models.StockItem) -> StockItemRead:
        lot = stock_item.lot
        if not lot:
            lot = await self._session.get(models.Lot, stock_item.lot_id)
        return StockItemRead(
            id=stock_item.id,
            warehouse_id=stock_item.warehouse_id,
            location_id=stock_item.location_id,
            lot_id=stock_item.lot_id,
            sku=lot.sku if lot else "",
            lot_number=lot.lot_number if lot else "",
            quantity=float(stock_item.quantity),
            reserved_quantity=float(stock_item.reserved_quantity),
        )

    async def _publish_event(
        self,
        *,
        event_type: str,
        aggregate_id: str,
        aggregate_type: str,
        data: dict[str, object],
    ) -> None:
        payload = {
            "eventId": str(uuid4()),
            "eventType": event_type,
            "aggregateId": aggregate_id,
            "aggregateType": aggregate_type,
            "eventVersion": EVENT_VERSION_DEFAULT,
            "occurredOn": datetime.utcnow().isoformat(),
            "tenantId": self._tenant_id,
            "data": data,
        }

        if self._event_bus:
            await self._event_bus.publish(event_type=event_type, tenant=self._tenant_id, data=payload)
        await emit_workflow_event(event_type=event_type, tenant=self._tenant_id, payload=payload)
