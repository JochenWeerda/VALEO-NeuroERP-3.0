"""SQLAlchemy models for CRM Service."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CaseStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CaseType(str, Enum):
    INCIDENT = "incident"
    PROBLEM = "problem"
    QUESTION = "question"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"


class SLAStatus(str, Enum):
    ACTIVE = "active"
    BREACHED = "breached"
    WARNING = "warning"
    EXPIRED = "expired"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class Case(Base):
    __tablename__ = "crm_service_cases"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    case_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[CaseStatus] = mapped_column(
        SQLEnum(
            CaseStatus,
            name="crm_service_case_status",
            values_callable=enum_values,
        ),
        default=CaseStatus.NEW,
        nullable=False,
    )

    priority: Mapped[CasePriority] = mapped_column(
        SQLEnum(
            CasePriority,
            name="crm_service_case_priority",
            values_callable=enum_values,
        ),
        default=CasePriority.MEDIUM,
        nullable=False,
    )

    case_type: Mapped[CaseType] = mapped_column(
        SQLEnum(
            CaseType,
            name="crm_service_case_type",
            values_callable=enum_values,
        ),
        default=CaseType.INCIDENT,
        nullable=False,
    )

    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    contact_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(64))
    assigned_by: Mapped[str | None] = mapped_column(String(64))
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime)

    resolution: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolved_by: Mapped[str | None] = mapped_column(String(64))

    sla_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_service_slas.id"))
    sla_breached: Mapped[bool] = mapped_column(default=False)

    category_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_service_categories.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sla: Mapped["SLA | None"] = relationship("SLA")
    category: Mapped["Category | None"] = relationship("Category")
    history: Mapped[list["CaseHistory"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class CaseHistory(Base):
    __tablename__ = "crm_service_case_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_service_cases.id"), nullable=False)

    action: Mapped[str] = mapped_column(String(64), nullable=False)  # created, updated, assigned, resolved, etc.
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    field_name: Mapped[str | None] = mapped_column(String(64))

    performed_by: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    case: Mapped[Case] = relationship(back_populates="history")


class SLA(Base):
    __tablename__ = "crm_service_slas"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    priority: Mapped[CasePriority] = mapped_column(
        SQLEnum(
            CasePriority,
            name="crm_service_sla_priority",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    response_time_hours: Mapped[int] = mapped_column(Integer, default=24)  # Hours to first response
    resolution_time_hours: Mapped[int] = mapped_column(Integer, default=168)  # Hours to resolution (7 days)

    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Category(Base):
    __tablename__ = "crm_service_categories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_service_categories.id"))

    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referencing relationship for subcategories
    parent: Mapped["Category | None"] = relationship("Category", remote_side=[id])
    subcategories: Mapped[list["Category"]] = relationship("Category", back_populates="parent")


class KnowledgeArticle(Base):
    __tablename__ = "crm_service_knowledge_articles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(String(500))

    category_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_service_categories.id"))
    tags: Mapped[str | None] = mapped_column(String(500))  # Comma-separated tags

    is_published: Mapped[bool] = mapped_column(default=False)
    is_featured: Mapped[bool] = mapped_column(default=False)

    view_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)

    category: Mapped[Category | None] = relationship("Category")