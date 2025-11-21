"""SQLAlchemy models for CRM Communication Service."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text, Integer, Boolean, JSON, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class EmailStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    COMPLAINT = "complaint"
    UNSUBSCRIBED = "unsubscribed"


class EmailDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class TemplateType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    LETTER = "letter"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class Email(Base):
    __tablename__ = "crm_communication_emails"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    message_id: Mapped[str] = mapped_column(String(255), unique=True)  # Email Message-ID header
    thread_id: Mapped[str] = mapped_column(String(255), index=True)  # Conversation thread

    direction: Mapped[EmailDirection] = mapped_column(
        SQLEnum(
            EmailDirection,
            name="crm_communication_email_direction",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_addresses: Mapped[list[str]] = mapped_column(JSON, nullable=False)  # List of recipients
    cc_addresses: Mapped[list[str] | None] = mapped_column(JSON)
    bcc_addresses: Mapped[list[str] | None] = mapped_column(JSON)

    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_html: Mapped[str | None] = mapped_column(Text)
    body_text: Mapped[str | None] = mapped_column(Text)

    status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(
            EmailStatus,
            name="crm_communication_email_status",
            values_callable=enum_values,
        ),
        default=EmailStatus.DRAFT,
        nullable=False,
    )

    # CRM Context
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)
    lead_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)
    case_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)
    opportunity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)

    # Template and Campaign
    template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_communication_templates.id"))
    campaign_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_communication_campaigns.id"))

    # Tracking
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Metadata
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template: Mapped["Template"] = relationship("Template", back_populates="emails")
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="emails")
    attachments: Mapped[list["Attachment"]] = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")


class Template(Base):
    __tablename__ = "crm_communication_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[TemplateType] = mapped_column(
        SQLEnum(
            TemplateType,
            name="crm_communication_template_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    subject_template: Mapped[str | None] = mapped_column(String(500))
    body_template: Mapped[str] = mapped_column(Text, nullable=False)

    variables: Mapped[dict] = mapped_column(JSON, default=dict)  # Available merge variables
    sample_data: Mapped[dict] = mapped_column(JSON, default=dict)  # Sample data for preview

    is_active: Mapped[bool] = mapped_column(default=True)
    is_default: Mapped[bool] = mapped_column(default=False)

    category: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    emails: Mapped[list[Email]] = relationship("Email", back_populates="template")


class Campaign(Base):
    __tablename__ = "crm_communication_campaigns"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    template_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_communication_templates.id"), nullable=False)

    status: Mapped[CampaignStatus] = mapped_column(
        SQLEnum(
            CampaignStatus,
            name="crm_communication_campaign_status",
            values_callable=enum_values,
        ),
        default=CampaignStatus.DRAFT,
        nullable=False,
    )

    # Targeting
    target_filters: Mapped[dict] = mapped_column(JSON, default=dict)  # Filters for target audience
    target_count: Mapped[int | None] = mapped_column(Integer)

    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Results
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0)
    opened_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_count: Mapped[int] = mapped_column(Integer, default=0)
    bounced_count: Mapped[int] = mapped_column(Integer, default=0)
    unsubscribed_count: Mapped[int] = mapped_column(Integer, default=0)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    template: Mapped[Template] = relationship("Template")
    emails: Mapped[list[Email]] = relationship("Email", back_populates="campaign")


class Attachment(Base):
    __tablename__ = "crm_communication_attachments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_communication_emails.id"), nullable=False)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    # File content stored as binary
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # Metadata
    inline: Mapped[bool] = mapped_column(default=False)  # Inline vs attachment
    content_id: Mapped[str | None] = mapped_column(String(255))  # For inline images

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    email: Mapped[Email] = relationship("Email", back_populates="attachments")


class Automation(Base):
    __tablename__ = "crm_communication_automations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    trigger_conditions: Mapped[dict] = mapped_column(JSON, nullable=False)  # When to trigger
    actions: Mapped[list[dict]] = mapped_column(JSON, nullable=False)  # What to do

    is_active: Mapped[bool] = mapped_column(default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    # Statistics
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)