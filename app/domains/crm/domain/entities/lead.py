"""
Lead Entity
Potential customer tracking
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class LeadStatus(str, Enum):
    """Lead lifecycle status."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


@dataclass
class Lead:
    """Lead domain entity."""
    
    id: str
    company_name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    status: LeadStatus
    source: Optional[str]
    estimated_value: Optional[float]
    notes: Optional[str]
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    def can_convert_to_customer(self) -> bool:
        """Check if lead is ready to be converted to customer."""
        return self.status in [LeadStatus.WON, LeadStatus.QUALIFIED]
    
    def advance_status(self) -> None:
        """Advance lead to next status."""
        status_progression = {
            LeadStatus.NEW: LeadStatus.CONTACTED,
            LeadStatus.CONTACTED: LeadStatus.QUALIFIED,
            LeadStatus.QUALIFIED: LeadStatus.PROPOSAL,
            LeadStatus.PROPOSAL: LeadStatus.NEGOTIATION,
            LeadStatus.NEGOTIATION: LeadStatus.WON,
        }
        
        if self.status in status_progression:
            self.status = status_progression[self.status]
            self.updated_at = datetime.utcnow()

