"""
SQLAlchemy-Modelle für Workflow-Definitionen und -Instanzen.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class WorkflowDefinitionModel(Base):
    __tablename__ = "workflow_definitions"

    key = Column(String(255), primary_key=True)
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    tenant = Column(String(64), nullable=False, default="default")
    definition = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class WorkflowInstanceModel(Base):
    __tablename__ = "workflow_instances"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_name = Column(String(128), nullable=False)
    workflow_version = Column(String(32), nullable=False)
    tenant = Column(String(64), nullable=False, default="default")
    state = Column(String(64), nullable=False)
    context = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


