"""
Service interfaces and base classes for VALEO-NeuroERP
Clean architecture service layer definitions
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, TypeVar, Generic
from uuid import UUID

from ...api.v1.schemas.base import PaginationParams, PaginatedResponse

T = TypeVar('T')
TCreate = TypeVar('TCreate')
TUpdate = TypeVar('TUpdate')


class BaseService(Generic[T, TCreate, TUpdate], ABC):
    """
    Base service interface following clean architecture principles.
    Provides common CRUD operations for domain entities.
    """

    @abstractmethod
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, tenant_id: str, pagination: Optional[PaginationParams] = None) -> PaginatedResponse[T]:
        """Get all entities with optional pagination."""
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


class TenantService(BaseService[Any, Any, Any], ABC):
    """Tenant management service interface."""
    pass


class UserService(BaseService[Any, Any, Any], ABC):
    """User management service interface."""

    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[Any]:
        """Authenticate user credentials."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: str) -> Optional[Any]:
        """Get user by username."""
        pass

    @abstractmethod
    async def change_password(self, user_id: str, new_password: str, tenant_id: str) -> bool:
        """Change user password."""
        pass


class CustomerService(BaseService[Any, Any, Any], ABC):
    """CRM customer service interface."""
    pass


class LeadService(BaseService[Any, Any, Any], ABC):
    """CRM lead service interface."""

    @abstractmethod
    async def convert_to_customer(self, lead_id: str, customer_data: Any, tenant_id: str) -> Optional[Any]:
        """Convert lead to customer."""
        pass


class ContactService(BaseService[Any, Any, Any], ABC):
    """CRM contact service interface."""
    pass


class ArticleService(BaseService[Any, Any, Any], ABC):
    """Inventory article service interface."""

    @abstractmethod
    async def get_by_barcode(self, barcode: str, tenant_id: str) -> Optional[Any]:
        """Get article by barcode."""
        pass

    @abstractmethod
    async def update_stock(self, article_id: str, quantity_change: float, tenant_id: str) -> bool:
        """Update article stock level."""
        pass


class WarehouseService(BaseService[Any, Any, Any], ABC):
    """Inventory warehouse service interface."""
    pass


class StockMovementService(BaseService[Any, Any, Any], ABC):
    """Inventory stock movement service interface."""

    @abstractmethod
    async def move_stock(self, article_id: str, from_warehouse_id: str,
                        to_warehouse_id: str, quantity: float, tenant_id: str) -> Optional[Any]:
        """Move stock between warehouses."""
        pass


class InventoryCountService(BaseService[Any, Any, Any], ABC):
    """Inventory count service interface."""

    @abstractmethod
    async def start_count(self, warehouse_id: str, counted_by: str, tenant_id: str) -> Any:
        """Start a new inventory count."""
        pass

    @abstractmethod
    async def complete_count(self, count_id: str, tenant_id: str) -> bool:
        """Complete an inventory count."""
        pass


class AccountService(BaseService[Any, Any, Any], ABC):
    """Finance account service interface."""

    @abstractmethod
    async def get_by_number(self, account_number: str, tenant_id: str) -> Optional[Any]:
        """Get account by account number."""
        pass

    @abstractmethod
    async def get_balance(self, account_id: str, tenant_id: str) -> float:
        """Get current account balance."""
        pass


class JournalEntryService(BaseService[Any, Any, Any], ABC):
    """Finance journal entry service interface."""

    @abstractmethod
    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        """Post a journal entry."""
        pass

    @abstractmethod
    async def reverse_entry(self, entry_id: str, reason: str, tenant_id: str) -> Optional[Any]:
        """Reverse a journal entry."""
        pass

    @abstractmethod
    async def get_trial_balance(self, start_date: str, end_date: str, tenant_id: str) -> Any:
        """Generate trial balance report."""
        pass


class EmailService(ABC):
    """Email service interface."""

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """Send email message."""
        pass

    @abstractmethod
    async def send_template_email(self, to: str, template: str, context: dict) -> bool:
        """Send templated email."""
        pass


class NotificationService(ABC):
    """Notification service interface."""

    @abstractmethod
    async def send_notification(self, user_id: str, title: str, message: str, type: str = "info") -> bool:
        """Send user notification."""
        pass

    @abstractmethod
    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Any]:
        """Get user notifications."""
        pass


class AuditService(ABC):
    """Audit logging service interface."""

    @abstractmethod
    async def log_action(self, user_id: str, action: str, resource: str,
                        resource_id: str, details: Optional[dict] = None, tenant_id: str = None) -> None:
        """Log user action for audit trail."""
        pass

    @abstractmethod
    async def get_audit_log(self, resource: str, resource_id: str, tenant_id: str) -> List[Any]:
        """Get audit log for a resource."""
        pass