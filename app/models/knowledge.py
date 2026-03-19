"""
PostgreSQL-backed models for the central Knowledge Core.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class KnowledgeObjectRecord(Base):
    __tablename__ = "knowledge_objects"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    knowledge_id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False, index=True)
    titel = Column(String(255), nullable=False, index=True)
    typ = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, index=True)
    beschreibung = Column(Text, nullable=False, default="")
    tags = Column(JSONB, nullable=False, default=list)
    zielrollen = Column(JSONB, nullable=False, default=list)
    agentenfreigabe = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    versionen = relationship(
        "KnowledgeVersionRecord",
        cascade="all, delete-orphan",
        order_by="KnowledgeVersionRecord.version.asc()",
        lazy="joined",
    )


class KnowledgeVersionRecord(Base):
    __tablename__ = "knowledge_versions"
    __table_args__ = (
        UniqueConstraint("knowledge_id", "version", name="uq_knowledge_object_version"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=uuid7)
    knowledge_id = Column(
        String,
        ForeignKey("domain_shared.knowledge_objects.knowledge_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(Integer, nullable=False)
    format = Column(String(32), nullable=False)
    inhalt = Column(Text, nullable=False)
    strukturierte_daten = Column(JSONB, nullable=False, default=dict)
    quelle = Column(String(255), nullable=False, default="system")
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
