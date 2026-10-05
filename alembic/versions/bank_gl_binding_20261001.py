"""Persist an explicit tenant-bound bank-to-ledger link; no inferred backfill."""
from alembic import op
from sqlalchemy import text

revision = "bank_gl_binding_20261001"
# Parent is the last committed head; pending parallel EUDR migrations need a coordinated merge.
down_revision = "eudr_sorgfaltserklaerung_20261001"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("ALTER TABLE domain_erp.chart_of_accounts ADD CONSTRAINT uq_coa_id_tenant_bank_gl UNIQUE (id, tenant_id)"))
    conn.execute(text("ALTER TABLE domain_erp.bank_accounts ADD COLUMN gl_account_id VARCHAR"))
    conn.execute(text("""
        ALTER TABLE domain_erp.bank_accounts ADD CONSTRAINT fk_bank_gl_tenant
        FOREIGN KEY (gl_account_id, tenant_id)
        REFERENCES domain_erp.chart_of_accounts (id, tenant_id)
    """))
    conn.execute(text("ALTER TABLE domain_erp.bank_accounts ADD CONSTRAINT ck_bank_gl_has_tenant CHECK (gl_account_id IS NULL OR tenant_id IS NOT NULL)"))
    conn.execute(text("CREATE INDEX ix_bank_gl_tenant ON domain_erp.bank_accounts (gl_account_id, tenant_id)"))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("ALTER TABLE domain_erp.bank_accounts DROP COLUMN gl_account_id"))
    conn.execute(text("ALTER TABLE domain_erp.chart_of_accounts DROP CONSTRAINT uq_coa_id_tenant_bank_gl"))
