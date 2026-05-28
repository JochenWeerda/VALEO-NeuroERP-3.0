"""Auto-generated domain schemas for gdpr requests.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class GdprRequestsOut(BaseSchema):
    """Response schema for gdpr requests endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class GdprRequest(Base):
    __tablename__ = "gdpr_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    subject_id = Column(String(36), nullable=False)
    subject_email = Column(String(255), nullable=False)
    # ACCESS | ERASURE | PORTABILITY | RECTIFICATION
    request_type = Column(String(40), nullable=False)
    # PENDING -> VERIFIED -> PROCESSING -> COMPLETED | REJECTED
    status = Column(String(40), nullable=False, default="PENDING")
    notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    # Stored JSON export payload (small payloads only)
    export_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(String(36), nullable=True)


class GdprRequestCreate(BaseModel):
    subject_id: str = Field(..., description="ID of the data subject")
    subject_email: str = Field(..., description="E-mail of the data subject")
    request_type: str = Field(..., description="ACCESS | ERASURE | PORTABILITY | RECTIFICATION")
    notes: Optional[str] = None


class GdprRequestResponse(BaseModel):
    id: str
    tenant_id: str
    subject_id: str
    subject_email: str
    request_type: str
    status: str
    notes: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    verified_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)

