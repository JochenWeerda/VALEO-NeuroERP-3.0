"""
Warehouse Entity
Physical location for inventory storage
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Warehouse:
    """Warehouse domain entity."""
    
    id: str
    code: str
    name: str
    address: Optional[str]
    capacity: Optional[int]
    is_active: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    def is_at_capacity(self, current_items: int) -> bool:
        """Check if warehouse is at or over capacity."""
        if self.capacity is None:
            return False
        return current_items >= self.capacity

