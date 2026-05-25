"""
Agribusiness Domain Models
Farmer master data for agribusiness/farmers endpoints.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class Farmer(Base):
    """Landwirt-Stammdaten (Farmer master record)."""

    __tablename__ = "farmers"
    __table_args__ = {"schema": "domain_shared"}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False, index=True)
    farmer_number = Column(String(64), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    full_name = Column(String(512))
    email = Column(String(255))
    phone = Column(String(64))
    farmer_type = Column(String(64), default="standard")
    status = Column(String(32), default="active")
    portal_access_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
