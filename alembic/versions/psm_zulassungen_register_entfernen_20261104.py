"""Entfernt das ersetzte Zulassungsregister einschliesslich Testdaten.

Revision ID: psm_register_entfernt_20261104
Revises: compliance_register_mandant_20261104
"""
from alembic import op
import sqlalchemy as sa

revision = "psm_register_entfernt_20261104"
down_revision = "compliance_register_mandant_20261104"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if not bind.execute(sa.text("SELECT to_regclass('domain_ops.ops_zulassungen_register')")).scalar():
        return
    op.execute("LOCK TABLE domain_ops.ops_zulassungen_register IN ACCESS EXCLUSIVE MODE")
    op.execute("DROP TABLE domain_ops.ops_zulassungen_register")


def downgrade() -> None:
    op.execute("""CREATE TABLE domain_ops.ops_zulassungen_register (
        id varchar PRIMARY KEY, tenant_id varchar(120) NOT NULL DEFAULT public.rls_current_tenant(),
        produkt varchar(255) NOT NULL, typ varchar(50) NOT NULL, nummer varchar(80) NOT NULL,
        behoerde varchar(120) NOT NULL, gueltig_bis timestamptz, status varchar(30) DEFAULT 'aktiv',
        created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())""")
    op.execute("CREATE INDEX ix_ops_zulassungen_register_tenant_id ON domain_ops.ops_zulassungen_register (tenant_id)")
    op.execute("ALTER TABLE domain_ops.ops_zulassungen_register ENABLE ROW LEVEL SECURITY")
    for kind, clause in (("select", "USING"), ("insert", "WITH CHECK"), ("delete", "USING")):
        op.execute(f"CREATE POLICY tenant_isolation_{kind} ON domain_ops.ops_zulassungen_register FOR {kind.upper()} {clause} (tenant_id = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_update ON domain_ops.ops_zulassungen_register FOR UPDATE USING (tenant_id = public.rls_current_tenant()) WITH CHECK (tenant_id = public.rls_current_tenant())")
