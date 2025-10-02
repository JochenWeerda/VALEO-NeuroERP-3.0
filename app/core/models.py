"""
Database Models for VALEO-NeuroERP
SQLAlchemy models for all domain entities
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()


class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_active = Column(Boolean, default=True, nullable=False)


# CRM Domain Models
class Lead(Base, TimestampMixin, SoftDeleteMixin):
    """Lead model for CRM"""
    __tablename__ = "crm_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Lead information
    source = Column(String(50), nullable=False)
    status = Column(String(20), default="new", nullable=False)
    priority = Column(String(10), default="medium", nullable=False)
    estimated_value = Column(Numeric(15, 2), nullable=True)

    # Company information
    company_name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Assignment and tracking
    assigned_to = Column(UUID(as_uuid=True), nullable=True)

    # Conversion tracking
    converted_at = Column(DateTime, nullable=True)
    converted_to_customer_id = Column(UUID(as_uuid=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('ix_crm_leads_tenant_status', 'tenant_id', 'status'),
        Index('ix_crm_leads_assigned_to', 'assigned_to'),
        Index('ix_crm_leads_email', 'email'),
    )


class Contact(Base, TimestampMixin, SoftDeleteMixin):
    """Contact model for CRM"""
    __tablename__ = "crm_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('crm_customers.id'), nullable=False, index=True)

    # Personal information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Professional information
    position = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="contacts")

    # Indexes
    __table_args__ = (
        Index('ix_crm_contacts_tenant_customer', 'tenant_id', 'customer_id'),
        Index('ix_crm_contacts_email', 'email'),
    )


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    """Customer model for CRM"""
    __tablename__ = "crm_customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Customer identification
    customer_number = Column(String(50), nullable=False, unique=True, index=True)
    company_name = Column(String(100), nullable=False)

    # Contact information
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)

    # Address information
    address = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    country = Column(String(50), nullable=True)

    # Business information
    industry = Column(String(50), nullable=True)
    website = Column(String(100), nullable=True)

    # Financial information
    credit_limit = Column(Numeric(15, 2), nullable=True)
    payment_terms = Column(String(50), nullable=True)
    tax_id = Column(String(50), nullable=True)

    # Relationships
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_crm_customers_tenant_number', 'tenant_id', 'customer_number'),
        Index('ix_crm_customers_company_name', 'company_name'),
        Index('ix_crm_customers_email', 'email'),
    )


# Shared Domain Models
class Tenant(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant model for multi-tenancy"""
    __tablename__ = "shared_tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant information
    name = Column(String(100), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    settings = Column(Text, default="{}", nullable=False)

    # Indexes
    __table_args__ = (
        Index('ix_shared_tenants_domain', 'domain'),
    )


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model for authentication"""
    __tablename__ = "shared_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Authentication
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Personal information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Indexes
    __table_args__ = (
        Index('ix_shared_users_tenant_email', 'tenant_id', 'email'),
        Index('ix_shared_users_username', 'username'),
    )


# Finance Domain Models
class Account(Base, TimestampMixin, SoftDeleteMixin):
    """Chart of accounts - Kontenrahmen"""
    __tablename__ = "finance_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Account identification
    account_number = Column(String(20), nullable=False, index=True)
    account_name = Column(String(100), nullable=False)

    # Account classification
    account_type = Column(String(20), nullable=False)  # asset, liability, equity, revenue, expense
    category = Column(String(50), nullable=False)  # current_assets, fixed_assets, etc.

    # Account properties
    is_active = Column(Boolean, default=True, nullable=False)
    allow_manual_entries = Column(Boolean, default=True, nullable=False)

    # Financial data
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)

    # Relationships
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")

    # Indexes
    __table_args__ = (
        Index('ix_finance_accounts_tenant_number', 'tenant_id', 'account_number', unique=True),
        Index('ix_finance_accounts_tenant_type', 'tenant_id', 'account_type'),
        Index('ix_finance_accounts_category', 'category'),
    )


class JournalEntry(Base, TimestampMixin):
    """Journal entries - Buchungen"""
    __tablename__ = "finance_journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Entry metadata
    entry_number = Column(String(50), nullable=False, index=True)
    entry_date = Column(DateTime, nullable=False, index=True)
    posting_date = Column(DateTime, nullable=False)

    # Entry details
    description = Column(String(500), nullable=False)
    reference = Column(String(100), nullable=True)
    source = Column(String(50), nullable=False)  # manual, system, integration

    # Status and approval
    status = Column(String(20), default="draft", nullable=False)  # draft, posted, reversed
    posted_by = Column(UUID(as_uuid=True), nullable=True)
    posted_at = Column(DateTime, nullable=True)

    # Financial totals
    total_debit = Column(Numeric(15, 2), default=0.00, nullable=False)
    total_credit = Column(Numeric(15, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)

    # Audit trail
    reversal_of = Column(UUID(as_uuid=True), nullable=True)  # Reference to reversed entry
    reversal_date = Column(DateTime, nullable=True)

    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_finance_journal_entries_tenant_number', 'tenant_id', 'entry_number', unique=True),
        Index('ix_finance_journal_entries_tenant_date', 'tenant_id', 'entry_date'),
        Index('ix_finance_journal_entries_status', 'status'),
        Index('ix_finance_journal_entries_source', 'source'),
    )


class JournalEntryLine(Base, TimestampMixin):
    """Journal entry lines - Buchungszeilen"""
    __tablename__ = "finance_journal_entry_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('finance_journal_entries.id'), nullable=False, index=True)

    # Account reference
    account_id = Column(UUID(as_uuid=True), ForeignKey('finance_accounts.id'), nullable=False, index=True)

    # Financial amounts
    debit_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    credit_amount = Column(Numeric(15, 2), default=0.00, nullable=False)

    # Line details
    line_number = Column(Integer, nullable=False)
    description = Column(String(200), nullable=True)

    # Tax information
    tax_code = Column(String(20), nullable=True)
    tax_amount = Column(Numeric(15, 2), default=0.00, nullable=False)

    # Dimensions (for analytical accounting)
    cost_center = Column(String(50), nullable=True)
    profit_center = Column(String(50), nullable=True)
    segment = Column(String(50), nullable=True)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", back_populates="journal_entry_lines")

    # Indexes
    __table_args__ = (
        Index('ix_finance_journal_entry_lines_tenant_entry', 'tenant_id', 'journal_entry_id'),
        Index('ix_finance_journal_entry_lines_account', 'account_id'),
        Index('ix_finance_journal_entry_lines_cost_center', 'cost_center'),
    )