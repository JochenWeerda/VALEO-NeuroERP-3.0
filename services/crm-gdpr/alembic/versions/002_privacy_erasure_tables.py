"""Privacy Erasure: Tabellen für Decision, Audit, Idempotenz

Revision ID: 002_privacy_erasure
Revises: 001_initial_gdpr
Create Date: 2026-05-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_privacy_erasure"
down_revision: Union[str, None] = "001_initial_gdpr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_json_empty = sa.text("'[]'::jsonb")


def upgrade() -> None:
    op.create_table(
        "crm_privacy_erasure_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("gdpr_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.String(64), nullable=False),
        sa.Column(
            "allowed_actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=_json_empty,
        ),
        sa.Column(
            "blocked_actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=_json_empty,
        ),
        sa.Column(
            "reasons",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=_json_empty,
        ),
        sa.Column("policy_version", sa.String(128), nullable=False),
        sa.Column("requires_manual_review", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("anonymize_only", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("correlation_id_evaluate", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_privacy_erasure_decision_tenant_req",
        "crm_privacy_erasure_decisions",
        ["tenant_id", "gdpr_request_id"],
    )
    op.create_index("ix_privacy_erasure_decision_expires", "crm_privacy_erasure_decisions", ["expires_at"])

    op.create_table(
        "crm_privacy_erasure_audit",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("gdpr_request_id", postgresql.UUID(as_uuid=True)),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True)),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("subject_ref", sa.String(255), nullable=False),
        sa.Column("actor_id", sa.String(255)),
        sa.Column("policy_version", sa.String(128), nullable=False),
        sa.Column("decision", sa.String(64)),
        sa.Column(
            "reason_codes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=_json_empty,
        ),
        sa.Column(
            "allowed_actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=_json_empty,
        ),
        sa.Column(
            "blocked_actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=_json_empty,
        ),
        sa.Column("executed_action", sa.String(128)),
        sa.Column("result", sa.String(64), nullable=False),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_privacy_erasure_audit_tenant", "crm_privacy_erasure_audit", ["tenant_id"])
    op.create_index(
        "ix_privacy_erasure_audit_request_created",
        "crm_privacy_erasure_audit",
        ["gdpr_request_id", "created_at"],
    )

    op.create_table(
        "crm_privacy_erasure_executions",
        sa.Column("idempotency_key", sa.String(512), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("gdpr_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("anonymize_only", sa.Boolean(), nullable=False),
        sa.Column("erasure_log", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("correlation_id", sa.String(128), nullable=False),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_privacy_erasure_exec_gate",
        "crm_privacy_erasure_executions",
        ["tenant_id", "gdpr_request_id", "subject_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_privacy_erasure_exec_gate", table_name="crm_privacy_erasure_executions")
    op.drop_table("crm_privacy_erasure_executions")
    op.drop_index("ix_privacy_erasure_audit_request_created", table_name="crm_privacy_erasure_audit")
    op.drop_index("ix_privacy_erasure_audit_tenant", table_name="crm_privacy_erasure_audit")
    op.drop_table("crm_privacy_erasure_audit")
    op.drop_index("ix_privacy_erasure_decision_expires", table_name="crm_privacy_erasure_decisions")
    op.drop_index("ix_privacy_erasure_decision_tenant_req", table_name="crm_privacy_erasure_decisions")
    op.drop_table("crm_privacy_erasure_decisions")
