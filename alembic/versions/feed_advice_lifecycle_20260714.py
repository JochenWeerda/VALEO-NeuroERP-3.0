"""Persistent feeding groups and immutable ration versions.

Revision ID: feed_advice_lifecycle_20260714
Revises: feed_advice_connectors_20260714
"""

from alembic import op

revision = "feed_advice_lifecycle_20260714"
down_revision = "feed_advice_connectors_20260714"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_groups (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      external_ref VARCHAR(160), name VARCHAR(200) NOT NULL,
      animal_type VARCHAR(40) NOT NULL DEFAULT 'dairy_cow',
      animal_count INTEGER NOT NULL CHECK (animal_count >= 0),
      body_mass_kg NUMERIC(10,3), days_in_milk INTEGER,
      lactation_number NUMERIC(6,2), target_milk_kg NUMERIC(10,3),
      feeding_system VARCHAR(40) NOT NULL DEFAULT 'TMR',
      location VARCHAR(200), active BOOLEAN NOT NULL DEFAULT TRUE,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_by VARCHAR(160) NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_group_external UNIQUE (tenant_id, external_ref)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_groups_tenant_active ON domain_agrar.feeding_groups (tenant_id,active,name)")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.rations (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      name VARCHAR(240) NOT NULL, description TEXT,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rations_group ON domain_agrar.rations (tenant_id,group_id,updated_at DESC)")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.ration_versions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      ration_id VARCHAR NOT NULL REFERENCES domain_agrar.rations(id),
      version_no INTEGER NOT NULL CHECK (version_no > 0),
      source VARCHAR(40) NOT NULL DEFAULT 'solver', comment TEXT,
      snapshot JSONB NOT NULL, snapshot_checksum VARCHAR(64) NOT NULL,
      based_on_version_id VARCHAR REFERENCES domain_agrar.ration_versions(id),
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_ration_version_no UNIQUE (tenant_id,ration_id,version_no),
      CONSTRAINT uq_ration_version_checksum UNIQUE (tenant_id,ration_id,snapshot_checksum)
    )""")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.ration_version_lifecycle (
      version_id VARCHAR PRIMARY KEY REFERENCES domain_agrar.ration_versions(id),
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      ration_id VARCHAR NOT NULL REFERENCES domain_agrar.rations(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      status VARCHAR(24) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','in_review','approved','scheduled','active','retired','archived')),
      feeding_start TIMESTAMPTZ,
      reviewed_by VARCHAR(160), reviewed_at TIMESTAMPTZ,
      approved_by VARCHAR(160), approved_at TIMESTAMPTZ,
      activated_by VARCHAR(160), activated_at TIMESTAMPTZ,
      retired_by VARCHAR(160), retired_at TIMESTAMPTZ,
      archived_by VARCHAR(160), archived_at TIMESTAMPTZ,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_active_ration_per_group ON domain_agrar.ration_version_lifecycle (tenant_id,group_id) WHERE status='active'")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ration_lifecycle_status ON domain_agrar.ration_version_lifecycle (tenant_id,status,feeding_start)")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.ration_audit_events (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      ration_id VARCHAR NOT NULL REFERENCES domain_agrar.rations(id),
      version_id VARCHAR REFERENCES domain_agrar.ration_versions(id),
      event_type VARCHAR(40) NOT NULL,
      from_status VARCHAR(24), to_status VARCHAR(24),
      actor VARCHAR(160) NOT NULL, reason TEXT,
      delta JSONB NOT NULL DEFAULT '{}'::jsonb,
      occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ration_audit_timeline ON domain_agrar.ration_audit_events (tenant_id,ration_id,occurred_at DESC)")

    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_ration_version()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'ration_versions are immutable; create a new version';
      END;
      $$""")
    op.execute("""DROP TRIGGER IF EXISTS trg_immutable_ration_version ON domain_agrar.ration_versions""")
    op.execute("""CREATE TRIGGER trg_immutable_ration_version
      BEFORE UPDATE OR DELETE ON domain_agrar.ration_versions
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_ration_version()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_ration_version ON domain_agrar.ration_versions")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_ration_version()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_ration_audit_timeline")
    op.execute("DROP TABLE IF EXISTS domain_agrar.ration_audit_events")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_ration_lifecycle_status")
    op.execute("DROP INDEX IF EXISTS domain_agrar.uq_active_ration_per_group")
    op.execute("DROP TABLE IF EXISTS domain_agrar.ration_version_lifecycle")
    op.execute("DROP TABLE IF EXISTS domain_agrar.ration_versions")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_rations_group")
    op.execute("DROP TABLE IF EXISTS domain_agrar.rations")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_groups_tenant_active")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_groups")

