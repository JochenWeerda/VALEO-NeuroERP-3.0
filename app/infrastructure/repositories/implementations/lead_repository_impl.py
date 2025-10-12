"""
Lead Repository Implementation
PostgreSQL-based implementation of the Lead repository interface
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..interfaces import LeadRepository
from ....infrastructure.models import Lead

logger = logging.getLogger(__name__)


class LeadRepositoryImpl(LeadRepository):
    """PostgreSQL implementation of Lead repository"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _get_session(self) -> Session:
        return self.session_factory()

    async def create(self, data: Dict[str, Any], tenant_id: str) -> Lead:
        """Create a new lead"""
        try:
            session = self._get_session()
            lead = Lead(
                tenant_id=tenant_id,
                **data
            )
            session.add(lead)
            session.commit()
            session.refresh(lead)
            logger.info(f"Created lead {lead.id} for tenant {tenant_id}")
            return lead
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create lead: {e}")
            raise
        finally:
            session.close()

    async def get_by_id(self, lead_id: str, tenant_id: str) -> Optional[Lead]:
        """Get lead by ID"""
        try:
            session = self._get_session()
            lead = session.query(Lead).filter(
                and_(Lead.id == lead_id, Lead.tenant_id == tenant_id, Lead.is_active == True)
            ).first()
            return lead
        except Exception as e:
            logger.error(f"Failed to get lead {lead_id}: {e}")
            raise
        finally:
            session.close()

    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100,
                     status: Optional[str] = None, assigned_to: Optional[str] = None) -> List[Lead]:
        """Get all leads with optional filtering"""
        try:
            session = self._get_session()
            query = session.query(Lead).filter(
                and_(Lead.tenant_id == tenant_id, Lead.is_active == True)
            )

            if status:
                query = query.filter(Lead.status == status)
            if assigned_to:
                query = query.filter(Lead.assigned_to == assigned_to)

            leads = query.offset(skip).limit(limit).all()
            return leads
        except Exception as e:
            logger.error(f"Failed to get leads for tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    async def count(self, tenant_id: str, status: Optional[str] = None,
                   assigned_to: Optional[str] = None) -> int:
        """Count leads with optional filtering"""
        try:
            session = self._get_session()
            query = session.query(func.count(Lead.id)).filter(
                and_(Lead.tenant_id == tenant_id, Lead.is_active == True)
            )

            if status:
                query = query.filter(Lead.status == status)
            if assigned_to:
                query = query.filter(Lead.assigned_to == assigned_to)

            count = query.scalar()
            return count or 0
        except Exception as e:
            logger.error(f"Failed to count leads for tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    async def update(self, lead_id: str, data: Dict[str, Any], tenant_id: str) -> Optional[Lead]:
        """Update lead"""
        try:
            session = self._get_session()
            lead = session.query(Lead).filter(
                and_(Lead.id == lead_id, Lead.tenant_id == tenant_id, Lead.is_active == True)
            ).first()

            if not lead:
                return None

            for key, value in data.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)

            session.commit()
            session.refresh(lead)
            logger.info(f"Updated lead {lead_id}")
            return lead
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update lead {lead_id}: {e}")
            raise
        finally:
            session.close()

    async def delete(self, lead_id: str, tenant_id: str) -> bool:
        """Soft delete lead"""
        try:
            session = self._get_session()
            lead = session.query(Lead).filter(
                and_(Lead.id == lead_id, Lead.tenant_id == tenant_id, Lead.is_active == True)
            ).first()

            if not lead:
                return False

            lead.is_active = False
            session.commit()
            logger.info(f"Soft deleted lead {lead_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete lead {lead_id}: {e}")
            raise
        finally:
            session.close()

    async def convert_to_customer(self, lead_id: str, customer_id: str, tenant_id: str) -> bool:
        """Convert lead to customer"""
        try:
            session = self._get_session()
            lead = session.query(Lead).filter(
                and_(Lead.id == lead_id, Lead.tenant_id == tenant_id, Lead.is_active == True)
            ).first()

            if not lead:
                return False

            # Update lead status and conversion info
            from datetime import datetime
            lead.status = "converted"
            lead.converted_at = datetime.utcnow()
            lead.converted_to_customer_id = customer_id

            session.commit()
            logger.info(f"Converted lead {lead_id} to customer {customer_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to convert lead {lead_id}: {e}")
            raise
        finally:
            session.close()
