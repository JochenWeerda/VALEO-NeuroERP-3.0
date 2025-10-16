"""
Concrete repository implementations for VALEO-NeuroERP
SQLAlchemy-based implementations of repository interfaces
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from .base_repository import BaseRepositoryImpl
from .interfaces import (
    TenantRepository, UserRepository, CustomerRepository, LeadRepository,
    ContactRepository, ArticleRepository, WarehouseRepository,
    StockMovementRepository, InventoryCountRepository,
    AccountRepository, JournalEntryRepository
)
from ..models import (
    Tenant, User, Customer, Lead, Contact, Activity, FarmProfile, Article, Warehouse,
    StockMovement, InventoryCount, Account, JournalEntry, JournalEntryLine
)


# Shared Repositories
class TenantRepositoryImpl(BaseRepositoryImpl[Tenant, dict, dict], TenantRepository):
    """Tenant repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Tenant)


class UserRepositoryImpl(BaseRepositoryImpl[User, dict, dict], UserRepository):
    """User repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, User)

    async def get_by_username(self, username: str, tenant_id: str) -> User | None:
        """Get user by username"""
        return self.session.query(User).filter(
            and_(
                User.username == username,
                User.tenant_id == tenant_id,
                User.is_active == True
            )
        ).first()

    async def get_by_email(self, email: str, tenant_id: str) -> User | None:
        """Get user by email"""
        return self.session.query(User).filter(
            and_(
                User.email == email,
                User.tenant_id == tenant_id,
                User.is_active == True
            )
        ).first()


# CRM Repositories
class CustomerRepositoryImpl(BaseRepositoryImpl[Customer, dict, dict], CustomerRepository):
    """Customer repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Customer)


class LeadRepositoryImpl(BaseRepositoryImpl[Lead, dict, dict], LeadRepository):
    """Lead repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Lead)


class ContactRepositoryImpl(BaseRepositoryImpl[Contact, dict, dict], ContactRepository):
    """Contact repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Contact)


class ActivityRepositoryImpl(BaseRepositoryImpl[Activity, dict, dict], ContactRepository):
    """Activity repository implementation with SQLAlchemy"""
    def __init__(self, session: Session):
        super().__init__(session, Activity)
    
    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs) -> list[Activity]:
        """Get all activities with filtering"""
        query = self.session.query(Activity)
        
        # Apply filters
        if 'type' in kwargs and kwargs['type']:
            query = query.filter(Activity.type == kwargs['type'])
        if 'status' in kwargs and kwargs['status']:
            query = query.filter(Activity.status == kwargs['status'])
        
        return query.offset(skip).limit(limit).all()
    
    async def count(self, tenant_id: str, **kwargs) -> int:
        """Count activities"""
        query = self.session.query(Activity)
        
        if 'type' in kwargs and kwargs['type']:
            query = query.filter(Activity.type == kwargs['type'])
        if 'status' in kwargs and kwargs['status']:
            query = query.filter(Activity.status == kwargs['status'])
        
        return query.count()


class FarmProfileRepositoryImpl(BaseRepositoryImpl[FarmProfile, dict, dict], ContactRepository):
    """Farm profile repository implementation with SQLAlchemy"""
    def __init__(self, session: Session):
        super().__init__(session, FarmProfile)
    
    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs) -> list[FarmProfile]:
        """Get all farm profiles with filtering"""
        query = self.session.query(FarmProfile)
        
        # Apply search filter
        if 'search' in kwargs and kwargs['search']:
            search_term = f"%{kwargs['search']}%"
            query = query.filter(
                (FarmProfile.farm_name.ilike(search_term)) | 
                (FarmProfile.owner.ilike(search_term))
            )
        
        return query.offset(skip).limit(limit).all()
    
    async def count(self, tenant_id: str, **kwargs) -> int:
        """Count farm profiles"""
        query = self.session.query(FarmProfile)
        
        if 'search' in kwargs and kwargs['search']:
            search_term = f"%{kwargs['search']}%"
            query = query.filter(
                (FarmProfile.farm_name.ilike(search_term)) | 
                (FarmProfile.owner.ilike(search_term))
            )
        
        return query.count()




# Inventory Repositories
class ArticleRepositoryImpl(BaseRepositoryImpl[Article, dict, dict], ArticleRepository):
    """Article repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Article)

    async def get_by_barcode(self, barcode: str, tenant_id: str) -> Article | None:
        """Get article by barcode"""
        return self.session.query(Article).filter(
            and_(
                Article.barcode == barcode,
                Article.tenant_id == tenant_id,
                Article.is_active == True
            )
        ).first()

    async def update_stock(self, article_id: str, quantity_change: float, tenant_id: str) -> bool:
        """Update article stock level"""
        try:
            article = await self.get_by_id(article_id, tenant_id)
            if article:
                article.current_stock += quantity_change
                article.available_stock = article.current_stock - article.reserved_stock
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            return False


class WarehouseRepositoryImpl(BaseRepositoryImpl[Warehouse, dict, dict], WarehouseRepository):
    """Warehouse repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Warehouse)


class StockMovementRepositoryImpl(BaseRepositoryImpl[StockMovement, dict, dict], StockMovementRepository):
    """Stock movement repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, StockMovement)


class InventoryCountRepositoryImpl(BaseRepositoryImpl[InventoryCount, dict, dict], InventoryCountRepository):
    """Inventory count repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, InventoryCount)


# Finance Repositories
class AccountRepositoryImpl(AccountRepository):
    """Account repository implementation"""
    def __init__(self, session: Session):
        self.session = session
        self.model_class = Account

    async def get_by_id(self, id: str, tenant_id: str) -> Account | None:
        """Get entity by ID."""
        try:
            return self.session.query(Account).filter(
                and_(
                    Account.id == id,
                    Account.tenant_id == tenant_id,
                    Account.is_active == True
                )
            ).first()
        except Exception as e:
            return None

    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs) -> list[Account]:
        """Get all entities with pagination and optional filtering."""
        try:
            query = self.session.query(Account).filter(
                Account.is_active == True
            )

            if tenant_id:
                query = query.filter(Account.tenant_id == tenant_id)

            return query.offset(skip).limit(limit).all()
        except Exception as e:
            return []

    async def create(self, data: dict, tenant_id: str) -> Account:
        """Create a new entity."""
        try:
            if hasattr(data, 'model_dump'):
                data_dict = data.model_dump()
            else:
                data_dict = dict(data) if hasattr(data, '__dict__') else data

            if tenant_id:
                data_dict['tenant_id'] = tenant_id

            instance = Account(**data_dict)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except Exception as e:
            self.session.rollback()
            raise

    async def update(self, id: str, data: dict, tenant_id: str) -> Account | None:
        """Update an existing entity."""
        try:
            if hasattr(data, 'model_dump'):
                data_dict = data.model_dump(exclude_unset=True)
            else:
                data_dict = dict(data) if hasattr(data, '__dict__') else data

            query = self.session.query(Account).filter(
                Account.id == id,
                Account.is_active == True
            )

            if tenant_id:
                query = query.filter(Account.tenant_id == tenant_id)

            result = query.update(data_dict)
            self.session.commit()

            if result > 0:
                return await self.get_by_id(id, tenant_id)
            else:
                return None
        except Exception as e:
            self.session.rollback()
            raise

    async def delete(self, id: str, tenant_id: str) -> bool:
        """Soft delete an entity."""
        try:
            query = self.session.query(Account).filter(
                Account.id == id,
                Account.is_active == True
            )

            if tenant_id:
                query = query.filter(Account.tenant_id == tenant_id)

            result = query.update({
                'is_active': False,
                'deleted_at': func.now()
            })
            self.session.commit()
            return result > 0
        except Exception as e:
            self.session.rollback()
            raise

    async def exists(self, id: str, tenant_id: str) -> bool:
        """Check if entity exists."""
        try:
            query = self.session.query(Account).filter(
                Account.id == id,
                Account.is_active == True
            )

            if tenant_id:
                query = query.filter(Account.tenant_id == tenant_id)

            return self.session.query(query.exists()).scalar()
        except Exception as e:
            return False

    async def count(self, tenant_id: str) -> int:
        """Count entities for tenant."""
        try:
            query = self.session.query(Account).filter(
                Account.is_active == True
            )

            if tenant_id:
                query = query.filter(Account.tenant_id == tenant_id)

            return query.count()
        except Exception as e:
            return 0

    async def get_by_number(self, account_number: str, tenant_id: str) -> Account | None:
        """Get account by account number"""
        return self.session.query(Account).filter(
            and_(
                Account.account_number == account_number,
                Account.tenant_id == tenant_id,
                Account.is_active == True
            )
        ).first()

    async def get_balance(self, account_id: str, tenant_id: str) -> float:
        """Get current account balance"""
        account = await self.get_by_id(account_id, tenant_id)
        return float(account.balance) if account else 0.0

    async def update_balance(self, account_id: str, amount: float, tenant_id: str) -> bool:
        """Update account balance"""
        try:
            account = await self.get_by_id(account_id, tenant_id)
            if account:
                account.balance += amount
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            return False


class JournalEntryRepositoryImpl(BaseRepositoryImpl[JournalEntry, dict, dict], JournalEntryRepository):
    """Journal entry repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, JournalEntry)

    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        """Post a journal entry"""
        try:
            entry = await self.get_by_id(entry_id, tenant_id)
            if entry and entry.status == 'draft':
                entry.status = 'posted'
                entry.posted_at = func.now()
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            return False

    async def get_entries_by_date_range(self, start_date: str, end_date: str, tenant_id: str):
        """Get journal entries by date range"""
        from datetime import datetime
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        return self.session.query(JournalEntry).filter(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.entry_date >= start,
                JournalEntry.entry_date <= end
            )
        ).all()
