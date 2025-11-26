"""
CRM Domain Models
Models for Customer Relationship Management
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


class Customer(Base):
    """Customer master data"""
    __tablename__ = "crm_customers"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_number = Column(String(20), nullable=False, unique=True)
    company_name = Column(String(200), nullable=False)
    salutation = Column(String(20))
    first_name = Column(String(100))
    last_name = Column(String(100), nullable=False)

    ***REMOVED*** Address
    street = Column(String(200), nullable=False)
    postal_code = Column(String(10), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(3), default="DE")

    ***REMOVED*** Contact
    phone = Column(String(50))
    email = Column(String(200))
    mobile = Column(String(50))

    ***REMOVED*** Business data
    ust_id = Column(String(20))
    tax_number = Column(String(50))
    credit_limit = Column(DECIMAL(12, 2), default=0)
    payment_terms = Column(String(50), default="30 Tage")
    discount = Column(DECIMAL(5, 2), default=0)
    credit_rating = Column(String(20), default="gut")

    ***REMOVED*** Sales data
    last_order_date = Column(DateTime(timezone=True))
    total_revenue = Column(DECIMAL(15, 2), default=0)
    customer_segment = Column(String(20), default="C")  ***REMOVED*** Bestehend, wird zu analytics.segment gemappt
    price_group = Column(String(50))  ***REMOVED*** NEU: sales.price_group
    tax_category = Column(String(50))  ***REMOVED*** NEU: tax.category
    ***REMOVED*** industry und region: Werden aus crm-core gemappt (bestehend)
    ***REMOVED*** customer_price_list: Wird über customer.price_list_id verwaltet (bestehend)

    ***REMOVED*** Status
    status = Column(String(20), default="aktiv")
    is_active = Column(Boolean, default=True)

    ***REMOVED*** Metadata
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ***REMOVED*** Relationships
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="customer", cascade="all, delete-orphan")


class Contact(Base):
    """Contact persons for customers/suppliers"""
    __tablename__ = "crm_contacts"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("domain_crm.crm_customers.id"), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(100))
    department = Column(String(100))

    ***REMOVED*** Contact details
    phone = Column(String(50))
    mobile = Column(String(50))
    email = Column(String(200), nullable=False)

    ***REMOVED*** Preferences
    preferred_contact_method = Column(String(20), default="email")  ***REMOVED*** email, phone, mobile
    communication_language = Column(String(3), default="de")

    ***REMOVED*** Personal data
    birthday = Column(DateTime(timezone=True))
    notes = Column(Text)

    ***REMOVED*** Priority and status
    priority = Column(String(1), default="C")  ***REMOVED*** A, B, C, D
    status = Column(String(20), default="aktiv")
    is_active = Column(Boolean, default=True)

    ***REMOVED*** Metadata
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ***REMOVED*** Relationships
    customer = relationship("Customer", back_populates="contacts")


class Activity(Base):
    """Customer activities and interactions"""
    __tablename__ = "crm_activities"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("domain_crm.crm_customers.id"), nullable=False)
    contact_id = Column(String, ForeignKey("domain_crm.crm_contacts.id"))

    ***REMOVED*** Activity details
    activity_type = Column(String(50), nullable=False)  ***REMOVED*** call, visit, email, meeting, note
    subject = Column(String(200), nullable=False)
    description = Column(Text)

    ***REMOVED*** Timing
    activity_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer)

    ***REMOVED*** Assignment and status
    assigned_to = Column(String, nullable=False)  ***REMOVED*** User ID
    status = Column(String(20), default="completed")  ***REMOVED*** planned, completed, cancelled

    ***REMOVED*** Follow-up
    next_action_date = Column(DateTime(timezone=True))
    next_action_description = Column(Text)

    ***REMOVED*** Location (for visits)
    location = Column(String(200))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))

    ***REMOVED*** Additional data
    metadata = Column(JSONB)  ***REMOVED*** Flexible storage for type-specific data

    ***REMOVED*** Metadata
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ***REMOVED*** Relationships
    customer = relationship("Customer", back_populates="activities")


class VisitReport(Base):
    """Detailed visit reports for field sales"""
    __tablename__ = "crm_visit_reports"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("domain_crm.crm_customers.id"), nullable=False)

    ***REMOVED*** Visit details
    visit_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))

    ***REMOVED*** Personnel
    sales_rep = Column(String, nullable=False)  ***REMOVED*** User ID
    contact_person = Column(String)  ***REMOVED*** Contact ID

    ***REMOVED*** Location and travel
    location = Column(String(200))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    kilometers_driven = Column(DECIMAL(8, 2))

    ***REMOVED*** Content
    main_topics = Column(JSONB)  ***REMOVED*** Array of discussed topics
    products_discussed = Column(JSONB)  ***REMOVED*** Array of product IDs
    customer_feedback = Column(Text)
    sales_opportunities = Column(JSONB)  ***REMOVED*** Array of opportunities

    ***REMOVED*** Results
    orders_placed = Column(JSONB)  ***REMOVED*** Array of order IDs
    quotes_created = Column(JSONB)  ***REMOVED*** Array of quote IDs
    samples_provided = Column(JSONB)  ***REMOVED*** Array of sample details

    ***REMOVED*** Follow-up
    follow_up_actions = Column(JSONB)  ***REMOVED*** Array of follow-up tasks
    next_visit_date = Column(DateTime(timezone=True))

    ***REMOVED*** Photos and documents
    photos = Column(JSONB)  ***REMOVED*** Array of photo URLs/metadata
    documents = Column(JSONB)  ***REMOVED*** Array of document URLs

    ***REMOVED*** Metadata
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ***REMOVED*** Relationships
    customer = relationship("Customer")


class Opportunity(Base):
    """Sales opportunities and pipeline management"""
    __tablename__ = "crm_opportunities"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("domain_crm.crm_customers.id"), nullable=False)

    ***REMOVED*** Opportunity details
    title = Column(String(200), nullable=False)
    description = Column(Text)

    ***REMOVED*** Product/Service
    product_category = Column(String(100))
    estimated_value = Column(DECIMAL(12, 2))
    estimated_quantity = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="EUR")

    ***REMOVED*** Pipeline
    stage = Column(String(50), default="prospecting")  ***REMOVED*** prospecting, qualification, proposal, negotiation, closed_won, closed_lost
    probability = Column(Integer, default=0)  ***REMOVED*** 0-100%
    expected_close_date = Column(DateTime(timezone=True))

    ***REMOVED*** Assignment
    assigned_to = Column(String, nullable=False)  ***REMOVED*** User ID
    source = Column(String(100))  ***REMOVED*** How was this opportunity created?

    ***REMOVED*** Status and tracking
    status = Column(String(20), default="aktiv")
    is_active = Column(Boolean, default=True)

    ***REMOVED*** Competition
    competitors = Column(JSONB)  ***REMOVED*** Array of competitor information

    ***REMOVED*** Metadata
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ***REMOVED*** Relationships
    customer = relationship("Customer")