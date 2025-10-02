"""
VALEO-NeuroERP API v1 Schemas Package
Pydantic models for API request/response validation
"""

from .base import (
    BaseSchema,
    TimestampMixin,
    SoftDeleteMixin,
    PaginationParams,
    PaginatedResponse,
    APIResponse,
    ErrorResponse,
    HealthResponse,
    DatabaseHealthResponse
)

from .shared import (
    Tenant,
    TenantCreate,
    TenantUpdate,
    User,
    UserCreate,
    UserUpdate,
    UserLogin,
    TokenResponse,
    PasswordResetRequest,
    PasswordReset,
    PasswordChange
)

from .crm import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
    Lead,
    LeadCreate,
    LeadUpdate,
    Contact,
    ContactCreate,
    ContactUpdate
)

from .inventory import (
    Article,
    ArticleCreate,
    ArticleUpdate,
    Warehouse,
    WarehouseCreate,
    WarehouseUpdate,
    StockMovement,
    StockMovementCreate,
    InventoryCount,
    InventoryCountCreate
)

from .finance import (
    Account,
    AccountCreate,
    AccountUpdate,
    JournalEntry,
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryLine,
    JournalEntryLineCreate
)

__all__ = [
    # Base schemas
    "BaseSchema", "TimestampMixin", "SoftDeleteMixin",
    "PaginationParams", "PaginatedResponse", "APIResponse",
    "ErrorResponse", "HealthResponse", "DatabaseHealthResponse",

    # Shared schemas
    "Tenant", "TenantCreate", "TenantUpdate",
    "User", "UserCreate", "UserUpdate", "UserLogin", "TokenResponse",
    "PasswordResetRequest", "PasswordReset", "PasswordChange",

    # CRM schemas
    "Customer", "CustomerCreate", "CustomerUpdate",
    "Lead", "LeadCreate", "LeadUpdate",
    "Contact", "ContactCreate", "ContactUpdate",

    # Inventory schemas
    "Article", "ArticleCreate", "ArticleUpdate",
    "Warehouse", "WarehouseCreate", "WarehouseUpdate",
    "StockMovement", "StockMovementCreate",
    "InventoryCount", "InventoryCountCreate",

    # Finance schemas
    "Account", "AccountCreate", "AccountUpdate",
    "JournalEntry", "JournalEntryCreate", "JournalEntryUpdate",
    "JournalEntryLine", "JournalEntryLineCreate"
]