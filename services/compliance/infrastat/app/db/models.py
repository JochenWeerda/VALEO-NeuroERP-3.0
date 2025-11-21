"""SQLAlchemy-Modelle für InfraStat."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DeclarationStatus(str, Enum):
    COLLECTING = "collecting"
    VALIDATING = "validating"
    READY = "ready"
    SUBMITTED = "submitted"
    ERROR = "error"
    ARCHIVED = "archived"


class DeclarationBatch(Base):
    __tablename__ = "infrastat_declaration_batches"
    __table_args__ = (
        UniqueConstraint("tenant_id", "reference_period", "flow_type", name="uq_batch_period_flow"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    flow_type: Mapped[str] = mapped_column(String(8), nullable=False)  # arrival / dispatch
    reference_period: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[DeclarationStatus] = mapped_column(Enum(DeclarationStatus), default=DeclarationStatus.COLLECTING)
    total_value_eur: Mapped[Optional[float]] = mapped_column(Numeric(16, 2))
    total_weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(16, 3))
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lines: Mapped[list["DeclarationLine"]] = relationship(back_populates="batch", cascade="all, delete-orphan")
    validation_errors: Mapped[list["ValidationError"]] = relationship(back_populates="batch", cascade="all, delete-orphan")
    submissions: Mapped[list["SubmissionLog"]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class DeclarationLine(Base):
    __tablename__ = "infrastat_declaration_lines"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    batch_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("infrastat_declaration_batches.id"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    commodity_code: Mapped[str] = mapped_column(String(10), nullable=False)
    country_of_origin: Mapped[str] = mapped_column(String(2), nullable=False)
    country_of_destination: Mapped[str] = mapped_column(String(2), nullable=False)
    net_mass_kg: Mapped[float] = mapped_column(Numeric(16, 3), nullable=False)
    supplementary_units: Mapped[Optional[float]] = mapped_column(Numeric(16, 3))
    invoice_value_eur: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False)
    statistical_value_eur: Mapped[Optional[float]] = mapped_column(Numeric(16, 2))
    nature_of_transaction: Mapped[str] = mapped_column(String(2), nullable=False)
    transport_mode: Mapped[str] = mapped_column(String(1), nullable=False)
    delivery_terms: Mapped[Optional[str]] = mapped_column(String(3))
    line_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"))

    batch: Mapped["DeclarationBatch"] = relationship(back_populates="lines")


class ValidationError(Base):
    __tablename__ = "infrastat_validation_errors"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    batch_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("infrastat_declaration_batches.id"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    line_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("infrastat_declaration_lines.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(String(512), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    batch: Mapped["DeclarationBatch"] = relationship(back_populates="validation_errors")
    line: Mapped[Optional["DeclarationLine"]] = relationship()


class SubmissionLog(Base):
    __tablename__ = "infrastat_submission_log"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    batch_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("infrastat_declaration_batches.id"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submission_channel: Mapped[str] = mapped_column(String(32), nullable=False, default="idev")
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_number: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    response_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    success: Mapped[bool] = mapped_column(Boolean, default=False)

    batch: Mapped["DeclarationBatch"] = relationship(back_populates="submissions")

