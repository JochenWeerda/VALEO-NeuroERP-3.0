"""
Base repository implementation for VALEO-NeuroERP
SQLAlchemy-based repository following repository pattern
"""

import logging
from datetime import datetime
from typing import List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from ...core.database import Base

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Base)
TCreate = TypeVar('TCreate')
TUpdate = TypeVar('TUpdate')


class BaseRepositoryImpl(Generic[T, TCreate, TUpdate]):
    """
    Base repository implementation using SQLAlchemy.
    Provides common CRUD operations for all entities.
    """

    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        """Get entity by ID."""
        try:
            # Check if model has tenant_id field
            if hasattr(self.model_class, 'tenant_id'):
                return self.session.query(self.model_class).filter(
                    and_(
                        self.model_class.id == id,
                        self.model_class.tenant_id == tenant_id,
                        self.model_class.is_active == True
                    )
                ).first()
            else:
                return self.session.query(self.model_class).filter(
                    and_(
                        self.model_class.id == id,
                        self.model_class.is_active == True
                    )
                ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {id}: {e}")
            return None

    async def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100, **kwargs) -> List[T]:
        """Get all entities with pagination and optional filtering."""
        try:
            query = self.session.query(self.model_class).filter(
                self.model_class.is_active == True
            )

            # Add tenant filter if model supports it
            if hasattr(self.model_class, 'tenant_id'):
                query = query.filter(self.model_class.tenant_id == tenant_id)

            # Apply additional filters from kwargs
            for key, value in kwargs.items():
                if value is not None and hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key).ilike(f"%{value}%"))

            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {e}")
            return []

    async def create(self, data: TCreate, tenant_id: str) -> T:
        """Create a new entity."""
        try:
            # Convert data to dict if it's a Pydantic model
            if hasattr(data, 'model_dump'):
                data_dict = data.model_dump()
            else:
                data_dict = dict(data) if hasattr(data, '__dict__') else data

            # Add tenant_id if model supports it
            if hasattr(self.model_class, 'tenant_id'):
                data_dict['tenant_id'] = tenant_id

            # Create instance
            instance = self.model_class(**data_dict)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)

            logger.info(f"Created {self.model_class.__name__} with ID {instance.id}")
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise

    async def update(self, id: str, data: TUpdate, tenant_id: str) -> Optional[T]:
        """Update an existing entity."""
        try:
            # Convert data to dict if it's a Pydantic model
            if hasattr(data, 'model_dump'):
                data_dict = data.model_dump(exclude_unset=True)
            else:
                data_dict = dict(data) if hasattr(data, '__dict__') else data

            # Build query
            query = self.session.query(self.model_class).filter(
                self.model_class.id == id,
                self.model_class.is_active == True
            )

            # Add tenant filter if model supports it
            if hasattr(self.model_class, 'tenant_id'):
                query = query.filter(self.model_class.tenant_id == tenant_id)

            # Update
            result = query.update(data_dict)
            self.session.commit()

            if result > 0:
                # Return updated instance
                return await self.get_by_id(id, tenant_id)
            else:
                return None
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model_class.__name__} {id}: {e}")
            raise

    async def delete(self, id: str, tenant_id: str) -> bool:
        """Soft delete an entity."""
        try:
            # Build query
            query = self.session.query(self.model_class).filter(
                self.model_class.id == id,
                self.model_class.is_active == True
            )

            # Add tenant filter if model supports it
            if hasattr(self.model_class, 'tenant_id'):
                query = query.filter(self.model_class.tenant_id == tenant_id)

            # Soft delete
            result = query.update({
                'is_active': False,
                'deleted_at': datetime.utcnow()
            })
            self.session.commit()

            success = result > 0
            if success:
                logger.info(f"Soft deleted {self.model_class.__name__} {id}")
            return success
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} {id}: {e}")
            raise

    async def exists(self, id: str, tenant_id: str) -> bool:
        """Check if entity exists."""
        try:
            # Build query
            query = self.session.query(self.model_class).filter(
                self.model_class.id == id,
                self.model_class.is_active == True
            )

            # Add tenant filter if model supports it
            if hasattr(self.model_class, 'tenant_id'):
                query = query.filter(self.model_class.tenant_id == tenant_id)

            return self.session.query(query.exists()).scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model_class.__name__} {id}: {e}")
            return False

    async def count(self, tenant_id: str, **kwargs) -> int:
        """Count entities for tenant with optional filtering."""
        try:
            query = self.session.query(self.model_class).filter(
                self.model_class.is_active == True
            )

            # Add tenant filter if model supports it
            if hasattr(self.model_class, 'tenant_id'):
                query = query.filter(self.model_class.tenant_id == tenant_id)

            for key, value in kwargs.items():
                if value is not None and hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key).ilike(f"%{value}%"))

            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            return 0
