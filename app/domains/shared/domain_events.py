"""
Domain Events Definitions
Concrete events for each domain
"""

from dataclasses import dataclass
from datetime import datetime
from .events import DomainEvent


# Inventory Events
@dataclass
class ArticleCreated(DomainEvent):
    """Fired when a new article is created."""
    aggregate_id: str  # Article ID
    timestamp: datetime
    article_number: str
    name: str
    price: float
    tenant_id: str


@dataclass
class StockUpdated(DomainEvent):
    """Fired when article stock quantity changes."""
    aggregate_id: str  # Article ID
    timestamp: datetime
    article_number: str
    old_quantity: int
    new_quantity: int
    delta: int
    warehouse_id: str
    tenant_id: str


@dataclass
class LowStockDetected(DomainEvent):
    """Fired when article stock falls below minimum."""
    aggregate_id: str  # Article ID
    timestamp: datetime
    article_number: str
    name: str
    current_stock: int
    min_stock: int
    tenant_id: str


# CRM Events
@dataclass
class CustomerCreated(DomainEvent):
    """Fired when a new customer is created."""
    aggregate_id: str  # Customer ID
    timestamp: datetime
    customer_number: str
    name: str
    email: str | None
    tenant_id: str


@dataclass
class LeadConverted(DomainEvent):
    """Fired when a lead is converted to customer."""
    aggregate_id: str  # Lead ID
    timestamp: datetime
    lead_id: str
    customer_id: str
    company_name: str
    tenant_id: str


@dataclass
class LeadStatusChanged(DomainEvent):
    """Fired when lead status changes."""
    aggregate_id: str  # Lead ID
    timestamp: datetime
    lead_id: str
    old_status: str
    new_status: str
    tenant_id: str


# Finance Events
@dataclass
class JournalEntryPosted(DomainEvent):
    """Fired when journal entry is posted."""
    aggregate_id: str  # Journal Entry ID
    timestamp: datetime
    entry_number: str
    entry_date: str
    total_debit: float
    total_credit: float
    tenant_id: str


@dataclass
class AccountBalanceChanged(DomainEvent):
    """Fired when account balance changes."""
    aggregate_id: str  # Account ID
    timestamp: datetime
    account_number: str
    old_balance: float
    new_balance: float
    delta: float
    tenant_id: str

