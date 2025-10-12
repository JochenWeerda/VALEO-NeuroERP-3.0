"""
Account Repository Implementation
PostgreSQL-based implementation of the Account repository interface
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..interfaces import AccountRepository
from ....infrastructure.models import Account

logger = logging.getLogger(__name__)


class AccountRepositoryImpl(AccountRepository):
    """PostgreSQL implementation of Account repository"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _get_session(self) -> Session:
        return self.session_factory()

    async def create(self, data: Dict[str, Any], tenant_id: str) -> Account:
        """Create a new account"""
        try:
            session = self._get_session()
            account = Account(
                tenant_id=tenant_id,
                **data
            )
            session.add(account)
            session.commit()
            session.refresh(account)
            logger.info(f"Created account {account.account_number} for tenant {tenant_id}")
            return account
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create account: {e}")
            raise
        finally:
            session.close()

    async def get_by_id(self, account_id: str, tenant_id: str) -> Optional[Account]:
        """Get account by ID"""
        try:
            session = self._get_session()
            account = session.query(Account).filter(
                and_(Account.id == account_id, Account.tenant_id == tenant_id, Account.is_active == True)
            ).first()
            return account
        except Exception as e:
            logger.error(f"Failed to get account {account_id}: {e}")
            raise
        finally:
            session.close()

    async def get_by_number(self, account_number: str, tenant_id: str) -> Optional[Account]:
        """Get account by account number"""
        try:
            session = self._get_session()
            account = session.query(Account).filter(
                and_(Account.account_number == account_number, Account.tenant_id == tenant_id, Account.is_active == True)
            ).first()
            return account
        except Exception as e:
            logger.error(f"Failed to get account {account_number}: {e}")
            raise
        finally:
            session.close()

    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100,
                     account_type: Optional[str] = None, category: Optional[str] = None) -> List[Account]:
        """Get all accounts with optional filtering"""
        try:
            session = self._get_session()
            query = session.query(Account).filter(
                and_(Account.tenant_id == tenant_id, Account.is_active == True)
            )

            if account_type:
                query = query.filter(Account.account_type == account_type)
            if category:
                query = query.filter(Account.category == category)

            accounts = query.offset(skip).limit(limit).all()
            return accounts
        except Exception as e:
            logger.error(f"Failed to get accounts for tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    async def count(self, tenant_id: str, account_type: Optional[str] = None,
                   category: Optional[str] = None) -> int:
        """Count accounts with optional filtering"""
        try:
            session = self._get_session()
            query = session.query(func.count(Account.id)).filter(
                and_(Account.tenant_id == tenant_id, Account.is_active == True)
            )

            if account_type:
                query = query.filter(Account.account_type == account_type)
            if category:
                query = query.filter(Account.category == category)

            count = query.scalar()
            return count or 0
        except Exception as e:
            logger.error(f"Failed to count accounts for tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    async def update(self, account_id: str, data: Dict[str, Any], tenant_id: str) -> Optional[Account]:
        """Update account"""
        try:
            session = self._get_session()
            account = session.query(Account).filter(
                and_(Account.id == account_id, Account.tenant_id == tenant_id, Account.is_active == True)
            ).first()

            if not account:
                return None

            for key, value in data.items():
                if hasattr(account, key):
                    setattr(account, key, value)

            session.commit()
            session.refresh(account)
            logger.info(f"Updated account {account_id}")
            return account
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update account {account_id}: {e}")
            raise
        finally:
            session.close()

    async def delete(self, account_id: str, tenant_id: str) -> bool:
        """Soft delete account"""
        try:
            session = self._get_session()
            account = session.query(Account).filter(
                and_(Account.id == account_id, Account.tenant_id == tenant_id, Account.is_active == True)
            ).first()

            if not account:
                return False

            account.is_active = False
            session.commit()
            logger.info(f"Soft deleted account {account_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete account {account_id}: {e}")
            raise
        finally:
            session.close()

    async def get_balance(self, account_id: str, tenant_id: str) -> float:
        """Get current account balance"""
        try:
            session = self._get_session()
            account = session.query(Account).filter(
                and_(Account.id == account_id, Account.tenant_id == tenant_id, Account.is_active == True)
            ).first()

            return float(account.balance) if account else 0.0
        except Exception as e:
            logger.error(f"Failed to get balance for account {account_id}: {e}")
            raise
        finally:
            session.close()

    async def update_balance(self, account_id: str, amount: float, tenant_id: str) -> bool:
        """Update account balance"""
        try:
            session = self._get_session()
            account = session.query(Account).filter(
                and_(Account.id == account_id, Account.tenant_id == tenant_id, Account.is_active == True)
            ).first()

            if not account:
                return False

            account.balance += amount
            session.commit()
            logger.info(f"Updated balance for account {account_id}: {amount}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update balance for account {account_id}: {e}")
            raise
        finally:
            session.close()
