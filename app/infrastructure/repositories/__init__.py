"""
Repository package aggregator for VALEO-NeuroERP.
Exposes the repository contracts and their default SQLAlchemy implementations.
"""

from .interfaces import (
    BaseRepository,
    TenantRepository,
    UserRepository,
    CustomerRepository,
    LeadRepository,
    ContactRepository,
    ArticleRepository,
    WarehouseRepository,
    StockMovementRepository,
    InventoryCountRepository,
    AccountRepository,
    JournalEntryRepository,
)
from .base_repository import BaseRepositoryImpl
from .implementations import (
    TenantRepositoryImpl,
    UserRepositoryImpl,
    CustomerRepositoryImpl,
    LeadRepositoryImpl,
    ContactRepositoryImpl,
    ArticleRepositoryImpl,
    WarehouseRepositoryImpl,
    StockMovementRepositoryImpl,
    InventoryCountRepositoryImpl,
    AccountRepositoryImpl,
    JournalEntryRepositoryImpl,
)

__all__ = [
    # Interfaces
    "BaseRepository",
    "TenantRepository",
    "UserRepository",
    "CustomerRepository",
    "LeadRepository",
    "ContactRepository",
    "ArticleRepository",
    "WarehouseRepository",
    "StockMovementRepository",
    "InventoryCountRepository",
    "AccountRepository",
    "JournalEntryRepository",
    # Implementations
    "BaseRepositoryImpl",
    "TenantRepositoryImpl",
    "UserRepositoryImpl",
    "CustomerRepositoryImpl",
    "LeadRepositoryImpl",
    "ContactRepositoryImpl",
    "ArticleRepositoryImpl",
    "WarehouseRepositoryImpl",
    "StockMovementRepositoryImpl",
    "InventoryCountRepositoryImpl",
    "AccountRepositoryImpl",
    "JournalEntryRepositoryImpl",
]
