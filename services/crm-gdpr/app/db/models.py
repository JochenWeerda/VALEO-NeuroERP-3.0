"""SQLAlchemy models for CRM GDPR."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GDPRRequestType(str, Enum):
    """Types of GDPR requests."""
    ACCESS = "access"  ***REMOVED*** Art. 15 - Right of access
    DELETION = "deletion"  ***REMOVED*** Art. 17 - Right to erasure
    PORTABILITY = "portability"  ***REMOVED*** Art. 20 - Right to data portability
    OBJECTION = "objection"  ***REMOVED*** Art. 21 - Right to object


class GDPRRequestStatus(str, Enum):
    """Status of GDPR request."""
    PENDING = "pending"  ***REMOVED*** Awaiting verification
    IN_PROGRESS = "in_progress"  ***REMOVED*** Being processed
    COMPLETED = "completed"  ***REMOVED*** Successfully completed
    REJECTED = "rejected"  ***REMOVED*** Rejected (with reason)
    CANCELLED = "cancelled"  ***REMOVED*** Cancelled by requester


class VerificationMethod(str, Enum):
    """Methods for identity verification."""
    EMAIL = "email"  ***REMOVED*** Email verification
    ID_CARD = "id_card"  ***REMOVED*** ID card upload
    MANUAL = "manual"  ***REMOVED*** Manual verification by officer
    OTHER = "other"


class GDPRRequestHistoryAction(str, Enum):
    """Actions in GDPR request history."""
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    VERIFIED = "verified"
    DATA_EXPORTED = "data_exported"
    DATA_DELETED = "data_deleted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class GDPRRequest(Base):
    """GDPR request record."""
    __tablename__ = "crm_gdpr_requests"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    ***REMOVED*** Request details
    request_type: Mapped[GDPRRequestType] = mapped_column(SQLEnum(GDPRRequestType), nullable=False)
    contact_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    ***REMOVED*** Status
    status: Mapped[GDPRRequestStatus] = mapped_column(SQLEnum(GDPRRequestStatus), nullable=False, default=GDPRRequestStatus.PENDING)
    
    ***REMOVED*** Timestamps
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    ***REMOVED*** Requester
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False)  ***REMOVED*** User ID or contact email
    is_self_request: Mapped[bool] = mapped_column(Boolean, default=True)  ***REMOVED*** Requested by data subject themselves
    
    ***REMOVED*** Verification
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_method: Mapped[VerificationMethod | None] = mapped_column(SQLEnum(VerificationMethod))
    verification_token: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True)
    
    ***REMOVED*** Response data
    response_data: Mapped[dict | None] = mapped_column(JSONB)  ***REMOVED*** Exported data (JSON)
    response_file_path: Mapped[str | None] = mapped_column(String(512))  ***REMOVED*** Path to export file
    response_file_format: Mapped[str | None] = mapped_column(String(10))  ***REMOVED*** json, csv, pdf
    
    ***REMOVED*** Rejection
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    
    ***REMOVED*** Notes
    notes: Mapped[str | None] = mapped_column(Text)  ***REMOVED*** Internal notes
    
    ***REMOVED*** Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
    
    ***REMOVED*** Relationships
    history: Mapped[list["GDPRRequestHistory"]] = relationship(
        "GDPRRequestHistory",
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="GDPRRequestHistory.changed_at.desc()"
    )


class GDPRRequestHistory(Base):
    """History of GDPR request changes (revision-safe audit trail)."""
    __tablename__ = "crm_gdpr_request_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_gdpr_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    ***REMOVED*** Change details
    action: Mapped[GDPRRequestHistoryAction] = mapped_column(SQLEnum(GDPRRequestHistoryAction), nullable=False)
    old_status: Mapped[GDPRRequestStatus | None] = mapped_column(SQLEnum(GDPRRequestStatus))
    new_status: Mapped[GDPRRequestStatus | None] = mapped_column(SQLEnum(GDPRRequestStatus))
    
    ***REMOVED*** Notes
    notes: Mapped[str | None] = mapped_column(Text)
    
    ***REMOVED*** Metadata
    changed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    ***REMOVED*** Relationships
    request: Mapped["GDPRRequest"] = relationship("GDPRRequest", back_populates="history")

