"""OPERATOR-AGENT-002 — SQLAlchemy-Modell für persistente Agent-Proposals."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AgentProposalRecord(Base):
    """Persistente Speicherung von Operator-Agent-Proposals."""

    __tablename__ = "agent_proposals"

    proposal_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    context_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    execution_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_agent_proposals_tenant_status", "tenant_id", "approval_status"),
        Index("ix_agent_proposals_tenant_created", "tenant_id", "created_at"),
    )
