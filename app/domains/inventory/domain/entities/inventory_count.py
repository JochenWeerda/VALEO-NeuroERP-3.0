"""
Inventory Count Entity
Manages physical inventory counting and reconciliation
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InventoryCount:
    """Inventory count domain entity."""

    id: str
    warehouse_id: str
    count_date: datetime
    counted_by: str
    status: str  # 'draft', 'completed', 'approved'
    total_items: int
    discrepancies_found: int
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    def is_completed(self) -> bool:
        """Check if count is completed."""
        return self.status == 'completed'

    def is_approved(self) -> bool:
        """Check if count is approved."""
        return self.status == 'approved'

    def has_discrepancies(self) -> bool:
        """Check if count found any discrepancies."""
        return self.discrepancies_found > 0

    def can_be_approved(self) -> bool:
        """Check if count can be approved."""
        return self.status == 'completed' and not self.is_approved()

    def mark_completed(self) -> None:
        """Mark count as completed."""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()

    def approve(self, approved_by: str) -> None:
        """Approve the inventory count."""
        if not self.can_be_approved():
            raise ValueError("Count cannot be approved in current status")

        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()