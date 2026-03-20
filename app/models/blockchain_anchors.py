"""
Persistent blockchain anchor records for enterprise ledger integration.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class BlockchainAnchorRecordModel(Base):
    __tablename__ = "blockchain_anchors"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    anchor_id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False, index=True)
    subject_type = Column(String(64), nullable=False, index=True)
    subject_ref = Column(String(255), nullable=False, index=True)
    network_profile = Column(String(64), nullable=False, index=True)
    payload_hash_algorithm = Column(String(32), nullable=False, default="SHA-256")
    canonical_payload_hash = Column(String(64), nullable=False, index=True)
    private_payload_hash = Column(String(64), nullable=True)
    anchor_payload = Column(JSONB, nullable=False, default=dict)
    adapter_hint = Column(JSONB, nullable=False, default=dict)
    status = Column(String(32), nullable=False, default="prepared", index=True)
    evidence_ref = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
