"""Bind operations scales to verified tenant; leave unknown legacy ownership unassigned.

Revision ID: waage_tenant_20261030
Revises: crm_activity_canon_20261029
"""
from alembic import op
import sqlalchemy as sa

revision = 'waage_tenant_20261030'
down_revision = 'crm_activity_canon_20261029'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ops_waagen', sa.Column('tenant_id', sa.String(64), nullable=True), schema='domain_ops')
    # NOT VALID preserves unassigned historic rows, while every new/updated row
    # must have an explicit nonblank tenant even for a privileged DB role.
    op.execute("ALTER TABLE domain_ops.ops_waagen ADD CONSTRAINT ck_ops_waagen_tenant_nonblank CHECK (tenant_id IS NOT NULL AND length(btrim(tenant_id)) > 0) NOT VALID")
    op.create_index('ix_domain_ops_ops_waagen_tenant_id', 'ops_waagen', ['tenant_id'], schema='domain_ops')
    op.execute('ALTER TABLE domain_ops.ops_waagen ENABLE ROW LEVEL SECURITY')
    op.execute('CREATE POLICY tenant_isolation_select ON domain_ops.ops_waagen FOR SELECT USING (tenant_id = public.rls_current_tenant())')
    op.execute('CREATE POLICY tenant_isolation_insert ON domain_ops.ops_waagen FOR INSERT WITH CHECK (tenant_id = public.rls_current_tenant())')
    op.execute('CREATE POLICY tenant_isolation_update ON domain_ops.ops_waagen FOR UPDATE USING (tenant_id = public.rls_current_tenant()) WITH CHECK (tenant_id = public.rls_current_tenant())')
    op.execute('CREATE POLICY tenant_isolation_delete ON domain_ops.ops_waagen FOR DELETE USING (tenant_id = public.rls_current_tenant())')

    op.add_column('ops_waagen', sa.Column('eichamt', sa.String(200), nullable=True), schema='domain_ops')
    op.add_column('ops_waagen', sa.Column('zertifikat_nr', sa.String(200), nullable=True), schema='domain_ops')
    op.create_table('waage_import_entries',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('waage_id', sa.String(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error', sa.Text()), sa.Column('ticket_id', sa.String()),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False), schema='domain_ops')
    op.create_index('ix_domain_ops_waage_import_entries_tenant_id', 'waage_import_entries', ['tenant_id'], schema='domain_ops')
    op.execute('ALTER TABLE domain_ops.waage_import_entries ENABLE ROW LEVEL SECURITY')
    op.execute('CREATE POLICY tenant_isolation ON domain_ops.waage_import_entries USING (tenant_id = public.rls_current_tenant()) WITH CHECK (tenant_id = public.rls_current_tenant())')
    # Only the permission predicate bypasses RLS; no row or owner is returned.
    # Existence must be visible here, otherwise a foreign ID looks external.
    op.execute("""CREATE FUNCTION public.waage_reference_allowed(ref text) RETURNS boolean
        LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path = pg_catalog
        SET row_security = off AS $$
        DECLARE owner_tenant text; active_tenant text;
        BEGIN
            active_tenant := public.rls_current_tenant();
            IF active_tenant IS NULL THEN RETURN false; END IF;
            SELECT tenant_id INTO owner_tenant FROM domain_ops.ops_waagen WHERE id = ref FOR SHARE;
            IF FOUND THEN RETURN COALESCE(owner_tenant = active_tenant, false); END IF;
            RETURN true;
        END
        $$""")
    op.execute('REVOKE ALL ON FUNCTION public.waage_reference_allowed(text) FROM PUBLIC')
    op.execute('GRANT EXECUTE ON FUNCTION public.waage_reference_allowed(text) TO valeo_app')


def downgrade():
    raise RuntimeError("Waage-Tenant-Isolation cannot be removed by an automatic downgrade")
