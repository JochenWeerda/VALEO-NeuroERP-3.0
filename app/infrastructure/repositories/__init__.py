"""
Repository interfaces and implementations for VALEO-NeuroERP
Data access layer following repository pattern
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar('T')
TCreate = TypeVar('TCreate')
TUpdate = TypeVar('TUpdate')


class BaseRepository(Generic[T, TCreate, TUpdate], ABC):
    """
    Base repository interface following repository pattern.
    Provides common data access operations.
    """

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def create(self, data: TCreate, tenant_id: str) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, id: str, data: TUpdate, tenant_id: str) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: str, tenant_id: str) -> bool:
        """Soft delete an entity."""
        pass

    @abstractmethod
    async def exists(self, id: str, tenant_id: str) -> bool:
        """Check if entity exists."""
        pass

    @abstractmethod
    async def count(self, tenant_id: str) -> int:
        """Count entities for tenant."""
        pass


# Repository interfaces for each domain
class TenantRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Tenant data access interface."""
    pass


class UserRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """User data access interface."""

    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: str) -> Optional[T]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str, tenant_id: str) -> Optional[T]:
        """Get user by email."""
        pass


class CustomerRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Customer data access interface."""
    pass


class LeadRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Lead data access interface."""
    pass


class ContactRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Contact data access interface."""
    pass


class ArticleRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Article data access interface."""

    @abstractmethod
    async def get_by_barcode(self, barcode: str, tenant_id: str) -> Optional[T]:
        """Get article by barcode."""
        pass

    @abstractmethod
    async def update_stock(self, article_id: str, quantity_change: float, tenant_id: str) -> bool:
        """Update article stock level."""
        pass


class WarehouseRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Warehouse data access interface."""
    pass


class StockMovementRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Stock movement data access interface."""
    pass


class InventoryCountRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Inventory count data access interface."""
    pass


class AccountRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Account data access interface."""

    @abstractmethod
    async def get_by_number(self, account_number: str, tenant_id: str) -> Optional[T]:
        """Get account by account number."""
        pass

    @abstractmethod
    async def get_balance(self, account_id: str, tenant_id: str) -> float:
        """Get current account balance."""
        pass


class JournalEntryRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Journal entry data access interface."""

    @abstractmethod
    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        """Post a journal entry."""
        pass

    @abstractmethod
    async def get_entries_by_date_range(self, start_date: str, end_date: str, tenant_id: str) -> List[T]:
        """Get journal entries by date range."""
        pass