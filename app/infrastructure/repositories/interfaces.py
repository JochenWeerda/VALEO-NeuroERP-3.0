"""
Repository Interfaces for VALEO-NeuroERP
Abstract interfaces defining repository contracts
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')
TCreate = TypeVar('TCreate')
TUpdate = TypeVar('TUpdate')


class BaseRepository(Generic[T, TCreate, TUpdate], ABC):
    """Base repository interface"""

    @abstractmethod
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        """Get entity by ID"""

    @abstractmethod
    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs) -> List[T]:
        """Get all entities with pagination and optional filtering"""

    @abstractmethod
    async def create(self, data: TCreate, tenant_id: str) -> T:
        """Create a new entity"""

    @abstractmethod
    async def update(self, id: str, data: TUpdate, tenant_id: str) -> Optional[T]:
        """Update an existing entity"""

    @abstractmethod
    async def delete(self, id: str, tenant_id: str) -> bool:
        """Delete an entity (soft delete)"""

    @abstractmethod
    async def exists(self, id: str, tenant_id: str) -> bool:
        """Check if entity exists"""

    @abstractmethod
    async def count(self, tenant_id: str, **kwargs) -> int:
        """Count entities for tenant with optional filtering"""


# Shared Repository Interfaces
class TenantRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Tenant repository interface"""


class UserRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """User repository interface"""

    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: str) -> Optional[T]:
        """Get user by username"""

    @abstractmethod
    async def get_by_email(self, email: str, tenant_id: str) -> Optional[T]:
        """Get user by email"""

    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[T]:
        """Authenticate user"""

    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: str) -> Optional[T]:  # noqa: F811
        """Get user by username"""

    @abstractmethod
    async def change_password(self, user_id: str, new_password: str, tenant_id: str) -> bool:
        """Change user password"""


# CRM Repository Interfaces
class CustomerRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Customer repository interface"""

    @abstractmethod
    async def get_by_customer_number(self, customer_number: str, tenant_id: str) -> Optional[T]:
        """Get customer by customer number"""


class LeadRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Lead repository interface"""

    @abstractmethod
    async def convert_to_customer(self, lead_id: str, customer_id: str, tenant_id: str) -> bool:
        """Convert lead to customer"""


class ContactRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Contact repository interface"""


class ActivityRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Activity repository interface"""


class FarmProfileRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Farm profile repository interface"""


# Inventory Repository Interfaces
class ArticleRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Article repository interface"""

    @abstractmethod
    async def get_by_barcode(self, barcode: str, tenant_id: str) -> Optional[T]:
        """Get article by barcode"""

    @abstractmethod
    async def update_stock(self, article_id: str, quantity_change: float, tenant_id: str) -> bool:
        """Update article stock level"""


class WarehouseRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Warehouse repository interface"""


class StockMovementRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Stock movement repository interface"""


class InventoryCountRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Inventory count repository interface"""


# Finance Repository Interfaces
class AccountRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Account repository interface"""

    @abstractmethod
    async def get_by_number(self, account_number: str, tenant_id: str) -> Optional[T]:
        """Get account by account number"""

    @abstractmethod
    async def get_balance(self, account_id: str, tenant_id: str) -> float:
        """Get current account balance"""

    @abstractmethod
    async def update_balance(self, account_id: str, amount: float, tenant_id: str) -> bool:
        """Update account balance"""


class JournalEntryRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Journal entry repository interface"""

    @abstractmethod
    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        """Post a journal entry"""

    @abstractmethod
    async def get_entries_by_date_range(
        self, start_date: str, end_date: str, tenant_id: str, reference: Optional[str] = None
    ) -> List[T]:
        """Get journal entries by date range, optionally by reference (e.g. Importlauf run_id)."""

    @abstractmethod
    async def get_entries_by_account(self, account_id: str, tenant_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[T]:
        """Get journal entries for a specific account"""

    @abstractmethod
    async def reverse_entry(self, entry_id: str, reason: str, tenant_id: str) -> Optional[T]:
        """Create a reversal entry"""
