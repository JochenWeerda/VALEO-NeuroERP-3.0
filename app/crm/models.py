"""
CRM SQLAlchemy Models
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Integer, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ContactType(str, enum.Enum):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    LEAD = "lead"


class LeadPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    VISIT = "visit"


class ActivityStatus(str, enum.Enum):
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Contact(Base):
    __tablename__ = "crm_contacts"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50))
    type = Column(Enum(ContactType), nullable=False, default=ContactType.CUSTOMER)
    
    # Address
    address_street = Column(String(255))
    address_zip = Column(String(10))
    address_city = Column(String(100))
    address_country = Column(String(100), default="Deutschland")
    
    notes = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    tenant_id = Column(String(36), nullable=False, index=True)


class Lead(Base):
    __tablename__ = "crm_leads"

    id = Column(String(36), primary_key=True)
    company = Column(String(255), nullable=False, index=True)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    source = Column(String(100))
    potential = Column(Numeric(12, 2), default=0)
    priority = Column(Enum(LeadPriority), default=LeadPriority.MEDIUM)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    assigned_to = Column(String(100))
    expected_close_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    tenant_id = Column(String(36), nullable=False, index=True)


class Activity(Base):
    __tablename__ = "crm_activities"

    id = Column(String(36), primary_key=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    type = Column(Enum(ActivityType), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    subject = Column(String(255))
    notes = Column(Text)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.PLANNED)
    created_by = Column(String(100))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tenant_id = Column(String(36), nullable=False, index=True)


class BetriebsProfil(Base):
    __tablename__ = "crm_betriebsprofile"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    betriebsform = Column(String(100))
    flaeche_ha = Column(Numeric(10, 2))
    tierbestand = Column(Integer)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True)
    notes = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tenant_id = Column(String(36), nullable=False, index=True)

