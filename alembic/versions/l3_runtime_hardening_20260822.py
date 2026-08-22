"""L3 runtime tenant and uniqueness hardening.

Revision ID: l3_runtime_hardening_20260822
Revises: l3_deep_mask_parity_20260822
"""

from alembic import op

revision = "l3_runtime_hardening_20260822"
down_revision = "l3_deep_mask_parity_20260822"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      ALTER TABLE domain_inventory.article_documents
        ADD COLUMN IF NOT EXISTS tenant_id TEXT;
      UPDATE domain_inventory.article_documents ad
         SET tenant_id = a.tenant_id
        FROM domain_inventory.articles a
       WHERE ad.article_id = a.id AND ad.tenant_id IS NULL;
      UPDATE domain_inventory.article_documents
         SET tenant_id = 'legacy-unassigned' WHERE tenant_id IS NULL;
      ALTER TABLE domain_inventory.article_documents
        ALTER COLUMN tenant_id SET NOT NULL;
      CREATE INDEX IF NOT EXISTS ix_article_documents_tenant_created
        ON domain_inventory.article_documents (tenant_id, created_at DESC);

      ALTER TABLE domain_ops.ops_chargen
        DROP CONSTRAINT IF EXISTS ops_chargen_chargen_id_key;
      CREATE UNIQUE INDEX IF NOT EXISTS uq_ops_chargen_tenant_charge
        ON domain_ops.ops_chargen (tenant_id, chargen_id);

      CREATE INDEX IF NOT EXISTS ix_l3_bonus_lines_run_tenant
        ON domain_reporting.l3_bonus_run_lines (run_id, tenant_id);
    """)


def downgrade() -> None:
    op.execute("""
      DROP INDEX IF EXISTS domain_reporting.ix_l3_bonus_lines_run_tenant;
      DROP INDEX IF EXISTS domain_ops.uq_ops_chargen_tenant_charge;
      ALTER TABLE domain_ops.ops_chargen
        ADD CONSTRAINT ops_chargen_chargen_id_key UNIQUE (chargen_id);
      DROP INDEX IF EXISTS domain_inventory.ix_article_documents_tenant_created;
      ALTER TABLE domain_inventory.article_documents
        DROP COLUMN IF EXISTS tenant_id;
    """)
