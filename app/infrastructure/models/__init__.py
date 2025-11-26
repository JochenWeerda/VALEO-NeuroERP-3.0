"""
SQLAlchemy models for VALEO-NeuroERP
Database entities following domain-driven design
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


# Shared Models
class Tenant(Base):
    """Tenant model for multi-tenancy"""
    __tablename__ = "tenants"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=False)
    settings = Column(Text, default="{}")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    """User model"""
    __tablename__ = "users"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    keycloak_id = Column(String, nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    roles = Column(Text, default="[]")  # JSON array of roles
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


# CRM Models
class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_number = Column(String(50), nullable=False)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    country = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)
    website = Column(String(100), nullable=True)
    customer_type = Column(String(50), nullable=True)
    credit_limit = Column(DECIMAL(15, 2), nullable=True)
    payment_terms = Column(Integer, nullable=True)
    tax_id = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Lead(Base):
    """Lead model"""
    __tablename__ = "leads"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    priority = Column(String(10), default="medium")
    estimated_value = Column(DECIMAL(15, 2), nullable=True)
    company_name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    assigned_to = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    converted_to_customer_id = Column(String, ForeignKey("domain_crm.customers.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Contact(Base):
    """Contact model"""
    __tablename__ = "contacts"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    position = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    customer_id = Column(String, ForeignKey("domain_crm.customers.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Activity(Base):
    """CRM Activity model"""
    __tablename__ = "activities"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(20), nullable=False)  # meeting, call, email, note
    title = Column(String(200), nullable=False)
    customer = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)  # planned, completed, overdue
    assigned_to = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FarmProfile(Base):
    """Farm Profile model for agricultural operations"""
    __tablename__ = "farm_profiles"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_name = Column(String(200), nullable=False)
    owner = Column(String(100), nullable=False)
    total_area = Column(Float, nullable=False)  # in hectares
    crops = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")  # JSON array of {crop, area}
    livestock = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")  # JSON array of {type, count}
    location = Column(postgresql.JSONB(astext_type=Text()), nullable=True)  # {latitude, longitude, address}
    certifications = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")  # JSON array of strings
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Inventory Models
class Article(Base):
    """Article/Product model"""
    __tablename__ = "articles"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_number = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    barcode = Column(String(50), nullable=True)
    supplier_number = Column(String(50), nullable=True)
    purchase_price = Column(DECIMAL(10, 2), nullable=True)
    sales_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    min_stock = Column(DECIMAL(10, 2), nullable=True)
    max_stock = Column(DECIMAL(10, 2), nullable=True)
    weight = Column(DECIMAL(8, 2), nullable=True)
    dimensions = Column(String(50), nullable=True)
    current_stock = Column(DECIMAL(10, 2), default=0)
    reserved_stock = Column(DECIMAL(10, 2), default=0)
    available_stock = Column(DECIMAL(10, 2), default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Warehouse(Base):
    """Warehouse model"""
    __tablename__ = "warehouses"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    country = Column(String(2), default="DE")
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    warehouse_type = Column(String(20), default="standard")
    total_capacity = Column(DECIMAL(12, 2), nullable=True)
    used_capacity = Column(DECIMAL(12, 2), default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class StockMovement(Base):
    """Stock movement model"""
    __tablename__ = "inventory_stock_movements"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # in, out, transfer, adjustment
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_cost = Column(DECIMAL(10, 2), nullable=True)
    reference_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    previous_stock = Column(DECIMAL(10, 2), nullable=False)
    new_stock = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(12, 2), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InventoryCount(Base):
    """Inventory count model"""
    __tablename__ = "inventory_counts"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    count_date = Column(DateTime(timezone=True), server_default=func.now())
    counted_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    status = Column(String(20), default="draft")  # draft, completed, approved
    total_items = Column(Integer, default=0)
    discrepancies_found = Column(Integer, default=0)
    approved_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Finance Models
class Account(Base):
    """Chart of accounts model"""
    __tablename__ = "finance_accounts"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String(20), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False)  # asset, liability, equity, revenue, expense
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_summary = Column(Boolean, default=False)
    balance = Column(DECIMAL(15, 2), default=0)
    last_transaction_date = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    parent_account_id = Column(String, ForeignKey("domain_erp.finance_accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class JournalEntry(Base):
    """Journal entry model"""
    __tablename__ = "finance_journal_entries"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entry_number = Column(String(20), nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    posting_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(200), nullable=False)
    reference = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), default="draft")  # draft, posted, reversed
    total_debit = Column(DECIMAL(15, 2), default=0)
    total_credit = Column(DECIMAL(15, 2), default=0)
    posted_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    reversed_entry_id = Column(String, ForeignKey("domain_erp.finance_journal_entries.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JournalEntryLine(Base):
    """Journal entry line model"""
    __tablename__ = "finance_journal_entry_lines"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    journal_entry_id = Column(String, ForeignKey("domain_erp.finance_journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("domain_erp.finance_accounts.id"), nullable=False)
    debit = Column(DECIMAL(15, 2), default=0)
    credit = Column(DECIMAL(15, 2), default=0)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Policy Engine Models
class PolicyRule(Base):
    """MCP policy rule model"""
    __tablename__ = "policy_rules"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    when_kpi_id = Column(String, nullable=False)
    when_severity = Column(postgresql.JSONB(astext_type=Text()), nullable=False)
    action = Column(String, nullable=False)
    params = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    limits = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    window = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    approval = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    auto_execute = Column(Boolean, default=False)
    auto_suggest = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Audit & Compliance Models
class AuditLog(Base):
    """Audit log for compliance tracking"""
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    user_email = Column(String(100), nullable=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String, nullable=False)
    changes = Column(postgresql.JSONB(astext_type=Text()), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(200), nullable=True)
    correlation_id = Column(String(50), nullable=True)


# Import Agrar models
from .agrar_models import (
    Saatgut,
    SaatgutLizenz,
    Duenger,
    DuengerMischung,
    PSM,
    Sachkunde,
    Biostimulanz
)
