"""
Stock Movement Entity
Tracks inventory movements and transactions
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class StockMovement:
    """Stock movement domain entity."""

    id: str
    article_id: str
    warehouse_id: str
    movement_type: str  # 'in', 'out', 'transfer', 'adjustment'
    quantity: Decimal
    unit_cost: Optional[Decimal]
    reference_number: Optional[str]
    notes: Optional[str]
    previous_stock: Decimal
    new_stock: Decimal
    total_cost: Optional[Decimal]
    tenant_id: str
    created_at: datetime

    def is_inbound(self) -> bool:
        """Check if movement is inbound (increasing stock)."""
        return self.movement_type in ['in', 'transfer'] and self.quantity > 0

    def is_outbound(self) -> bool:
        """Check if movement is outbound (decreasing stock)."""
        return self.movement_type in ['out', 'transfer'] and self.quantity < 0

    def get_movement_value(self) -> Optional[Decimal]:
        """Calculate total value of the movement."""
        if self.unit_cost is None:
            return None
        return abs(self.quantity) * self.unit_cost

    def affects_inventory_value(self) -> bool:
        """Check if this movement affects inventory valuation."""
        return self.movement_type in ['in', 'adjustment'] and self.unit_cost is not None