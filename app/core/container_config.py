"""
Dependency Injection Container Configuration
Wires up all services, repositories, and dependencies for VALEO-NeuroERP
"""

import logging
from .dependency_container import container
from .database import get_db, SessionLocal
from ..infrastructure.repositories import (
    TenantRepository, UserRepository, CustomerRepository,
    LeadRepository, ContactRepository, ArticleRepository,
    WarehouseRepository, StockMovementRepository, InventoryCountRepository,
    AccountRepository, JournalEntryRepository
)
from ..infrastructure.repositories.implementations import (
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
from ..repositories.document_repository import DocumentRepository
from ..finance.repositories import OffenerPostenRepository, BuchungRepository, KontoRepository, AnlageRepository
from .services import (
    TenantService, UserService, CustomerService, LeadService, ContactService,
    ArticleService, WarehouseService, StockMovementService, InventoryCountService,
    AccountService, JournalEntryService, EmailService, NotificationService, AuditService
)
from .production_service_implementations import (
    ProductionTenantService, ProductionUserService, ProductionCustomerService
)
from .production_enhanced_services import (
    ProductionEmailService, ProductionNotificationService, ProductionAuditService
)

logger = logging.getLogger(__name__)


def configure_container():
    """
    Configure the dependency injection container with all services and repositories.
    This function sets up the entire service layer for clean architecture.
    """

    # Database session factory
    def get_db_session_factory():
        """Factory for database sessions with improved error handling."""
        try:
            from sqlalchemy.orm import sessionmaker
            from .database import SessionLocal
            logger.debug("Creating database session factory")
            return SessionLocal()
        except Exception as e:
            logger.error(f"Failed to create database session: {e}")
            raise

    container.register_factory(type(SessionLocal()), get_db_session_factory)

    # Register repository implementations
    def create_tenant_repository():
        return TenantRepositoryImpl(SessionLocal())

    def create_user_repository():
        return UserRepositoryImpl(SessionLocal())

    def create_customer_repository():
        return CustomerRepositoryImpl(SessionLocal())

    def create_lead_repository():
        return LeadRepositoryImpl(SessionLocal())

    def create_contact_repository():
        return ContactRepositoryImpl(SessionLocal())

    def create_article_repository():
        return ArticleRepositoryImpl(SessionLocal())

    def create_warehouse_repository():
        return WarehouseRepositoryImpl(SessionLocal())

    def create_stock_movement_repository():
        return StockMovementRepositoryImpl(SessionLocal())

    def create_inventory_count_repository():
        return InventoryCountRepositoryImpl(SessionLocal())

    def create_account_repository():
        return AccountRepositoryImpl(SessionLocal())

    def create_journal_entry_repository():
        return JournalEntryRepositoryImpl(SessionLocal())

    def create_document_repository():
        return DocumentRepository(SessionLocal())

    # Register repositories
    container.register_factory(TenantRepository, create_tenant_repository)
    container.register_factory(UserRepository, create_user_repository)
    container.register_factory(CustomerRepository, create_customer_repository)
    container.register_factory(LeadRepository, create_lead_repository)
    container.register_factory(ContactRepository, create_contact_repository)
    container.register_factory(ArticleRepository, create_article_repository)
    container.register_factory(WarehouseRepository, create_warehouse_repository)
    container.register_factory(StockMovementRepository, create_stock_movement_repository)
    container.register_factory(InventoryCountRepository, create_inventory_count_repository)
    container.register_factory(AccountRepository, create_account_repository)
    container.register_factory(JournalEntryRepository, create_journal_entry_repository)
    container.register_factory(DocumentRepository, create_document_repository)

    # Finance repositories
    def create_offener_posten_repository():
        return OffenerPostenRepository(SessionLocal())

    def create_buchung_repository():
        return BuchungRepository(SessionLocal())

    def create_konto_repository():
        return KontoRepository(SessionLocal())

    def create_anlage_repository():
        return AnlageRepository(SessionLocal())

    container.register_factory(OffenerPostenRepository, create_offener_posten_repository)
    container.register_factory(BuchungRepository, create_buchung_repository)
    container.register_factory(KontoRepository, create_konto_repository)
    container.register_factory(AnlageRepository, create_anlage_repository)

    # Infrastructure Services (Singletons)
    # These would be implemented as concrete classes in the infrastructure layer

    # Domain Services
    # These will be registered when we implement the concrete service classes
    # For now, we'll register placeholder implementations

    class PlaceholderTenantService(TenantService):
        async def get_by_id(self, id: str, tenant_id: str):
            logger.warning("PlaceholderTenantService.get_by_id called")
            return None
        async def get_all(self, tenant_id: str, pagination=None):
            logger.warning("PlaceholderTenantService.get_all called")
            return []
        async def create(self, data, tenant_id: str):
            logger.warning("PlaceholderTenantService.create called")
            return None
        async def update(self, id: str, data, tenant_id: str):
            logger.warning("PlaceholderTenantService.update called")
            return None
        async def delete(self, id: str, tenant_id: str):
            logger.warning("PlaceholderTenantService.delete called")
            return False
        async def exists(self, id: str, tenant_id: str):
            logger.warning("PlaceholderTenantService.exists called")
            return False

    class PlaceholderUserService(UserService):
        async def get_by_id(self, id: str, tenant_id: str):
            logger.warning("PlaceholderUserService.get_by_id called")
            return None
        async def get_all(self, tenant_id: str, pagination=None):
            logger.warning("PlaceholderUserService.get_all called")
            return []
        async def create(self, data, tenant_id: str):
            logger.warning("PlaceholderUserService.create called")
            return None
        async def update(self, id: str, data, tenant_id: str):
            logger.warning("PlaceholderUserService.update called")
            return None
        async def delete(self, id: str, tenant_id: str):
            logger.warning("PlaceholderUserService.delete called")
            return False
        async def exists(self, id: str, tenant_id: str):
            logger.warning("PlaceholderUserService.exists called")
            return False
        async def authenticate(self, username: str, password: str):
            logger.warning("PlaceholderUserService.authenticate called")
            return None
        async def get_by_username(self, username: str, tenant_id: str):
            logger.warning("PlaceholderUserService.get_by_username called")
            return None
        async def change_password(self, user_id: str, new_password: str, tenant_id: str):
            logger.warning("PlaceholderUserService.change_password called")
            return False

    # Register production services (replacing placeholders)
    def create_tenant_service():
        return ProductionTenantService(SessionLocal)

    def create_user_service():
        return ProductionUserService(SessionLocal)

    def create_customer_service():
        return ProductionCustomerService(SessionLocal)

    container.register_factory(TenantService, create_tenant_service)
    container.register_factory(UserService, create_user_service)
    container.register_factory(CustomerService, create_customer_service)

    # Register other services as placeholders for now
    # These will be replaced with actual implementations as we build them

    class PlaceholderService:
        async def get_by_id(self, id: str, tenant_id: str):
            logger.warning(f"PlaceholderService.get_by_id called for {self.__class__.__name__}")
            return None
        async def get_all(self, tenant_id: str, pagination=None):
            logger.warning(f"PlaceholderService.get_all called for {self.__class__.__name__}")
            return []
        async def create(self, data, tenant_id: str):
            logger.warning(f"PlaceholderService.create called for {self.__class__.__name__}")
            return None
        async def update(self, id: str, data, tenant_id: str):
            logger.warning(f"PlaceholderService.update called for {self.__class__.__name__}")
            return None
        async def delete(self, id: str, tenant_id: str):
            logger.warning(f"PlaceholderService.delete called for {self.__class__.__name__}")
            return False
        async def exists(self, id: str, tenant_id: str):
            logger.warning(f"PlaceholderService.exists called for {self.__class__.__name__}")
            return False

    # Create placeholder classes for each service
    PlaceholderCustomerService = type('PlaceholderCustomerService', (PlaceholderService, CustomerService), {})
    PlaceholderLeadService = type('PlaceholderLeadService', (PlaceholderService, LeadService), {})
    PlaceholderContactService = type('PlaceholderContactService', (PlaceholderService, ContactService), {})
    PlaceholderArticleService = type('PlaceholderArticleService', (PlaceholderService, ArticleService), {})
    PlaceholderWarehouseService = type('PlaceholderWarehouseService', (PlaceholderService, WarehouseService), {})
    PlaceholderStockMovementService = type('PlaceholderStockMovementService', (PlaceholderService, StockMovementService), {})
    PlaceholderInventoryCountService = type('PlaceholderInventoryCountService', (PlaceholderService, InventoryCountService), {})
    PlaceholderAccountService = type('PlaceholderAccountService', (PlaceholderService, AccountService), {})
    PlaceholderJournalEntryService = type('PlaceholderJournalEntryService', (PlaceholderService, JournalEntryService), {})

    # Register all placeholder services
    # CustomerService now uses ProductionCustomerService (already registered above)
    # container.register(CustomerService, PlaceholderCustomerService)  # Replaced with ProductionCustomerService
    container.register(LeadService, PlaceholderLeadService)
    container.register(ContactService, PlaceholderContactService)
    container.register(ArticleService, PlaceholderArticleService)
    container.register(WarehouseService, PlaceholderWarehouseService)
    container.register(StockMovementService, PlaceholderStockMovementService)
    container.register(InventoryCountService, PlaceholderInventoryCountService)
    container.register(AccountService, PlaceholderAccountService)
    container.register(JournalEntryService, PlaceholderJournalEntryService)

    # Infrastructure services (email, notifications, audit)
    class PlaceholderEmailService(EmailService):
        async def send_email(self, to: str, subject: str, body: str, html=None):
            logger.warning("PlaceholderEmailService.send_email called")
            return True
        async def send_template_email(self, to: str, template: str, context: dict):
            logger.warning("PlaceholderEmailService.send_template_email called")
            return True

    class PlaceholderNotificationService(NotificationService):
        async def send_notification(self, user_id: str, title: str, message: str, type: str = "info"):
            logger.warning("PlaceholderNotificationService.send_notification called")
            return True
        async def get_user_notifications(self, user_id: str, unread_only: bool = False):
            logger.warning("PlaceholderNotificationService.get_user_notifications called")
            return []

    class PlaceholderAuditService(AuditService):
        async def log_action(self, user_id: str, action: str, resource: str,
                           resource_id: str, details=None, tenant_id=None):
            logger.warning("PlaceholderAuditService.log_action called")
        async def get_audit_log(self, resource: str, resource_id: str, tenant_id: str):
            logger.warning("PlaceholderAuditService.get_audit_log called")
            return []

    # Register enhanced production services for infrastructure
    container.register(EmailService, ProductionEmailService)
    container.register(NotificationService, ProductionNotificationService)
    container.register(AuditService, ProductionAuditService)

    logger.info("Dependency injection container configured with all services")


# Initialize container on import
configure_container()
