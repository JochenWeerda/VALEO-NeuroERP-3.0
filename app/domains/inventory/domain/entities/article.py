"""
Article Entity
Core business object for inventory items
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """Article domain entity."""
    
    id: str
    article_number: str
    name: str
    description: Optional[str]
    barcode: Optional[str]
    price: float
    cost_price: Optional[float]
    category: Optional[str]
    unit: str
    stock_quantity: int
    min_stock: Optional[int]
    is_active: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    def is_low_stock(self) -> bool:
        """Check if article is below minimum stock level."""
        if self.min_stock is None:
            return False
        return self.stock_quantity < self.min_stock
    
    def update_stock(self, quantity_delta: int) -> None:
        """Update stock quantity by delta (positive or negative)."""
        self.stock_quantity += quantity_delta
        self.updated_at = datetime.utcnow()
    
    def calculate_margin(self) -> Optional[float]:
        """Calculate profit margin percentage."""
        if self.cost_price is None or self.cost_price == 0:
            return None
        return ((self.price - self.cost_price) / self.cost_price) * 100

