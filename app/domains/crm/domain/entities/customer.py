"""
Customer Entity
Core business object for customer management
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """Customer domain entity."""
    
    id: str
    customer_number: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    tax_id: Optional[str]
    credit_limit: Optional[float]
    payment_terms: int  # Days
    is_active: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    def is_credit_available(self, current_balance: float) -> bool:
        """Check if customer has available credit."""
        if self.credit_limit is None:
            return True
        return current_balance < self.credit_limit
    
    def is_payment_overdue(self, invoice_date: datetime, current_date: datetime) -> bool:
        """Check if payment is overdue based on payment terms."""
        days_elapsed = (current_date - invoice_date).days
        return days_elapsed > self.payment_terms

