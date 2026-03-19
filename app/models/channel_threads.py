"""
Persistent channel process threads and audit trail records.
"""

from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ChannelProcessThreadRecord(Base):
    __tablename__ = "channel_process_threads"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    thread_id: Mapped[str] = mapped_column(String, primary_key=True)
    kanal: Mapped[str] = mapped_column(String(32), nullable=False)
    tenant_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("domain_shared.tenants.id"),
        nullable=False,
    )
    process_definition_key: Mapped[str] = mapped_column(String(120), nullable=False)
    command_name: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(120), nullable=False)
    rolle: Mapped[str] = mapped_column(String(120), nullable=False)
    issuer_type: Mapped[str] = mapped_column(String(32), nullable=False)
    employee_ref: Mapped[str | None] = mapped_column(String(120))
    channel_user_id: Mapped[str | None] = mapped_column(String(120))
    request_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    execution: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    approval_requirement: Mapped[dict | None] = mapped_column(JSONB)
    approval_record: Mapped[dict | None] = mapped_column(JSONB)
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    audit_items: Mapped[list["ChannelThreadAuditItemRecord"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="ChannelThreadAuditItemRecord.position",
    )


class ChannelThreadAuditItemRecord(Base):
    __tablename__ = "channel_thread_audit_items"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("domain_shared.channel_process_threads.thread_id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    audit_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    recorded_at: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    thread: Mapped[ChannelProcessThreadRecord] = relationship(back_populates="audit_items")
