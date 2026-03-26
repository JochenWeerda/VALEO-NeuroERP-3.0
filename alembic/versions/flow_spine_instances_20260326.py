"""Flow Spine Instance persistence table

Revision ID: flow_spine_instances_20260326
Revises: sales_cn_ret_pl_20260305
Create Date: 2026-03-26

Wave 104 — P0: ersetzt prozess-internen In-Memory-Dict durch DB-Tabelle.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "flow_spine_instances_20260326"
down_revision = "sales_cn_ret_pl_20260305"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_ops"))

    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_ops.ops_flow_spine_instances (
            id                  VARCHAR(36)  PRIMARY KEY,
            case_number         VARCHAR(64)  NOT NULL,
            process_key         VARCHAR(120) NOT NULL,
            label               VARCHAR(255) NOT NULL DEFAULT '',
            customer_id         VARCHAR(120),
            customer_name       VARCHAR(255),
            subject             VARCHAR(255),
            entry_mode          VARCHAR(80),
            linked_document_id  VARCHAR(120),
            linked_document_type VARCHAR(80),
            node_statuses       JSONB        NOT NULL DEFAULT '{}',
            active_node_id      VARCHAR(120),
            last_actor          VARCHAR(120),
            last_action_label   VARCHAR(255),
            tenant_id           VARCHAR(120) NOT NULL DEFAULT 'default',
            created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instances_process_key "
        "ON domain_ops.ops_flow_spine_instances (process_key)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instances_tenant_id "
        "ON domain_ops.ops_flow_spine_instances (tenant_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instances_case_number "
        "ON domain_ops.ops_flow_spine_instances (case_number)"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_ops.ops_flow_spine_instances"))
