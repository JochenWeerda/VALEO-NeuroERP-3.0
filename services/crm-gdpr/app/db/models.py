"""SQLAlchemy models for CRM GDPR."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GDPRRequestType(str, Enum):
    """Types of GDPR requests."""
    ACCESS = "access"  # Art. 15 - Right of access
    DELETION = "deletion"  # Art. 17 - Right to erasure
    PORTABILITY = "portability"  # Art. 20 - Right to data portability
    OBJECTION = "objection"  # Art. 21 - Right to object


class GDPRRequestStatus(str, Enum):
    """Status of GDPR request."""
    PENDING = "pending"  # Awaiting verification
    IN_PROGRESS = "in_progress"  # Being processed
    COMPLETED = "completed"  # Successfully completed
    REJECTED = "rejected"  # Rejected (with reason)
    CANCELLED = "cancelled"  # Cancelled by requester


class VerificationMethod(str, Enum):
    """Methods for identity verification."""
    EMAIL = "email"  # Email verification
    ID_CARD = "id_card"  # ID card upload
    MANUAL = "manual"  # Manual verification by officer
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
    
    # Request details
    request_type: Mapped[GDPRRequestType] = mapped_column(SQLEnum(GDPRRequestType), nullable=False)
    contact_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Status
    status: Mapped[GDPRRequestStatus] = mapped_column(SQLEnum(GDPRRequestStatus), nullable=False, default=GDPRRequestStatus.PENDING)
    
    # Timestamps
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Requester
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False)  # User ID or contact email
    is_self_request: Mapped[bool] = mapped_column(Boolean, default=True)  # Requested by data subject themselves
    
    # Verification
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_method: Mapped[VerificationMethod | None] = mapped_column(SQLEnum(VerificationMethod))
    verification_token: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True)
    
    # Response data
    response_data: Mapped[dict | None] = mapped_column(JSONB)  # Exported data (JSON)
    response_file_path: Mapped[str | None] = mapped_column(String(512))  # Path to export file
    response_file_format: Mapped[str | None] = mapped_column(String(10))  # json, csv, pdf
    
    # Rejection
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    
    # Notes
    notes: Mapped[str | None] = mapped_column(Text)  # Internal notes
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
    
    # Relationships
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
    
    # Change details
    action: Mapped[GDPRRequestHistoryAction] = mapped_column(SQLEnum(GDPRRequestHistoryAction), nullable=False)
    old_status: Mapped[GDPRRequestStatus | None] = mapped_column(SQLEnum(GDPRRequestStatus))
    new_status: Mapped[GDPRRequestStatus | None] = mapped_column(SQLEnum(GDPRRequestStatus))
    
    # Notes
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Metadata
    changed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    request: Mapped["GDPRRequest"] = relationship("GDPRRequest", back_populates="history")


class PrivacyErasureDecision(Base):
    """Aus evaluate: versionierte Policy-Decision (Referenz zu GDPR-Antrag)."""

    __tablename__ = "crm_privacy_erasure_decisions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    gdpr_request_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

    decision: Mapped[str] = mapped_column(String(64), nullable=False)
    allowed_actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    blocked_actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    reasons: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    policy_version: Mapped[str] = mapped_column(String(128), nullable=False)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    anonymize_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    correlation_id_evaluate: Mapped[str] = mapped_column(String(128), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PrivacyErasureAudit(Base):
    """Append-only Privacy/Erasure-Audit (keine Updates aus dem Anwendungscode)."""

    __tablename__ = "crm_privacy_erasure_audit"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    gdpr_request_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)
    decision_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(255))

    policy_version: Mapped[str] = mapped_column(String(128), nullable=False)
    decision: Mapped[str | None] = mapped_column(String(64))
    reason_codes: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    allowed_actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    blocked_actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    executed_action: Mapped[str | None] = mapped_column(String(128))
    result: Mapped[str] = mapped_column(String(64), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    extra: Mapped[dict | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class PrivacyErasureExecution(Base):
    """Erfolgreiche Execute-Operationen für Idempotenz und Delete-Gate."""

    __tablename__ = "crm_privacy_erasure_executions"

    idempotency_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    gdpr_request_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    subject_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    decision_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    anonymize_only: Mapped[bool] = mapped_column(Boolean, nullable=False)

    erasure_log: Mapped[dict | None] = mapped_column(JSONB)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
