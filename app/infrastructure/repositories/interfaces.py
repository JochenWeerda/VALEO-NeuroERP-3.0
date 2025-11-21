"""
Repository Interfaces for VALEO-NeuroERP
Abstract interfaces defining repository contracts
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')
TCreate = TypeVar('TCreate')
TUpdate = TypeVar('TUpdate')


class BaseRepository(Generic[T, TCreate, TUpdate], ABC):
    """Base repository interface"""

    @abstractmethod
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        """Get entity by ID"""
        pass

    @abstractmethod
    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs) -> List[T]:
        """Get all entities with pagination and optional filtering"""
        pass

    @abstractmethod
    async def create(self, data: TCreate, tenant_id: str) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    async def update(self, id: str, data: TUpdate, tenant_id: str) -> Optional[T]:
        """Update an existing entity"""
        pass

    @abstractmethod
    async def delete(self, id: str, tenant_id: str) -> bool:
        """Delete an entity (soft delete)"""
        pass

    @abstractmethod
    async def exists(self, id: str, tenant_id: str) -> bool:
        """Check if entity exists"""
        pass

    @abstractmethod
    async def count(self, tenant_id: str, **kwargs) -> int:
        """Count entities for tenant with optional filtering"""
        pass


# Shared Repository Interfaces
class TenantRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Tenant repository interface"""
    pass


class UserRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """User repository interface"""

    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: str) -> Optional[T]:
        """Get user by username"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str, tenant_id: str) -> Optional[T]:
        """Get user by email"""
        pass

    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[T]:
        """Authenticate user"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: str) -> Optional[T]:
        """Get user by username"""
        pass

    @abstractmethod
    async def change_password(self, user_id: str, new_password: str, tenant_id: str) -> bool:
        """Change user password"""
        pass


# CRM Repository Interfaces
class CustomerRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Customer repository interface"""

    @abstractmethod
    async def get_by_customer_number(self, customer_number: str, tenant_id: str) -> Optional[T]:
        """Get customer by customer number"""
        pass


class LeadRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Lead repository interface"""

    @abstractmethod
    async def convert_to_customer(self, lead_id: str, customer_id: str, tenant_id: str) -> bool:
        """Convert lead to customer"""
        pass


class ContactRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Contact repository interface"""
    pass


class ActivityRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Activity repository interface"""
    pass


class FarmProfileRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Farm profile repository interface"""
    pass


# Inventory Repository Interfaces
class ArticleRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Article repository interface"""

    @abstractmethod
    async def get_by_barcode(self, barcode: str, tenant_id: str) -> Optional[T]:
        """Get article by barcode"""
        pass

    @abstractmethod
    async def update_stock(self, article_id: str, quantity_change: float, tenant_id: str) -> bool:
        """Update article stock level"""
        pass


class WarehouseRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Warehouse repository interface"""
    pass


class StockMovementRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Stock movement repository interface"""
    pass


class InventoryCountRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Inventory count repository interface"""
    pass


# Finance Repository Interfaces
class AccountRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Account repository interface"""

    @abstractmethod
    async def get_by_number(self, account_number: str, tenant_id: str) -> Optional[T]:
        """Get account by account number"""
        pass

    @abstractmethod
    async def get_balance(self, account_id: str, tenant_id: str) -> float:
        """Get current account balance"""
        pass

    @abstractmethod
    async def update_balance(self, account_id: str, amount: float, tenant_id: str) -> bool:
        """Update account balance"""
        pass


class JournalEntryRepository(BaseRepository[T, TCreate, TUpdate], ABC):
    """Journal entry repository interface"""

    @abstractmethod
    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        """Post a journal entry"""
        pass

    @abstractmethod
    async def get_entries_by_date_range(self, start_date: str, end_date: str, tenant_id: str) -> List[T]:
        """Get journal entries by date range"""
        pass

    @abstractmethod
    async def get_entries_by_account(self, account_id: str, tenant_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[T]:
        """Get journal entries for a specific account"""
        pass

    @abstractmethod
    async def reverse_entry(self, entry_id: str, reason: str, tenant_id: str) -> Optional[T]:
        """Create a reversal entry"""
        pass
