"""Audit trail for the foreign-goods operator worklist.

Revision ID: foreign_goods_worklist_20260821
Revises: billing_batch_20260821
"""

from alembic import op

revision = "foreign_goods_worklist_20260821"
down_revision = "billing_batch_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_einkauf;
      CREATE TABLE IF NOT EXISTS domain_einkauf.foreign_goods_audit (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        foreign_goods_id TEXT NOT NULL,
        action TEXT NOT NULL,
        old_status TEXT,
        new_status TEXT,
        old_warehouse_id TEXT,
        new_warehouse_id TEXT,
        old_location TEXT,
        new_location TEXT,
        old_quantity NUMERIC(14,3),
        new_quantity NUMERIC(14,3),
        actor TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_foreign_goods_audit_case
        ON domain_einkauf.foreign_goods_audit (tenant_id, foreign_goods_id, created_at);
      CREATE INDEX IF NOT EXISTS ix_fwe_operator_worklist
        ON domain_einkauf.fremdwaren_einlagerung
          (tenant_id, status, eigentuemer_id, warehouse_id, einlagerungsdatum);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_einkauf.foreign_goods_audit;")
