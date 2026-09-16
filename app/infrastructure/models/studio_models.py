"""Studio ScreenDefinition drafts (UIX-090 / MERIDIAN-SCREEN-STUDIO)."""

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class ScreenDefinitionDraft(Base):
    """Tenant-scoped ScreenDefinition draft with four-eyes publish."""

    __tablename__ = "screen_definition_drafts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "screen_id", name="uq_screen_definition_drafts_tenant_screen"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id", ondelete="CASCADE"), nullable=False)
    screen_id = Column(String(96), nullable=False)
    base_screen_id = Column(String(96), nullable=True)
    definition = Column(JSONB, nullable=False)
    status = Column(String(16), nullable=False, default="draft")
    readiness = Column(JSONB, nullable=True)
    created_by = Column(String(64), nullable=False)
    updated_by = Column(String(64), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
