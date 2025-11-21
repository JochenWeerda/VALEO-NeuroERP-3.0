"""SQLAlchemy models for CRM Sales."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OpportunityStatus(str, Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityStage(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    NEEDS_ANALYSIS = "needs_analysis"
    VALUE_PROPOSITION = "value_proposition"
    IDENTIFY_DECISION_MAKERS = "identify_decision_makers"
    PROPOSAL_PRICE_QUOTE = "proposal_price_quote"
    NEGOTIATION_REVIEW = "negotiation_review"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class Opportunity(Base):
    __tablename__ = "crm_sales_opportunities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[float | None] = mapped_column(Float)
    probability: Mapped[float | None] = mapped_column(Float, default=0.0)
    expected_close_date: Mapped[datetime | None] = mapped_column(DateTime)
    actual_close_date: Mapped[datetime | None] = mapped_column(DateTime)

    status: Mapped[OpportunityStatus] = mapped_column(
        SQLEnum(
            OpportunityStatus,
            name="crm_sales_opportunity_status",
            values_callable=enum_values,
        ),
        default=OpportunityStatus.PROSPECTING,
        nullable=False,
    )

    stage: Mapped[OpportunityStage] = mapped_column(
        SQLEnum(
            OpportunityStage,
            name="crm_sales_opportunity_stage",
            values_callable=enum_values,
        ),
        default=OpportunityStage.INITIAL_CONTACT,
        nullable=False,
    )

    lead_source: Mapped[str | None] = mapped_column(String(128))
    assigned_to: Mapped[str | None] = mapped_column(String(64))
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    contact_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    quotes: Mapped[list["Quote"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")


class Quote(Base):
    __tablename__ = "crm_sales_quotes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    quote_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    opportunity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_sales_opportunities.id"), nullable=True)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    contact_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)

    valid_until: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    assigned_to: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    opportunity: Mapped[Opportunity | None] = relationship(back_populates="quotes")
    line_items: Mapped[list["QuoteLineItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")


class QuoteLineItem(Base):
    __tablename__ = "crm_sales_quote_line_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    quote_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_sales_quotes.id"), nullable=False)
    product_id: Mapped[str | None] = mapped_column(String(64))
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
    line_total: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    quote: Mapped[Quote] = relationship(back_populates="line_items")


class SalesActivity(Base):
    __tablename__ = "crm_sales_activities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    opportunity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_sales_opportunities.id"), nullable=True)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    contact_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    activity_type: Mapped[str] = mapped_column(String(32), nullable=False)  # call, meeting, email, demo, etc.
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="planned")  # planned, completed, cancelled
    priority: Mapped[str] = mapped_column(String(16), default="medium")  # high, medium, low

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_minutes: Mapped[int | None] = mapped_column(Float)

    assigned_to: Mapped[str | None] = mapped_column(String(64))
    outcome: Mapped[str | None] = mapped_column(Text)  # Result of the activity

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    opportunity: Mapped[Opportunity | None] = relationship("Opportunity")