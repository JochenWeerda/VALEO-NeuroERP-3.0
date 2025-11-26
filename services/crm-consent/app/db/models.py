"""SQLAlchemy models for CRM Consent."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ConsentChannel(str, Enum):
    """Communication channels."""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    POSTAL = "postal"


class ConsentType(str, Enum):
    """Types of consent."""
    MARKETING = "marketing"
    SERVICE = "service"
    REQUIRED = "required"  # Required for service delivery


class ConsentStatus(str, Enum):
    """Consent status."""
    PENDING = "pending"  # Awaiting double opt-in confirmation
    GRANTED = "granted"  # Active consent
    DENIED = "denied"  # Explicitly denied
    REVOKED = "revoked"  # Previously granted, now revoked


class ConsentSource(str, Enum):
    """Source of consent."""
    WEB_FORM = "web_form"
    API = "api"
    IMPORT = "import"
    MANUAL = "manual"


class ConsentHistoryAction(str, Enum):
    """Actions in consent history."""
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    UPDATED = "updated"


class Consent(Base):
    """Consent record for a contact/customer."""
    __tablename__ = "crm_consent_consents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Contact reference
    contact_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Consent details
    channel: Mapped[ConsentChannel] = mapped_column(SQLEnum(ConsentChannel), nullable=False)
    consent_type: Mapped[ConsentType] = mapped_column(SQLEnum(ConsentType), nullable=False)
    status: Mapped[ConsentStatus] = mapped_column(SQLEnum(ConsentStatus), nullable=False, default=ConsentStatus.PENDING)
    
    # Timestamps
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    denied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Double opt-in
    double_opt_in_token: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True)
    double_opt_in_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Metadata
    source: Mapped[ConsentSource] = mapped_column(SQLEnum(ConsentSource), nullable=False, default=ConsentSource.MANUAL)
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 compatible
    user_agent: Mapped[str | None] = mapped_column(Text)
    
    # Optional expiry
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
    
    # Relationships
    history: Mapped[list["ConsentHistory"]] = relationship(
        "ConsentHistory",
        back_populates="consent",
        cascade="all, delete-orphan",
        order_by="ConsentHistory.changed_at.desc()"
    )


class ConsentHistory(Base):
    """History of consent changes (revision-safe audit trail)."""
    __tablename__ = "crm_consent_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    consent_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_consent_consents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Change details
    action: Mapped[ConsentHistoryAction] = mapped_column(SQLEnum(ConsentHistoryAction), nullable=False)
    old_status: Mapped[ConsentStatus | None] = mapped_column(SQLEnum(ConsentStatus))
    new_status: Mapped[ConsentStatus] = mapped_column(SQLEnum(ConsentStatus), nullable=False)
    
    # Reason (optional)
    reason: Mapped[str | None] = mapped_column(Text)
    
    # Metadata
    changed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    
    # Relationships
    consent: Mapped["Consent"] = relationship("Consent", back_populates="history")

