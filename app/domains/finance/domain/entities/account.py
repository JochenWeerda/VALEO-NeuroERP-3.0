"""
Account Entity
Chart of accounts entry
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class AccountType(str, Enum):
    """Account types following SKR03."""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


@dataclass
class Account:
    """Account domain entity."""
    
    id: str
    account_number: str
    name: str
    account_type: AccountType
    balance: float
    parent_account_id: Optional[str]
    is_active: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    def is_debit_account(self) -> bool:
        """Check if account has normal debit balance."""
        return self.account_type in [AccountType.ASSET, AccountType.EXPENSE]
    
    def is_credit_account(self) -> bool:
        """Check if account has normal credit balance."""
        return self.account_type in [AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE]
    
    def update_balance(self, amount: float) -> None:
        """Update account balance."""
        self.balance += amount
        self.updated_at = datetime.utcnow()

