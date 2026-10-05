"""Document control exception worklist and audit.

Revision ID: document_control_20260821
Revises: docflow_returns_20260821
"""
from alembic import op

revision = "document_control_20260821"
down_revision = "docflow_returns_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_ops;
      CREATE TABLE IF NOT EXISTS domain_ops.document_control_exceptions (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        exception_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        document_ref TEXT NOT NULL,
        document_number TEXT NOT NULL,
        partner_ref TEXT,
        partner_name TEXT,
        assigned_user TEXT,
        due_at TIMESTAMPTZ,
        source_route TEXT,
        source_key TEXT NOT NULL,
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id, source_key),
        CHECK (exception_type IN (
          'open_purchase_order',
          'missing_inbound_document',
          'blocked_delivery_note',
          'uninvoiced_delivery_note'
        )),
        CHECK (status IN ('open','assigned','in_progress','resolved','waived'))
      );
      CREATE INDEX IF NOT EXISTS ix_docctrl_worklist
        ON domain_ops.document_control_exceptions (tenant_id, status, exception_type, due_at);
      CREATE TABLE IF NOT EXISTS domain_ops.document_control_audit (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        case_id TEXT NOT NULL REFERENCES domain_ops.document_control_exceptions(id),
        action TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        actor TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_docctrl_audit
        ON domain_ops.document_control_audit (tenant_id, case_id, created_at);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_ops.document_control_audit;
      DROP TABLE IF EXISTS domain_ops.document_control_exceptions;
    """)
