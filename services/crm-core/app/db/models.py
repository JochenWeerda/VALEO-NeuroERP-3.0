"""SQLAlchemy models for CRM core."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CustomerStatus(str, Enum):
    PROSPECT = "prospect"
    ACTIVE = "active"
    DORMANT = "dormant"
    FORMER = "former"
    BLACKLISTED = "blacklisted"


class CustomerType(str, Enum):
    COMPANY = "company"
    PERSON = "person"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class Customer(Base):
    __tablename__ = "crm_core_customers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[CustomerType] = mapped_column(
        SQLEnum(
            CustomerType,
            name="crm_core_customer_type",
            values_callable=enum_values,
        ),
        default=CustomerType.COMPANY,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[CustomerStatus] = mapped_column(
        SQLEnum(
            CustomerStatus,
            name="crm_core_customer_status",
            values_callable=enum_values,
        ),
        default=CustomerStatus.PROSPECT,
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    industry: Mapped[str | None] = mapped_column(String(128))
    region: Mapped[str | None] = mapped_column(String(64))
    lead_score: Mapped[float | None] = mapped_column(Float)
    churn_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes: Mapped[str | None] = mapped_column(Text)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "crm_core_contacts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_core_customers.id"), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    job_title: Mapped[str | None] = mapped_column(String(150))
    department: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer: Mapped[Customer] = relationship(back_populates="contacts")


class Lead(Base):
    __tablename__ = "crm_core_leads"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_core_customers.id"), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new")
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    source: Mapped[str | None] = mapped_column(String(64))
    estimated_value: Mapped[float | None] = mapped_column(Float)
    assigned_to: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer: Mapped[Customer | None] = relationship("Customer")


class Activity(Base):
    __tablename__ = "crm_core_activities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_core_customers.id"), nullable=True)
    contact_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_core_contacts.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    assigned_to: Mapped[str | None] = mapped_column(String(64))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer: Mapped[Customer | None] = relationship("Customer")
    contact: Mapped[Contact | None] = relationship("Contact")


class FarmProfile(Base):
    __tablename__ = "crm_core_farm_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_core_customers.id"), nullable=True)
    farm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(150), nullable=False)
    total_area: Mapped[float] = mapped_column(Float, nullable=False)
    crops: Mapped[dict | None] = mapped_column(JSONB, default=list)
    livestock: Mapped[dict | None] = mapped_column(JSONB, default=list)
    location: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    certifications: Mapped[dict | None] = mapped_column(JSONB, default=list)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer: Mapped[Customer | None] = relationship("Customer")
