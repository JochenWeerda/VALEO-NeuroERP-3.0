"""
Journal Entry Entity
Double-entry bookkeeping transaction
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional


@dataclass
class JournalEntryLine:
    """Single line in a journal entry."""
    account_id: str
    account_number: str
    description: str
    debit: float
    credit: float


@dataclass
class JournalEntry:
    """Journal entry domain entity."""
    
    id: str
    entry_number: str
    entry_date: date
    description: str
    lines: List[JournalEntryLine]
    total_debit: float
    total_credit: float
    is_posted: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    def is_balanced(self) -> bool:
        """Check if debit equals credit (double-entry rule)."""
        return abs(self.total_debit - self.total_credit) < 0.01
    
    def can_post(self) -> bool:
        """Check if entry is ready to be posted."""
        return not self.is_posted and self.is_balanced() and len(self.lines) >= 2
    
    def post(self) -> None:
        """Post the journal entry (make it permanent)."""
        if not self.can_post():
            raise ValueError("Journal entry cannot be posted (not balanced or already posted)")
        self.is_posted = True
        self.updated_at = datetime.utcnow()

