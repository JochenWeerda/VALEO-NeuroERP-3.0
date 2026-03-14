from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.core.database import Base


class ReadModelSnapshotRecord(Base):
    """Persistierte Read-Model-Snapshots fuer Wave-8."""

    __tablename__ = "read_model_snapshots"

    snapshot_id = Column(String(36), primary_key=True)
    model_name = Column(String(120), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    payload_hash = Column(String(64), nullable=False)
    cursor = Column(String(32), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    schema_version = Column(Integer, nullable=False, default=1)
