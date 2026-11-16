"""Extend the canonical raw-material settlement catalog with lifecycle and formula lines."""
from alembic import op

revision = 'rohware_schema_canonical_20261115'
down_revision = 'budget_planning_schema_20261115'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE domain_shared.rohwarengruppen ADD CONSTRAINT uq_rohwarengruppe_id_tenant UNIQUE (id, tenant_id)")
    op.execute("""ALTER TABLE domain_shared.rohware_abrechnungsschemata
        ADD COLUMN gueltig_ab date DEFAULT CURRENT_DATE,
        ADD COLUMN gueltig_bis date,
        ADD COLUMN version integer NOT NULL DEFAULT 1,
        ADD COLUMN status text DEFAULT 'AKTIV',
        ADD COLUMN updated_at timestamp NOT NULL DEFAULT now()""")
    # Existing catalog rows retain their active/inactive state; invalid group ownership
    # fails constraint validation rather than changing or discarding legacy data.
    op.execute("UPDATE domain_shared.rohware_abrechnungsschemata SET status = CASE WHEN aktiv THEN 'AKTIV' ELSE 'ARCHIV' END, gueltig_ab = CASE WHEN aktiv THEN created_at::date ELSE NULL END")
    op.execute("ALTER TABLE domain_shared.rohware_abrechnungsschemata ALTER COLUMN status SET NOT NULL")
    op.execute("""ALTER TABLE domain_shared.rohware_abrechnungsschemata
        ADD CONSTRAINT uq_rohware_schema_id_tenant UNIQUE (id, tenant_id),
        ADD CONSTRAINT fk_rohware_schema_gruppe_tenant FOREIGN KEY (gruppe_id, tenant_id)
            REFERENCES domain_shared.rohwarengruppen(id, tenant_id),
        ADD CONSTRAINT ck_rohware_schema_status CHECK (status IN ('ENTWURF', 'AKTIV', 'ARCHIV')),
        ADD CONSTRAINT ck_rohware_schema_aktiv CHECK (aktiv = (status = 'AKTIV')),
        ADD CONSTRAINT ck_rohware_schema_version CHECK (version > 0),
        ADD CONSTRAINT ck_rohware_schema_dates CHECK (gueltig_bis IS NULL OR gueltig_ab IS NULL OR gueltig_bis >= gueltig_ab),
        ADD CONSTRAINT ck_rohware_schema_active_date CHECK (status <> 'AKTIV' OR gueltig_ab IS NOT NULL)""")
    op.execute("""CREATE TABLE domain_shared.rohware_schema_lines (
        id text PRIMARY KEY, tenant_id text NOT NULL, schema_id text NOT NULL,
        positions_typ text NOT NULL, bezeichnung text NOT NULL,
        berechnungsformel text NOT NULL, einheit text NOT NULL,
        sort_order integer NOT NULL DEFAULT 10, created_at timestamp NOT NULL DEFAULT now(),
        CONSTRAINT fk_rohware_schema_line_tenant FOREIGN KEY (schema_id, tenant_id)
            REFERENCES domain_shared.rohware_abrechnungsschemata(id, tenant_id) ON DELETE CASCADE)""")
    op.execute("CREATE INDEX ix_rohware_schema_lines_tenant_parent ON domain_shared.rohware_schema_lines (tenant_id, schema_id, sort_order)")
    op.execute("ALTER TABLE domain_shared.rohware_schema_lines ENABLE ROW LEVEL SECURITY")
    for action, clause in (("select", "USING (tenant_id = public.rls_current_tenant())"),
                           ("insert", "WITH CHECK (tenant_id = public.rls_current_tenant())"),
                           ("update", "USING (tenant_id = public.rls_current_tenant()) WITH CHECK (tenant_id = public.rls_current_tenant())"),
                           ("delete", "USING (tenant_id = public.rls_current_tenant())")):
        op.execute(f"CREATE POLICY tenant_isolation_{action} ON domain_shared.rohware_schema_lines FOR {action.upper()} {clause}")
    op.execute("""DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'valeo_app') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON domain_shared.rohware_schema_lines TO valeo_app;
      END IF;
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'valeo_agent') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON domain_shared.rohware_schema_lines TO valeo_agent;
      END IF;
    END $$""")


def downgrade():
    # Formula positions and lifecycle metadata are lost; existing catalog rows and
    # the current aktiv flag remain intact. Back up before a planned downgrade.
    op.execute("DROP TABLE domain_shared.rohware_schema_lines")
    op.execute("""ALTER TABLE domain_shared.rohware_abrechnungsschemata
        DROP CONSTRAINT ck_rohware_schema_active_date,
        DROP CONSTRAINT ck_rohware_schema_dates,
        DROP CONSTRAINT ck_rohware_schema_version,
        DROP CONSTRAINT ck_rohware_schema_aktiv,
        DROP CONSTRAINT ck_rohware_schema_status,
        DROP CONSTRAINT fk_rohware_schema_gruppe_tenant,
        DROP CONSTRAINT uq_rohware_schema_id_tenant,
        DROP COLUMN updated_at, DROP COLUMN status, DROP COLUMN version,
        DROP COLUMN gueltig_bis, DROP COLUMN gueltig_ab""")
    op.execute("ALTER TABLE domain_shared.rohwarengruppen DROP CONSTRAINT uq_rohwarengruppe_id_tenant")
