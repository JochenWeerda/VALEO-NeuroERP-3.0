"""
SQLAlchemy ORM models for Neuro State Graph + Confidence Ledger.

Tables live in schema domain_shared (cross-tenant infrastructure).
Both tables are designed as append-friendly: transitions and ledger entries
are never updated or deleted in production.
"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


# ---------------------------------------------------------------------------
# Neuro State Graph
# ---------------------------------------------------------------------------

class StateNodeRecord(Base):
    """Persistent business-object node in the Neuro State Graph."""

    __tablename__ = "neuroassist_state_nodes"
    __table_args__ = (
        Index("ix_state_nodes_tenant", "tenant_id"),
        Index("ix_state_nodes_type_phase", "node_type", "phase"),
        Index("ix_state_nodes_aggregate", "aggregate_type", "aggregate_id"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    node_id = Column(String, primary_key=True)
    node_type = Column(String(30), nullable=False)          # StateNodeType
    phase = Column(String(30), nullable=False)               # StatePhase
    tenant_id = Column(String, nullable=False)
    aggregate_id = Column(String, nullable=False)
    aggregate_type = Column(String(80), nullable=False)
    label = Column(String(255), nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=False, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    schema_version = Column(Integer, nullable=False, server_default="1")


class StateEdgeRecord(Base):
    """Directed edge between two state nodes."""

    __tablename__ = "neuroassist_state_edges"
    __table_args__ = (
        Index("ix_state_edges_source", "source_node_id"),
        Index("ix_state_edges_target", "target_node_id"),
        Index("ix_state_edges_tenant", "tenant_id"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    edge_id = Column(String, primary_key=True)
    source_node_id = Column(String, nullable=False)
    target_node_id = Column(String, nullable=False)
    relation = Column(String(30), nullable=False)            # EdgeRelation
    tenant_id = Column(String, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=False, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    schema_version = Column(Integer, nullable=False, server_default="1")


class StateTransitionRecord(Base):
    """Immutable phase-change record. Append-only -- no UPDATE/DELETE in production."""

    __tablename__ = "neuroassist_state_transitions"
    __table_args__ = (
        Index("ix_state_trans_node", "node_id"),
        Index("ix_state_trans_tenant", "tenant_id"),
        Index("ix_state_trans_case_run", "case_run_id"),
        Index("ix_state_trans_recorded", "recorded_at"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    transition_id = Column(String, primary_key=True)
    node_id = Column(String, nullable=False)
    from_phase = Column(String(30), nullable=False)
    to_phase = Column(String(30), nullable=False)
    tenant_id = Column(String, nullable=False)
    triggered_by = Column(String(120), nullable=False)
    reason = Column(Text, nullable=False, server_default="")
    case_run_id = Column(String, nullable=True)
    evidence_refs = Column(JSONB, nullable=False, server_default="[]")
    context_hash = Column(String(64), nullable=False, server_default="")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    schema_version = Column(Integer, nullable=False, server_default="1")


# ---------------------------------------------------------------------------
# Confidence Ledger
# ---------------------------------------------------------------------------

class ConfidenceLedgerRecord(Base):
    """
    Append-only, hash-chained confidence/risk ledger.

    Each row is immutable. The chain_hash links to the previous entry,
    forming a tamper-evident chain.
    """

    __tablename__ = "neuroassist_confidence_ledger"
    __table_args__ = (
        Index("ix_conf_ledger_tenant", "tenant_id"),
        Index("ix_conf_ledger_case_run", "case_run_id"),
        Index("ix_conf_ledger_state_node", "state_node_id"),
        Index("ix_conf_ledger_source", "source"),
        Index("ix_conf_ledger_recorded", "recorded_at"),
        Index("ix_conf_ledger_risk", "risk_level"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    entry_id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    case_run_id = Column(String, nullable=True)
    state_node_id = Column(String, nullable=True)

    # Score
    confidence_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)          # RiskLevel
    source = Column(String(30), nullable=False)              # ConfidenceSource

    # Reproducibility
    model_id = Column(String(120), nullable=False, server_default="")
    model_version = Column(String(30), nullable=False, server_default="")
    input_hash = Column(String(64), nullable=False, server_default="")

    # Evidence
    reason = Column(Text, nullable=False)
    evidence_refs = Column(JSONB, nullable=False, server_default="[]")
    context_data = Column(JSONB, nullable=False, server_default="{}")

    # Chain integrity
    previous_hash = Column(String(64), nullable=False)
    chain_hash = Column(String(64), nullable=False)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    schema_version = Column(Integer, nullable=False, server_default="1")
