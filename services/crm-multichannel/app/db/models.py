"""SQLAlchemy models for CRM Multi-Channel Integration Service."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChannelType(str, Enum):
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    WEBSITE = "website"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    STRIPE = "stripe"
    ERP = "erp"


class ChannelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    LINK = "link"
    FORM = "form"
    PAYMENT = "payment"
    ORDER = "order"


class ConversationStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    ESCALATED = "escalated"


class FormFieldType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  ***REMOVED*** noqa: E731


class Channel(Base):
    __tablename__ = "crm_multichannel_channels"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[ChannelType] = mapped_column(
        SQLEnum(
            ChannelType,
            name="crm_multichannel_channel_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    status: Mapped[ChannelStatus] = mapped_column(
        SQLEnum(
            ChannelStatus,
            name="crm_multichannel_channel_status",
            values_callable=enum_values,
        ),
        default=ChannelStatus.PENDING,
        nullable=False,
    )

    ***REMOVED*** Channel-specific configuration
    config: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** API keys, webhook URLs, etc.
    credentials: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** Encrypted credentials

    ***REMOVED*** Channel identifiers
    external_id: Mapped[str | None] = mapped_column(String(255))  ***REMOVED*** Facebook Page ID, Twitter Handle, etc.
    webhook_url: Mapped[str | None] = mapped_column(String(500))

    ***REMOVED*** Statistics
    messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    messages_received: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[datetime | None] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="channel")


class Conversation(Base):
    __tablename__ = "crm_multichannel_conversations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    channel_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_multichannel_channels.id"), nullable=False)

    ***REMOVED*** External conversation identifiers
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)  ***REMOVED*** Facebook Conversation ID, etc.
    thread_id: Mapped[str | None] = mapped_column(String(255))  ***REMOVED*** For threaded conversations

    ***REMOVED*** Customer association
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    contact_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    lead_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))

    ***REMOVED*** Conversation metadata
    subject: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(
            ConversationStatus,
            name="crm_multichannel_conversation_status",
            values_callable=enum_values,
        ),
        default=ConversationStatus.OPEN,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(String(16), default="normal")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    ***REMOVED*** Assignment
    assigned_to: Mapped[str | None] = mapped_column(String(64))
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime)

    ***REMOVED*** Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_message_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    ***REMOVED*** Statistics
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    customer_message_count: Mapped[int] = mapped_column(Integer, default=0)
    agent_message_count: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channel: Mapped[Channel] = relationship("Channel", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "crm_multichannel_messages"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    conversation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_multichannel_conversations.id"), nullable=False)

    ***REMOVED*** External message identifiers
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_parent_id: Mapped[str | None] = mapped_column(String(255))  ***REMOVED*** For replies

    direction: Mapped[MessageDirection] = mapped_column(
        SQLEnum(
            MessageDirection,
            name="crm_multichannel_message_direction",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    type: Mapped[MessageType] = mapped_column(
        SQLEnum(
            MessageType,
            name="crm_multichannel_message_type",
            values_callable=enum_values,
        ),
        default=MessageType.TEXT,
        nullable=False,
    )

    ***REMOVED*** Message content
    content: Mapped[str | None] = mapped_column(Text)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** URLs, attachments, etc.

    ***REMOVED*** Sender information
    sender_id: Mapped[str | None] = mapped_column(String(255))  ***REMOVED*** External sender ID
    sender_name: Mapped[str | None] = mapped_column(String(255))
    sender_type: Mapped[str] = mapped_column(String(32), default="customer")  ***REMOVED*** customer, agent, system

    ***REMOVED*** Processing status
    is_read: Mapped[bool] = mapped_column(default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)
    read_at: Mapped[datetime | None] = mapped_column(DateTime)

    ***REMOVED*** Agent assignment
    handled_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")


class WebForm(Base):
    __tablename__ = "crm_multichannel_webforms"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    ***REMOVED*** Form configuration
    fields: Mapped[list[dict]] = mapped_column(JSON, nullable=False)  ***REMOVED*** Field definitions
    settings: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** Form settings (theme, validation, etc.)

    ***REMOVED*** Publishing
    slug: Mapped[str] = mapped_column(String(255), unique=True)  ***REMOVED*** URL slug
    is_published: Mapped[bool] = mapped_column(default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)

    ***REMOVED*** Integration
    lead_source: Mapped[str | None] = mapped_column(String(64))  ***REMOVED*** Marketing campaign, etc.
    auto_create_lead: Mapped[bool] = mapped_column(default=True)
    notification_emails: Mapped[list[str]] = mapped_column(JSON, default=list)

    ***REMOVED*** Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    submission_count: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[float | None] = mapped_column(Float)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submissions: Mapped[list["FormSubmission"]] = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")


class FormSubmission(Base):
    __tablename__ = "crm_multichannel_submissions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    form_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_multichannel_webforms.id"), nullable=False)

    ***REMOVED*** Submission data
    data: Mapped[dict] = mapped_column(JSON, nullable=False)  ***REMOVED*** Form field values
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** IP, user agent, etc.

    ***REMOVED*** Lead creation
    lead_created: Mapped[bool] = mapped_column(default=False)
    lead_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))

    ***REMOVED*** Processing
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
    processing_status: Mapped[str] = mapped_column(String(32), default="pending")

    ***REMOVED*** Source tracking
    source_url: Mapped[str | None] = mapped_column(String(500))
    referrer: Mapped[str | None] = mapped_column(String(500))
    utm_parameters: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    form: Mapped[WebForm] = relationship("WebForm", back_populates="submissions")


class Integration(Base):
    __tablename__ = "crm_multichannel_integrations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)  ***REMOVED*** shopify, woocommerce, stripe, erp

    ***REMOVED*** Connection configuration
    config: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** API endpoints, credentials
    credentials: Mapped[dict] = mapped_column(JSON, default=dict)  ***REMOVED*** Encrypted credentials

    ***REMOVED*** Status and health
    status: Mapped[str] = mapped_column(String(32), default="disconnected")  ***REMOVED*** connected, disconnected, error
    last_sync: Mapped[datetime | None] = mapped_column(DateTime)
    last_error: Mapped[str | None] = mapped_column(Text)

    ***REMOVED*** Sync configuration
    sync_enabled: Mapped[bool] = mapped_column(default=True)
    sync_frequency: Mapped[int] = mapped_column(Integer, default=3600)  ***REMOVED*** seconds
    sync_entities: Mapped[list[str]] = mapped_column(JSON, default=list)  ***REMOVED*** customers, orders, products

    ***REMOVED*** Statistics
    records_synced: Mapped[int] = mapped_column(Integer, default=0)
    last_record_count: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)