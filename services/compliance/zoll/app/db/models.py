"""SQLAlchemy-Modelle für Zoll-/Exportkontrollservice."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ScreeningStatus(str, Enum):
    CLEAR = "clear"
    REVIEW = "review"
    BLOCKED = "blocked"


class ScreeningMatch(Base):
    __tablename__ = "compliance_screening_matches"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    list_name: Mapped[str] = mapped_column(String(128), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[ScreeningStatus] = mapped_column(SAEnum(ScreeningStatus), default=ScreeningStatus.REVIEW)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExportPermitStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ExportPermit(Base):
    __tablename__ = "compliance_export_permits"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    permit_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    country_destination: Mapped[str] = mapped_column(String(2), nullable=False)
    validity_start: Mapped[date] = mapped_column(Date, nullable=False)
    validity_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ExportPermitStatus] = mapped_column(SAEnum(ExportPermitStatus), default=ExportPermitStatus.PENDING)
    goods_description: Mapped[str] = mapped_column(String(255), nullable=False)
    control_list_entries: Mapped[list[str]] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PreferenceCalculation(Base):
    __tablename__ = "compliance_preference_calculations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    bill_of_materials_id: Mapped[str] = mapped_column(String(64), nullable=False)
    agreement_code: Mapped[str] = mapped_column(String(16), nullable=False)
    qualifies: Mapped[bool] = mapped_column(Boolean, default=False)
    originating_value_percent: Mapped[float] = mapped_column(Numeric(6, 2))
    remarks: Mapped[Optional[str]] = mapped_column(String(255))
    calculation_details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PermitDocument(Base):
    __tablename__ = "compliance_export_permit_docs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    permit_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("compliance_export_permits.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(128), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(256), nullable=False)

    permit: Mapped[ExportPermit] = relationship(backref="documents")
