"""
Contact Repository Implementation
PostgreSQL-based implementation of the Contact repository interface
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..interfaces import ContactRepository
from ....infrastructure.models import Contact

logger = logging.getLogger(__name__)


class ContactRepositoryImpl(ContactRepository):
    """PostgreSQL implementation of Contact repository"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _get_session(self) -> Session:
        return self.session_factory()

    async def create(self, data: Dict[str, Any], tenant_id: str) -> Contact:
        """Create a new contact"""
        try:
            session = self._get_session()
            contact = Contact(
                tenant_id=tenant_id,
                **data
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)
            logger.info(f"Created contact {contact.id} for tenant {tenant_id}")
            return contact
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create contact: {e}")
            raise
        finally:
            session.close()

    async def get_by_id(self, contact_id: str, tenant_id: str) -> Optional[Contact]:
        """Get contact by ID"""
        try:
            session = self._get_session()
            contact = session.query(Contact).filter(
                and_(Contact.id == contact_id, Contact.tenant_id == tenant_id, Contact.is_active == True)
            ).first()
            return contact
        except Exception as e:
            logger.error(f"Failed to get contact {contact_id}: {e}")
            raise
        finally:
            session.close()

    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100,
                     customer_id: Optional[str] = None) -> List[Contact]:
        """Get all contacts with optional filtering"""
        try:
            session = self._get_session()
            query = session.query(Contact).filter(
                and_(Contact.tenant_id == tenant_id, Contact.is_active == True)
            )

            if customer_id:
                query = query.filter(Contact.customer_id == customer_id)

            contacts = query.offset(skip).limit(limit).all()
            return contacts
        except Exception as e:
            logger.error(f"Failed to get contacts for tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    async def count(self, tenant_id: str, customer_id: Optional[str] = None) -> int:
        """Count contacts with optional filtering"""
        try:
            session = self._get_session()
            query = session.query(func.count(Contact.id)).filter(
                and_(Contact.tenant_id == tenant_id, Contact.is_active == True)
            )

            if customer_id:
                query = query.filter(Contact.customer_id == customer_id)

            count = query.scalar()
            return count or 0
        except Exception as e:
            logger.error(f"Failed to count contacts for tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    async def update(self, contact_id: str, data: Dict[str, Any], tenant_id: str) -> Optional[Contact]:
        """Update contact"""
        try:
            session = self._get_session()
            contact = session.query(Contact).filter(
                and_(Contact.id == contact_id, Contact.tenant_id == tenant_id, Contact.is_active == True)
            ).first()

            if not contact:
                return None

            for key, value in data.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)

            session.commit()
            session.refresh(contact)
            logger.info(f"Updated contact {contact_id}")
            return contact
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update contact {contact_id}: {e}")
            raise
        finally:
            session.close()

    async def delete(self, contact_id: str, tenant_id: str) -> bool:
        """Soft delete contact"""
        try:
            session = self._get_session()
            contact = session.query(Contact).filter(
                and_(Contact.id == contact_id, Contact.tenant_id == tenant_id, Contact.is_active == True)
            ).first()

            if not contact:
                return False

            contact.is_active = False
            session.commit()
            logger.info(f"Soft deleted contact {contact_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete contact {contact_id}: {e}")
            raise
        finally:
            session.close()
