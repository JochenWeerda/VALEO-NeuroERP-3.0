"""FEED-CORE-019: versioned feed analyses and provenance.

Revision ID: feed_core_feed_analyses_20260715
Revises: feed_core_feed_catalog_20260715
"""
from alembic import op


revision = "feed_core_feed_analyses_20260715"
down_revision = "feed_core_feed_catalog_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE domain_shared.grundfutter_analysen
          ADD COLUMN IF NOT EXISTS feed_id varchar NULL,
          ADD COLUMN IF NOT EXISTS scope_code varchar(80) NOT NULL DEFAULT 'default',
          ADD COLUMN IF NOT EXISTS status varchar(32) NOT NULL DEFAULT 'draft',
          ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT false,
          ADD COLUMN IF NOT EXISTS method varchar(255) NULL,
          ADD COLUMN IF NOT EXISTS sampled_at timestamptz NULL,
          ADD COLUMN IF NOT EXISTS valid_from date NOT NULL DEFAULT CURRENT_DATE,
          ADD COLUMN IF NOT EXISTS valid_until date NULL,
          ADD COLUMN IF NOT EXISTS original_document_id varchar NULL,
          ADD COLUMN IF NOT EXISTS original_sha256 varchar(64) NULL,
          ADD COLUMN IF NOT EXISTS revision integer NOT NULL DEFAULT 1,
          ADD COLUMN IF NOT EXISTS released_at timestamptz NULL,
          ADD COLUMN IF NOT EXISTS released_by varchar NULL,
          ADD COLUMN IF NOT EXISTS changed_by varchar NOT NULL DEFAULT 'migration';

        UPDATE domain_shared.grundfutter_analysen
           SET status='validated'
         WHERE verifiziert IS TRUE AND status='draft';

        DO $$ BEGIN
          ALTER TABLE domain_shared.grundfutter_analysen
            ADD CONSTRAINT fk_gfa_feed FOREIGN KEY (feed_id)
            REFERENCES domain_shared.futtermittel_einzelfutter(id) ON DELETE RESTRICT;
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
        DO $$ BEGIN
          ALTER TABLE domain_shared.grundfutter_analysen
            ADD CONSTRAINT ck_gfa_status CHECK (status IN
              ('uploaded','mapped','draft','validated','released','superseded','rejected'));
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
        DO $$ BEGIN
          ALTER TABLE domain_shared.grundfutter_analysen
            ADD CONSTRAINT ck_gfa_validity CHECK (valid_until IS NULL OR valid_until >= valid_from);
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;

        CREATE INDEX IF NOT EXISTS ix_gfa_tenant_feed
          ON domain_shared.grundfutter_analysen (tenant_id, feed_id, created_at DESC);
        CREATE UNIQUE INDEX IF NOT EXISTS uq_gfa_one_active_released
          ON domain_shared.grundfutter_analysen (tenant_id, feed_id, scope_code)
          WHERE status = 'released' AND is_active;

        CREATE TABLE IF NOT EXISTS domain_shared.feeding_feed_analysis_values (
          id varchar PRIMARY KEY,
          tenant_id varchar NOT NULL,
          analysis_id varchar NOT NULL REFERENCES domain_shared.grundfutter_analysen(id) ON DELETE CASCADE,
          nutrient_code varchar(80) NOT NULL,
          original_value numeric(24, 9) NOT NULL,
          original_unit_code varchar(80) NOT NULL,
          canonical_value numeric(24, 9) NOT NULL,
          canonical_unit_code varchar(80) NOT NULL,
          basis varchar(32) NOT NULL,
          value_status varchar(32) NOT NULL DEFAULT 'measured',
          method varchar(255) NULL,
          detection_limit numeric(24, 9) NULL,
          confidence numeric(5, 4) NULL,
          source_ref varchar(500) NULL,
          revision integer NOT NULL DEFAULT 1,
          created_at timestamptz NOT NULL DEFAULT now(),
          created_by varchar NOT NULL,
          CONSTRAINT ck_analysis_value_status CHECK (value_status IN ('measured','calculated','estimated')),
          CONSTRAINT ck_analysis_value_basis CHECK (basis IN ('fresh_matter','dry_matter')),
          UNIQUE (tenant_id, analysis_id, nutrient_code, revision)
        );
        CREATE INDEX IF NOT EXISTS ix_analysis_values_lookup
          ON domain_shared.feeding_feed_analysis_values (tenant_id, analysis_id, nutrient_code);

        CREATE TABLE IF NOT EXISTS domain_shared.feeding_feed_analysis_findings (
          id varchar PRIMARY KEY,
          tenant_id varchar NOT NULL,
          analysis_id varchar NOT NULL REFERENCES domain_shared.grundfutter_analysen(id) ON DELETE CASCADE,
          code varchar(120) NOT NULL,
          severity varchar(16) NOT NULL,
          message text NOT NULL,
          nutrient_code varchar(80) NULL,
          observed_value numeric(24, 9) NULL,
          acknowledged boolean NOT NULL DEFAULT false,
          created_at timestamptz NOT NULL DEFAULT now(),
          CONSTRAINT ck_analysis_finding_severity CHECK (severity IN ('info','warning','blocker'))
        );

        CREATE TABLE IF NOT EXISTS domain_shared.feeding_feed_analysis_revisions (
          id varchar PRIMARY KEY,
          tenant_id varchar NOT NULL,
          analysis_id varchar NOT NULL REFERENCES domain_shared.grundfutter_analysen(id) ON DELETE RESTRICT,
          revision integer NOT NULL,
          snapshot jsonb NOT NULL,
          reason text NOT NULL,
          changed_by varchar NOT NULL,
          changed_at timestamptz NOT NULL DEFAULT now(),
          UNIQUE (tenant_id, analysis_id, revision)
        );

        CREATE OR REPLACE FUNCTION domain_shared.guard_immutable_feeding_feed_analysis_revision()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          RAISE EXCEPTION 'feeding feed analysis revisions are immutable';
        END $$;
        DROP TRIGGER IF EXISTS trg_immutable_feeding_feed_analysis_revision
          ON domain_shared.feeding_feed_analysis_revisions;
        CREATE TRIGGER trg_immutable_feeding_feed_analysis_revision
          BEFORE UPDATE OR DELETE ON domain_shared.feeding_feed_analysis_revisions
          FOR EACH ROW EXECUTE FUNCTION domain_shared.guard_immutable_feeding_feed_analysis_revision();

        INSERT INTO domain_shared.feeding_feed_analysis_revisions
          (id, tenant_id, analysis_id, revision, snapshot, reason, changed_by)
        SELECT gen_random_uuid()::text, tenant_id, id, revision,
               jsonb_build_object('status', status, 'bezeichnung', bezeichnung, 'legacy_backfill', true),
               'Additiver Legacy-Backfill', 'migration'
          FROM domain_shared.grundfutter_analysen
        ON CONFLICT (tenant_id, analysis_id, revision) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS trg_immutable_feeding_feed_analysis_revision ON domain_shared.feeding_feed_analysis_revisions;
        DROP FUNCTION IF EXISTS domain_shared.guard_immutable_feeding_feed_analysis_revision();
        DROP TABLE IF EXISTS domain_shared.feeding_feed_analysis_revisions;
        DROP TABLE IF EXISTS domain_shared.feeding_feed_analysis_findings;
        DROP TABLE IF EXISTS domain_shared.feeding_feed_analysis_values;
        DROP INDEX IF EXISTS domain_shared.uq_gfa_one_active_released;
        DROP INDEX IF EXISTS domain_shared.ix_gfa_tenant_feed;
        ALTER TABLE domain_shared.grundfutter_analysen
          DROP CONSTRAINT IF EXISTS ck_gfa_validity,
          DROP CONSTRAINT IF EXISTS ck_gfa_status,
          DROP CONSTRAINT IF EXISTS fk_gfa_feed,
          DROP COLUMN IF EXISTS changed_by, DROP COLUMN IF EXISTS released_by,
          DROP COLUMN IF EXISTS released_at, DROP COLUMN IF EXISTS revision,
          DROP COLUMN IF EXISTS original_sha256, DROP COLUMN IF EXISTS original_document_id,
          DROP COLUMN IF EXISTS valid_until, DROP COLUMN IF EXISTS valid_from,
          DROP COLUMN IF EXISTS sampled_at, DROP COLUMN IF EXISTS method,
          DROP COLUMN IF EXISTS is_active, DROP COLUMN IF EXISTS status,
          DROP COLUMN IF EXISTS scope_code, DROP COLUMN IF EXISTS feed_id;
    """)
