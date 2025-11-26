"""SQLAlchemy models for CRM Marketing."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, Text, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SegmentType(str, Enum):
    """Types of segments."""
    DYNAMIC = "dynamic"  # Rule-based, automatically calculated
    STATIC = "static"  # Manually managed
    HYBRID = "hybrid"  # Combination of rules and manual members


class SegmentStatus(str, Enum):
    """Status of segment."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class RuleOperator(str, Enum):
    """Operators for segment rules."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"


class LogicalOperator(str, Enum):
    """Logical operators for combining rules."""
    AND = "AND"
    OR = "OR"


class Segment(Base):
    """Marketing segment."""
    __tablename__ = "crm_marketing_segments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # Segment type and status
    type: Mapped[SegmentType] = mapped_column(SQLEnum(SegmentType), nullable=False)
    status: Mapped[SegmentStatus] = mapped_column(SQLEnum(SegmentStatus), nullable=False, default=SegmentStatus.ACTIVE)
    
    # Rules (for dynamic segments)
    rules: Mapped[dict | None] = mapped_column(JSONB)  # JSON structure for rules
    
    # Cached metrics
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    last_calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
    
    # Relationships
    segment_rules: Mapped[list["SegmentRule"]] = relationship(
        "SegmentRule",
        back_populates="segment",
        cascade="all, delete-orphan",
        order_by="SegmentRule.order"
    )
    members: Mapped[list["SegmentMember"]] = relationship(
        "SegmentMember",
        back_populates="segment",
        cascade="all, delete-orphan"
    )
    performance: Mapped[list["SegmentPerformance"]] = relationship(
        "SegmentPerformance",
        back_populates="segment",
        cascade="all, delete-orphan"
    )


class SegmentRule(Base):
    """Rule for dynamic segment calculation."""
    __tablename__ = "crm_marketing_segment_rules"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    segment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_segments.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Rule definition
    field: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "contact.email_domain", "customer.category"
    operator: Mapped[RuleOperator] = mapped_column(SQLEnum(RuleOperator), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB)  # Can be single value or array
    
    # Logical combination
    logical_operator: Mapped[LogicalOperator | None] = mapped_column(SQLEnum(LogicalOperator))  # AND/OR with previous rule
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # Order of rule evaluation
    
    # Relationships
    segment: Mapped["Segment"] = relationship("Segment", back_populates="segment_rules")


class SegmentMember(Base):
    """Member of a segment (contact)."""
    __tablename__ = "crm_marketing_segment_members"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    segment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_segments.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Membership tracking
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    added_by: Mapped[str | None] = mapped_column(String(255))  # User ID or "system" for dynamic segments
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    removed_by: Mapped[str | None] = mapped_column(String(255))
    
    # Relationships
    segment: Mapped["Segment"] = relationship("Segment", back_populates="members")


class SegmentPerformance(Base):
    """Performance metrics for a segment."""
    __tablename__ = "crm_marketing_segment_performance"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    segment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_segments.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time period
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False, default="daily")  # daily, weekly, monthly
    
    # Metrics
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    active_members: Mapped[int] = mapped_column(Integer, default=0)
    campaign_count: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))  # Percentage
    revenue: Mapped[float | None] = mapped_column(Numeric(12, 2))  # Optional revenue attribution
    
    # Relationships
    segment: Mapped["Segment"] = relationship("Segment", back_populates="performance")


class CampaignType(str, Enum):
    """Types of campaigns."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SOCIAL = "social"


class CampaignStatus(str, Enum):
    """Status of campaign."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecipientStatus(str, Enum):
    """Status of campaign recipient."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    FAILED = "failed"


class CampaignEventType(str, Enum):
    """Types of campaign events."""
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    CONVERTED = "converted"


class Campaign(Base):
    """Marketing campaign."""
    __tablename__ = "crm_marketing_campaigns"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[CampaignType] = mapped_column(SQLEnum(CampaignType), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(SQLEnum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)
    
    # Targeting
    segment_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_segments.id"), nullable=True, index=True)
    template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaign_templates.id"), nullable=True, index=True)
    
    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Budget
    budget: Mapped[float | None] = mapped_column(Numeric(12, 2))
    spent: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    
    # Metrics (cached)
    target_count: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0)
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    conversion_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
    
    # Relationships
    segment: Mapped["Segment | None"] = relationship("Segment")
    template: Mapped["CampaignTemplate | None"] = relationship("CampaignTemplate")
    variants: Mapped[list["CampaignVariant"]] = relationship("CampaignVariant", back_populates="campaign", cascade="all, delete-orphan")
    recipients: Mapped[list["CampaignRecipient"]] = relationship("CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan")
    events: Mapped[list["CampaignEvent"]] = relationship("CampaignEvent", back_populates="campaign", cascade="all, delete-orphan")
    performance: Mapped[list["CampaignPerformance"]] = relationship("CampaignPerformance", back_populates="campaign", cascade="all, delete-orphan")


class CampaignTemplate(Base):
    """Campaign template."""
    __tablename__ = "crm_marketing_campaign_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[CampaignType] = mapped_column(SQLEnum(CampaignType), nullable=False)
    
    # Content
    subject: Mapped[str | None] = mapped_column(String(500))  # For email
    body_html: Mapped[str | None] = mapped_column(Text)
    body_text: Mapped[str | None] = mapped_column(Text)
    
    # Variables
    variables: Mapped[dict | None] = mapped_column(JSONB)  # JSON structure for personalization
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="template")


class CampaignVariant(Base):
    """Campaign variant for A/B testing."""
    __tablename__ = "crm_marketing_campaign_variants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Variant info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    variant_type: Mapped[str] = mapped_column(String(10), nullable=False)  # A, B, C, etc.
    
    # Template
    template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaign_templates.id"), nullable=True)
    
    # Distribution
    target_percentage: Mapped[int] = mapped_column(Integer, default=50)  # Percentage of recipients
    
    # Metrics
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    conversion_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Winner
    winner: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="variants")
    recipients: Mapped[list["CampaignRecipient"]] = relationship("CampaignRecipient", back_populates="variant")


class CampaignRecipient(Base):
    """Campaign recipient."""
    __tablename__ = "crm_marketing_campaign_recipients"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    variant_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaign_variants.id"), nullable=True, index=True)
    
    # Contact info (cached)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    
    # Status
    status: Mapped[RecipientStatus] = mapped_column(SQLEnum(RecipientStatus), nullable=False, default=RecipientStatus.PENDING)
    
    # Timestamps
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Metrics
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Errors
    bounce_reason: Mapped[str | None] = mapped_column(Text)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="recipients")
    variant: Mapped["CampaignVariant | None"] = relationship("CampaignVariant", back_populates="recipients")
    events: Mapped[list["CampaignEvent"]] = relationship("CampaignEvent", back_populates="recipient")


class CampaignEvent(Base):
    """Campaign tracking event."""
    __tablename__ = "crm_marketing_campaign_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaign_recipients.id"), nullable=True, index=True)
    
    # Event info
    event_type: Mapped[CampaignEventType] = mapped_column(SQLEnum(CampaignEventType), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Metadata
    metadata: Mapped[dict | None] = mapped_column(JSONB)  # IP, User-Agent, Link-URL, etc.
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="events")
    recipient: Mapped["CampaignRecipient | None"] = relationship("CampaignRecipient", back_populates="events")


class CampaignPerformance(Base):
    """Performance metrics for a campaign."""
    __tablename__ = "crm_marketing_campaign_performance"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_marketing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time period
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Metrics
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0)
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    conversion_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Rates
    open_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))  # Percentage
    click_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))  # Percentage
    conversion_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))  # Percentage
    
    # Revenue
    revenue: Mapped[float | None] = mapped_column(Numeric(12, 2))
    roi: Mapped[float | None] = mapped_column(Numeric(5, 2))  # Percentage
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="performance")

