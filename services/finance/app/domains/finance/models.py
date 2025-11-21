"""SQLAlchemy models for the Finance domain."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.finance.app.core.database import Base


class Account(Base):
    """Chart of Accounts entry."""

    __tablename__ = "finance_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    account_number: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(64), default=None)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    journal_entries: Mapped[list["JournalEntry"]] = relationship(back_populates="account")


class JournalEntry(Base):
    """Journal entries (Primanota)."""

    __tablename__ = "finance_journal_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("finance_accounts.id"))
    description: Mapped[str] = mapped_column(String(512))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    period: Mapped[str] = mapped_column(String(16))
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(64))

    account: Mapped[Account] = relationship(back_populates="journal_entries")


class OpenItem(Base):
    """Open items (Debtors)."""

    __tablename__ = "finance_open_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    document_number: Mapped[str] = mapped_column(String(64))
    customer_id: Mapped[str] = mapped_column(String(64))
    customer_name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


