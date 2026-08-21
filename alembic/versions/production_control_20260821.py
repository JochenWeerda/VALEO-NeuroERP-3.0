"""Production control worklist and audit.

Revision ID: production_control_20260821
Revises: document_control_20260821
"""
from alembic import op

revision = "production_control_20260821"
down_revision = "document_control_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_ops;
      CREATE TABLE IF NOT EXISTS domain_ops.production_operations (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        operation_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        source_type TEXT NOT NULL,
        source_ref TEXT NOT NULL,
        source_number TEXT NOT NULL,
        source_route TEXT,
        work_center TEXT,
        article_ref TEXT,
        article_name TEXT,
        batch_ref TEXT,
        quantity NUMERIC(14,3),
        unit TEXT,
        assigned_user TEXT,
        planned_at TIMESTAMPTZ,
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id, source_type, source_ref),
        CHECK (operation_type IN ('production_order','mill_run','stock_transfer','batch_posting','rework')),
        CHECK (status IN ('queued','released','running','paused','completed','cancelled','rework'))
      );
      CREATE INDEX IF NOT EXISTS ix_production_operations_worklist
        ON domain_ops.production_operations (tenant_id, status, operation_type, planned_at);
      CREATE TABLE IF NOT EXISTS domain_ops.production_operation_audit (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        operation_id TEXT NOT NULL REFERENCES domain_ops.production_operations(id),
        action TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        actor TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_production_operation_audit
        ON domain_ops.production_operation_audit (tenant_id, operation_id, created_at);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_ops.production_operation_audit;
      DROP TABLE IF EXISTS domain_ops.production_operations;
    """)
