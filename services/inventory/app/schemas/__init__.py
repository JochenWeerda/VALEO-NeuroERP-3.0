"""Pydantic Schemas für Inventory Service."""

from .warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from .location import LocationCreate, LocationRead
from .inventory import (
    LotListItem,
    LotListResponse,
    LotTraceResponse,
    ReceiptCreate,
    StockItemRead,
    TransactionRecord,
    TransferCreate,
)
from .articles import ArticleSummary, StockMovementCreate, StockMovementRecord
from .epcis import EpcisEventCreate, EpcisEventRead, EpcisEventsResponse

__all__ = [
    "WarehouseCreate",
    "WarehouseRead",
    "WarehouseUpdate",
    "LocationCreate",
    "LocationRead",
    "ReceiptCreate",
    "TransferCreate",
    "StockItemRead",
    "TransactionRecord",
    "LotTraceResponse",
    "LotListItem",
    "LotListResponse",
    "ArticleSummary",
    "StockMovementCreate",
    "StockMovementRecord",
    "EpcisEventCreate",
    "EpcisEventRead",
    "EpcisEventsResponse",
]
