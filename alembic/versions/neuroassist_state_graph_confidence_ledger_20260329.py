"""Neuro State Graph + Confidence Ledger tables

Revision ID: neuroassist_state_graph_confidence_ledger_20260329
Revises: lkw_annahme_queue_klaerung_20260328
Create Date: 2026-03-29

Lane B: State Graph (nodes, edges, transitions) + Confidence Ledger (append-only, hash-chained).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "neuroassist_state_graph_confidence_ledger_20260329"
down_revision: Union[str, tuple[str, ...], None] = "lkw_annahme_queue_klaerung_20260328"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- State Nodes --
    op.create_table(
        "neuroassist_state_nodes",
        sa.Column("node_id", sa.String(), primary_key=True),
        sa.Column("node_type", sa.String(30), nullable=False),
        sa.Column("phase", sa.String(30), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("aggregate_id", sa.String(), nullable=False),
        sa.Column("aggregate_type", sa.String(80), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        schema="domain_shared",
    )
    op.create_index("ix_state_nodes_tenant", "neuroassist_state_nodes", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_state_nodes_type_phase", "neuroassist_state_nodes", ["node_type", "phase"], schema="domain_shared")
    op.create_index("ix_state_nodes_aggregate", "neuroassist_state_nodes", ["aggregate_type", "aggregate_id"], schema="domain_shared")

    # -- State Edges --
    op.create_table(
        "neuroassist_state_edges",
        sa.Column("edge_id", sa.String(), primary_key=True),
        sa.Column("source_node_id", sa.String(), nullable=False),
        sa.Column("target_node_id", sa.String(), nullable=False),
        sa.Column("relation", sa.String(30), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        schema="domain_shared",
    )
    op.create_index("ix_state_edges_source", "neuroassist_state_edges", ["source_node_id"], schema="domain_shared")
    op.create_index("ix_state_edges_target", "neuroassist_state_edges", ["target_node_id"], schema="domain_shared")
    op.create_index("ix_state_edges_tenant", "neuroassist_state_edges", ["tenant_id"], schema="domain_shared")

    # -- State Transitions (append-only) --
    op.create_table(
        "neuroassist_state_transitions",
        sa.Column("transition_id", sa.String(), primary_key=True),
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("from_phase", sa.String(30), nullable=False),
        sa.Column("to_phase", sa.String(30), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("triggered_by", sa.String(120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("case_run_id", sa.String(), nullable=True),
        sa.Column("evidence_refs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("context_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        schema="domain_shared",
    )
    op.create_index("ix_state_trans_node", "neuroassist_state_transitions", ["node_id"], schema="domain_shared")
    op.create_index("ix_state_trans_tenant", "neuroassist_state_transitions", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_state_trans_case_run", "neuroassist_state_transitions", ["case_run_id"], schema="domain_shared")
    op.create_index("ix_state_trans_recorded", "neuroassist_state_transitions", ["recorded_at"], schema="domain_shared")

    # -- Confidence Ledger (append-only, hash-chained) --
    op.create_table(
        "neuroassist_confidence_ledger",
        sa.Column("entry_id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("case_run_id", sa.String(), nullable=True),
        sa.Column("state_node_id", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("model_id", sa.String(120), nullable=False, server_default=""),
        sa.Column("model_version", sa.String(30), nullable=False, server_default=""),
        sa.Column("input_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("evidence_refs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("context_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("chain_hash", sa.String(64), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        schema="domain_shared",
    )
    op.create_index("ix_conf_ledger_tenant", "neuroassist_confidence_ledger", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_conf_ledger_case_run", "neuroassist_confidence_ledger", ["case_run_id"], schema="domain_shared")
    op.create_index("ix_conf_ledger_state_node", "neuroassist_confidence_ledger", ["state_node_id"], schema="domain_shared")
    op.create_index("ix_conf_ledger_source", "neuroassist_confidence_ledger", ["source"], schema="domain_shared")
    op.create_index("ix_conf_ledger_recorded", "neuroassist_confidence_ledger", ["recorded_at"], schema="domain_shared")
    op.create_index("ix_conf_ledger_risk", "neuroassist_confidence_ledger", ["risk_level"], schema="domain_shared")


def downgrade() -> None:
    op.drop_table("neuroassist_confidence_ledger", schema="domain_shared")
    op.drop_table("neuroassist_state_transitions", schema="domain_shared")
    op.drop_table("neuroassist_state_edges", schema="domain_shared")
    op.drop_table("neuroassist_state_nodes", schema="domain_shared")
