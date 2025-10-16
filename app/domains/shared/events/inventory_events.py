"""
Inventory Domain Events
Event-driven workflows for inventory management
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .base import DomainEvent


@dataclass
class StockLevelChangedEvent(DomainEvent):
    """Event fired when stock levels change."""
    article_id: str
    warehouse_id: str
    previous_stock: Decimal
    new_stock: Decimal
    change_quantity: Decimal
    movement_type: str
    reference_number: Optional[str] = None


@dataclass
class LowStockAlertEvent(DomainEvent):
    """Event fired when stock falls below minimum level."""
    article_id: str
    article_number: str
    article_name: str
    current_stock: Decimal
    min_stock: Decimal
    warehouse_id: str
    tenant_id: str


@dataclass
class StockOutEvent(DomainEvent):
    """Event fired when stock reaches zero."""
    article_id: str
    article_number: str
    article_name: str
    warehouse_id: str
    tenant_id: str


@dataclass
class ReplenishmentNeededEvent(DomainEvent):
    """Event fired when replenishment is needed."""
    article_id: str
    article_number: str
    article_name: str
    current_stock: Decimal
    min_stock: Decimal
    suggested_quantity: Decimal
    priority: int
    supplier_number: Optional[str] = None
    tenant_id: str = None


@dataclass
class InventoryCountCompletedEvent(DomainEvent):
    """Event fired when inventory count is completed."""
    count_id: str
    warehouse_id: str
    counted_by: str
    total_items: int
    discrepancies_found: int
    tenant_id: str


@dataclass
class StockMovementRecordedEvent(DomainEvent):
    """Event fired when stock movement is recorded."""
    movement_id: str
    article_id: str
    warehouse_id: str
    movement_type: str
    quantity: Decimal
    previous_stock: Decimal
    new_stock: Decimal
    reference_number: Optional[str] = None
    tenant_id: str = None