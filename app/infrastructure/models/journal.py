"""
Journal entry ORM models in a dedicated module to avoid registry name clashes
with Pydantic/schema classes named JournalEntry/JournalEntryLine.
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class JournalEntryLine(Base):
    """Journal entry line model – nutzt domain_erp.journal_entry_lines (chart_of_accounts)."""
    __tablename__ = "journal_entry_lines"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    journal_entry_id = Column(String, ForeignKey("domain_erp.journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("domain_erp.chart_of_accounts.id", use_alter=True), nullable=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    debit = Column(DECIMAL(15, 2), default=0)
    credit = Column(DECIMAL(15, 2), default=0)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    journal_entry = relationship(
        "JournalEntry",
        back_populates="lines",
        foreign_keys=[journal_entry_id],
    )


class JournalEntry(Base):
    """Journal entry model – nutzt domain_erp.journal_entries (eine Tabelle für List + Connector)."""
    __tablename__ = "journal_entries"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    entry_number = Column(String(20), nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    posting_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(200), nullable=False)
    reference = Column(String(50), nullable=True)
    source = Column(String(50), nullable=True)
    document_type = Column(String(30), nullable=True)  # RE, GU, AB etc. (GoBD Belegart)
    status = Column(String(20), default="draft")
    total_debit = Column(DECIMAL(15, 2), default=0)
    total_credit = Column(DECIMAL(15, 2), default=0)
    posted_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    reversed_entry_id = Column(String, ForeignKey("domain_erp.journal_entries.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lines = relationship(
        JournalEntryLine,
        back_populates="journal_entry",
        lazy="select",
        foreign_keys=[JournalEntryLine.journal_entry_id],
    )
