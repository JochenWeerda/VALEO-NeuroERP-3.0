"""
SQLAlchemy Models für Dokumente
"""

from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DocumentHeader(Base):
    """Beleg-Header"""
    __tablename__ = 'documents_header'

    id = Column(String(36), primary_key=True)
    type = Column(String(50), nullable=False)
    number = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, server_default='draft')
    date = Column(Date, nullable=False)
    customer_id = Column(String(36), nullable=True)
    supplier_id = Column(String(36), nullable=True)
    total = Column(Numeric(10, 2), nullable=True)
    ref_id = Column(String(36), nullable=True)
    next_id = Column(String(36), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    lines = relationship("DocumentLine", back_populates="header", cascade="all, delete-orphan")


class DocumentLine(Base):
    """Beleg-Position"""
    __tablename__ = 'documents_line'

    id = Column(String(36), primary_key=True)
    header_id = Column(String(36), ForeignKey('documents_header.id', ondelete='CASCADE'), nullable=False)
    line_number = Column(Integer, nullable=False)
    article_id = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    price = Column(Numeric(10, 2), nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
    vat_rate = Column(Numeric(5, 2), nullable=True)
    total = Column(Numeric(10, 2), nullable=True)

    header = relationship("DocumentHeader", back_populates="lines")


class DocumentFlow(Base):
    """Belegfluss-Definition"""
    __tablename__ = 'document_flow'

    id = Column(String(36), primary_key=True)
    from_type = Column(String(50), nullable=False)
    to_type = Column(String(50), nullable=False)
    relation = Column(String(20), nullable=False, server_default='creates')
    copy_fields = Column(JSON, nullable=True)
    rules = Column(JSON, nullable=True)


class WorkflowStatus(Base):
    """Workflow-Status"""
    __tablename__ = 'workflow_status'

    id = Column(String(36), primary_key=True)
    domain = Column(String(50), nullable=False)
    doc_number = Column(String(50), nullable=False)
    state = Column(String(20), nullable=False, server_default='draft')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)


class WorkflowAudit(Base):
    """Workflow-Audit-Trail"""
    __tablename__ = 'workflow_audit'

    id = Column(String(36), primary_key=True)
    domain = Column(String(50), nullable=False)
    doc_number = Column(String(50), nullable=False)
    ts = Column(Integer, nullable=False)
    from_state = Column(String(20), nullable=False)
    to_state = Column(String(20), nullable=False)
    action = Column(String(20), nullable=False)
    user = Column(String(100), nullable=True)
    reason = Column(String(500), nullable=True)


class ArchiveIndex(Base):
    """Archiv-Index"""
    __tablename__ = 'archive_index'

    id = Column(String(36), primary_key=True)
    domain = Column(String(50), nullable=False)
    doc_number = Column(String(50), nullable=False)
    ts = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    sha256 = Column(String(64), nullable=False)
    user = Column(String(100), nullable=True)


class NumberSeries(Base):
    """Nummernkreise"""
    __tablename__ = 'number_series'

    id = Column(String(36), primary_key=True)
    domain = Column(String(50), nullable=False)
    tenant_id = Column(String(36), nullable=True, server_default='default')
    year = Column(Integer, nullable=True)
    prefix = Column(String(20), nullable=False)
    counter = Column(Integer, nullable=False, server_default='1')
    width = Column(Integer, nullable=False, server_default='5')

