"""
Concrete repository implementations for VALEO-NeuroERP
SQLAlchemy-based implementations of repository interfaces
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, func, or_

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

    async def get_by_customer_number(self, customer_number: str, tenant_id: str) -> Customer | None:
        """Return an active customer by customer number for the current tenant."""
        return (
            self.session.query(Customer)
            .filter(
                and_(
                    Customer.customer_number == customer_number,
                    Customer.tenant_id == tenant_id,
                    Customer.is_active == True,
                )
            )
            .first()
        )

    async def get_all(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        **kwargs
    ) -> list[Customer]:
        """Get customers for a tenant with optional search."""
        query = self.session.query(Customer).filter(Customer.is_active == True)

        if tenant_id:
            query = query.filter(Customer.tenant_id == tenant_id)

        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.company_name.ilike(like),
                    Customer.contact_person.ilike(like)
                )
            )

        return query.order_by(Customer.company_name.asc()).offset(skip).limit(limit).all()

    async def count(self, tenant_id: str, search: str | None = None, **kwargs) -> int:
        """Count customers for a tenant with optional search."""
        query = self.session.query(Customer).filter(Customer.is_active == True)

        if tenant_id:
            query = query.filter(Customer.tenant_id == tenant_id)

        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.company_name.ilike(like),
                    Customer.contact_person.ilike(like)
                )
            )

        return query.count()


class LeadRepositoryImpl(BaseRepositoryImpl[Lead, dict, dict], LeadRepository):
    """Lead repository implementation"""
    def __init__(self, session: Session):
        super().__init__(session, Lead)

    async def convert_to_customer(self, lead_id: str, customer_id: str, tenant_id: str) -> bool:
        """Mark lead as converted to a customer."""
        lead = await self.get_by_id(lead_id, tenant_id)
        if not lead:
            return False

        lead.status = "converted"
        lead.converted_to_customer_id = customer_id
        lead.converted_at = datetime.utcnow()
        self.session.commit()
        return True


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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
            return False

    async def count(self, tenant_id: str, **kwargs) -> int:
        """Count entities for tenant."""
        try:
            query = self.session.query(Account).filter(
                Account.is_active == True
            )

            if tenant_id:
                query = query.filter(Account.tenant_id == tenant_id)

            account_type = kwargs.get("account_type")
            if account_type:
                query = query.filter(Account.account_type == account_type)

            category = kwargs.get("category")
            if category:
                query = query.filter(Account.category == category)

            return query.count()
        except Exception:
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

    @staticmethod
    def _compute_hash(seq: int, entry_date: str, total_debit: float, total_credit: float, reference: str, hash_prev: str) -> str:
        import hashlib, json
        payload = json.dumps({
            "seq": seq, "entry_date": str(entry_date),
            "debit": str(total_debit), "credit": str(total_credit),
            "reference": reference or "", "prev": hash_prev,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    async def create(self, data: dict, tenant_id: str) -> JournalEntry:
        """Create a new journal entry with GoBD-compliant hash-chain."""
        from sqlalchemy.exc import SQLAlchemyError
        from ..repositories.base_repository import logger
        try:
            lines_data = data.pop("lines", [])
            data.setdefault("tenant_id", tenant_id)

            # GoBD: lückenlose Sequenz + Hash-Kette
            last = (
                self.session.query(JournalEntry)
                .filter(JournalEntry.tenant_id == tenant_id)
                .order_by(JournalEntry.sequence_number.desc())
                .first()
            )
            seq = (last.sequence_number or 0) + 1 if last else 1
            hash_prev = last.hash_current if last else "GENESIS"
            entry_date = data.get("entry_date") or data.get("posting_date") or datetime.utcnow().isoformat()
            hash_current = self._compute_hash(
                seq, entry_date,
                float(data.get("total_debit", 0)), float(data.get("total_credit", 0)),
                data.get("reference", ""), hash_prev,
            )
            data["sequence_number"] = seq
            data["hash_prev"] = hash_prev
            data["hash_current"] = hash_current

            # Strip keys not in ORM columns
            orm_cols = {c.key for c in JournalEntry.__table__.columns}
            clean = {k: v for k, v in data.items() if k in orm_cols}
            entry = JournalEntry(**clean)
            self.session.add(entry)
            self.session.flush()

            # Persist lines if provided as dicts
            for line in lines_data:
                if isinstance(line, dict):
                    line.setdefault("tenant_id", tenant_id)
                    line["journal_entry_id"] = entry.id
                    line_orm = JournalEntryLine(**{
                        k: v for k, v in line.items()
                        if k in {c.key for c in JournalEntryLine.__table__.columns}
                    })
                    self.session.add(line_orm)

            self.session.commit()
            self.session.refresh(entry)
            logger.info("Created JournalEntry %s seq=%s hash=%s…", entry.id, seq, hash_current[:8])
            return entry
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error creating JournalEntry: %s", e)
            raise

    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs):
        """Tenant-scoped reads propagate failures instead of reporting an empty ledger."""
        query = (
            self.session.query(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .filter(JournalEntry.tenant_id == tenant_id)
        )
        ref = kwargs.pop("reference", None)
        if ref is not None:
            query = query.filter(JournalEntry.reference == ref)
        for key, value in kwargs.items():
            if value is not None and hasattr(JournalEntry, key):
                query = query.filter(getattr(JournalEntry, key).ilike(f"%{value}%"))
        return query.order_by(JournalEntry.entry_date.desc()).offset(skip).limit(limit).all()

    def _transaction_service(self, tenant_id: str):
        from app.services.finance_transaction_service import FinanceTransactionService

        return FinanceTransactionService(self.session, tenant_id)

    async def get_by_id(self, id: str, tenant_id: str):
        """Journal heads have no is_active column; scope by tenant and identity."""
        return (
            self.session.query(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .filter(JournalEntry.id == id, JournalEntry.tenant_id == tenant_id)
            .first()
        )

    async def exists(self, id: str, tenant_id: str) -> bool:
        return await self.get_by_id(id, tenant_id) is not None

    async def count(self, tenant_id: str, **kwargs) -> int:
        query = self.session.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(JournalEntry, key):
                query = query.filter(getattr(JournalEntry, key) == value)
        return query.count()

    async def update(self, id: str, data: dict, tenant_id: str):
        from app.core.exceptions import EntityNotFoundError, ValidationFailedError

        # No silent loss of API date edits or unguarded arbitrary column updates.
        if set(data) - {"description", "reference", "document_type"}:
            raise ValidationFailedError("Unsupported journal update fields")
        for key, maximum in (("description", 200), ("reference", 50), ("document_type", 30)):
            if key in data and (
                not isinstance(data[key], str) or not data[key].strip() or len(data[key]) > maximum
            ):
                raise ValidationFailedError(f"Invalid journal {key}")
        try:
            return self._transaction_service(tenant_id).update(id, data)
        except EntityNotFoundError:
            return None

    async def delete(self, id: str, tenant_id: str) -> bool:
        from app.core.exceptions import EntityNotFoundError

        try:
            self._transaction_service(tenant_id).delete(id)
        except EntityNotFoundError:
            return False
        return True

    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        from app.core.exceptions import EntityNotFoundError

        try:
            self._transaction_service(tenant_id).post(entry_id)
        except EntityNotFoundError:
            return False
        return True

    async def get_entries_by_date_range(
        self,
        start_date: str,
        end_date: str,
        tenant_id: str,
        reference: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ):
        """Get journal entries by date range with DB-level pagination."""
        from datetime import datetime
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = (
            self.session.query(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .filter(
                and_(
                    JournalEntry.tenant_id == tenant_id,
                    JournalEntry.entry_date >= start,
                    JournalEntry.entry_date <= end,
                )
            )
        )
        if reference is not None:
            query = query.filter(JournalEntry.reference == reference)
        return query.order_by(JournalEntry.entry_date.desc()).offset(skip).limit(limit).all()

    async def get_entries_by_account(
        self,
        account_id: str,
        tenant_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """Get journal entries that contain at least one line for the given account."""
        query = (
            self.session.query(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .join(JournalEntryLine, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .filter(
                and_(
                    JournalEntry.tenant_id == tenant_id,
                    JournalEntryLine.account_id == account_id,
                )
            )
        )

        if start_date:
            query = query.filter(JournalEntry.entry_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(JournalEntry.entry_date <= datetime.fromisoformat(end_date))

        return query.order_by(JournalEntry.entry_date.desc()).all()

    async def reverse_entry(self, entry_id: str, reason: str, tenant_id: str):
        """Use the canonical locked, validated and stamped reversal."""
        from app.core.exceptions import EntityNotFoundError

        try:
            _, reversal = self._transaction_service(tenant_id).reverse(entry_id, reason)
        except EntityNotFoundError:
            return None
        return reversal
