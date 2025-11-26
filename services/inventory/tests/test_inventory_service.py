from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

sys.modules.pop("app", None)

from app.db import models  # noqa: E402
from app.services.inventory_service import InventoryService  # noqa: E402
from app.schemas import (  # noqa: E402
    LocationCreate,
    ReceiptCreate,
    StockMovementCreate,
    TransferCreate,
    WarehouseCreate,
)

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_receive_and_transfer(session: AsyncSession):
    service = InventoryService(session)
    warehouse = await service.create_warehouse(WarehouseCreate(code="WH1", name="Warehouse 1"))
    location_a = await service.add_location(warehouse.id, LocationCreate(code="A1"))
    location_b = await service.add_location(warehouse.id, LocationCreate(code="B1"))

    receipt = await service.receive_stock(
        ReceiptCreate(
            warehouse_id=warehouse.id,
            location_id=location_a.id,
            sku="SKU1",
            lot_number="LOT1",
            quantity=10,
            production_date=datetime.utcnow(),
        )
    )
    assert receipt.quantity == 10

    transfer_payload = TransferCreate(
        source_stock_item_id=receipt.id,
        source_location_id=location_a.id,
        source_warehouse_id=warehouse.id,
        destination_location_id=location_b.id,
        destination_warehouse_id=warehouse.id,
        lot_id=receipt.lot_id,
        quantity=5,
    )

    destination_stock = await service.transfer_stock(transfer_payload)
    assert destination_stock.quantity == 5

    trace = await service.trace_lot(receipt.lot_id)
    assert len(trace.transactions) == 2


@pytest.mark.asyncio
async def test_list_lots(session: AsyncSession):
    service = InventoryService(session)
    warehouse = await service.create_warehouse(WarehouseCreate(code="WH2", name="Warehouse 2"))
    location = await service.add_location(warehouse.id, LocationCreate(code="C1"))

    await service.receive_stock(
        ReceiptCreate(
            warehouse_id=warehouse.id,
            location_id=location.id,
            sku="SKU-TEST",
            lot_number="LOT-XYZ",
            quantity=7.5,
            production_date=datetime.utcnow(),
        )
    )

    response = await service.list_lots()
    assert response.total == 1
    assert response.items[0].lot_number == "LOT-XYZ"
    assert response.items[0].commodity == "SKU-TEST"


@pytest.mark.asyncio
async def test_stock_movement_api(session: AsyncSession):
    service = InventoryService(session)
    warehouse = await service.create_warehouse(WarehouseCreate(code="WH3", name="Warehouse 3"))
    location = await service.add_location(warehouse.id, LocationCreate(code="MAIN"))

    inbound = await service.create_stock_movement(
        StockMovementCreate(
            article_id="SKU-100",
            warehouse_id=warehouse.id,
            location_id=location.id,
            movement_type="in",
            quantity=20,
            lot_number="LOT-100",
        )
    )
    assert inbound.movement_type == "receipt"

    outbound = await service.create_stock_movement(
        StockMovementCreate(
            article_id="SKU-100",
            warehouse_id=warehouse.id,
            location_id=location.id,
            movement_type="out",
            quantity=5,
            lot_number="LOT-100",
        )
    )
    assert outbound.movement_type == "adjustment"

    articles = await service.list_articles()
    assert len(articles) == 1
    assert articles[0].current_stock == 15
