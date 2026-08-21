"""Billing batch orchestration and audit.

Revision ID: billing_batch_20260821
Revises: inventory_auxiliary_20260821
"""

from alembic import op

revision = "billing_batch_20260821"
down_revision = "inventory_auxiliary_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_finance;
      CREATE TABLE IF NOT EXISTS domain_finance.billing_batches (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, batch_number TEXT NOT NULL,
        batch_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', description TEXT,
        maker TEXT NOT NULL, checker TEXT, currency TEXT NOT NULL DEFAULT 'EUR',
        total_lines INTEGER NOT NULL DEFAULT 0, processed_lines INTEGER NOT NULL DEFAULT 0,
        failed_lines INTEGER NOT NULL DEFAULT 0, total_amount NUMERIC(16,2) NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,batch_number),
        CHECK (batch_type IN ('sales_invoice','purchase_invoice','self_billing_sales','self_billing_purchase')),
        CHECK (status IN ('draft','validated','released','running','completed','partial_failed','cancelled'))
      );
      CREATE TABLE IF NOT EXISTS domain_finance.billing_batch_lines (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
        batch_id TEXT NOT NULL REFERENCES domain_finance.billing_batches(id),
        source_type TEXT NOT NULL, source_ref TEXT NOT NULL, source_number TEXT NOT NULL,
        source_route TEXT, evidence_route TEXT, amount NUMERIC(16,2) NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'pending', validation_error TEXT, retry_count INTEGER NOT NULL DEFAULT 0,
        idempotency_key TEXT NOT NULL, processed_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,idempotency_key),
        CHECK (status IN ('pending','processed','failed'))
      );
      CREATE INDEX IF NOT EXISTS ix_billing_batches_worklist ON domain_finance.billing_batches (tenant_id,status,batch_type,created_at);
      CREATE INDEX IF NOT EXISTS ix_billing_batch_lines_error ON domain_finance.billing_batch_lines (tenant_id,status,batch_id);
      CREATE TABLE IF NOT EXISTS domain_finance.billing_batch_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
        batch_id TEXT NOT NULL REFERENCES domain_finance.billing_batches(id), line_id TEXT,
        action TEXT NOT NULL, old_value TEXT, new_value TEXT, actor TEXT NOT NULL,
        reason TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_billing_batch_audit ON domain_finance.billing_batch_audit (tenant_id,batch_id,created_at);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_finance.billing_batch_audit;
      DROP TABLE IF EXISTS domain_finance.billing_batch_lines;
      DROP TABLE IF EXISTS domain_finance.billing_batches;
    """)
