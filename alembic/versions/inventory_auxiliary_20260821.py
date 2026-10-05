"""Inventory auxiliary batch governance.

Revision ID: inventory_auxiliary_20260821
Revises: production_control_20260821
"""
from alembic import op

revision = "inventory_auxiliary_20260821"
down_revision = "production_control_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_inventory;
      CREATE TABLE IF NOT EXISTS domain_inventory.inventory_auxiliary_batches (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, inventory_count_id TEXT NOT NULL,
        batch_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'generated', source_hash TEXT NOT NULL,
        payload JSONB NOT NULL, line_count INTEGER NOT NULL DEFAULT 0,
        difference_count INTEGER NOT NULL DEFAULT 0, preliminary_value NUMERIC(16,2),
        maker TEXT NOT NULL, checker TEXT, source_route TEXT, notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id, batch_type, inventory_count_id, source_hash),
        CHECK (batch_type IN ('count_sheet','count_import','control_run','preliminary_valuation','opening_balance')),
        CHECK (status IN ('generated','reviewed','approved','applied','rejected'))
      );
      CREATE INDEX IF NOT EXISTS ix_inventory_aux_batches
        ON domain_inventory.inventory_auxiliary_batches (tenant_id,status,batch_type,created_at);
      CREATE TABLE IF NOT EXISTS domain_inventory.inventory_auxiliary_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
        batch_id TEXT NOT NULL REFERENCES domain_inventory.inventory_auxiliary_batches(id),
        action TEXT NOT NULL, old_value TEXT, new_value TEXT,
        actor TEXT NOT NULL, reason TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_inventory_aux_audit
        ON domain_inventory.inventory_auxiliary_audit (tenant_id,batch_id,created_at);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_inventory.inventory_auxiliary_audit;
      DROP TABLE IF EXISTS domain_inventory.inventory_auxiliary_batches;
    """)
