"""Versioned feeding-group profiles and parameter history (FEED-CORE-016).

Revision ID: feed_core_groups_20260715
Revises: feed_core_business_20260715
"""
from alembic import op

revision = "feed_core_groups_20260715"
down_revision = "feed_core_business_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE domain_agrar.feeding_groups
      ADD COLUMN IF NOT EXISTS profile_code VARCHAR(40) NOT NULL DEFAULT 'custom',
      ADD COLUMN IF NOT EXISTS pregnancy_status VARCHAR(20) NOT NULL DEFAULT 'unknown',
      ADD COLUMN IF NOT EXISTS gestation_day INTEGER,
      ADD COLUMN IF NOT EXISTS milk_fat_pct NUMERIC(6,3),
      ADD COLUMN IF NOT EXISTS milk_protein_pct NUMERIC(6,3),
      ADD COLUMN IF NOT EXISTS milk_urea_mg_dl NUMERIC(8,3),
      ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
      ADD COLUMN IF NOT EXISTS valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
      ADD COLUMN IF NOT EXISTS valid_until DATE,
      ADD COLUMN IF NOT EXISTS revision INTEGER NOT NULL DEFAULT 1""")
    op.execute("""ALTER TABLE domain_agrar.feeding_groups
      ADD CONSTRAINT ck_feeding_group_profile CHECK (profile_code IN
        ('custom','fresh_cow','high_yield_cow','mid_lactation_cow','late_lactation_cow',
         'dry_far_off','dry_close_up','heifer','calf','beef_cattle')),
      ADD CONSTRAINT ck_feeding_group_pregnancy CHECK (pregnancy_status IN ('unknown','open','pregnant')),
      ADD CONSTRAINT ck_feeding_group_gestation CHECK
        (gestation_day IS NULL OR (pregnancy_status='pregnant' AND gestation_day BETWEEN 0 AND 305)),
      ADD CONSTRAINT ck_feeding_group_milk_fat CHECK (milk_fat_pct IS NULL OR milk_fat_pct BETWEEN 0 AND 15),
      ADD CONSTRAINT ck_feeding_group_milk_protein CHECK (milk_protein_pct IS NULL OR milk_protein_pct BETWEEN 0 AND 10),
      ADD CONSTRAINT ck_feeding_group_milk_urea CHECK (milk_urea_mg_dl IS NULL OR milk_urea_mg_dl BETWEEN 0 AND 100),
      ADD CONSTRAINT ck_feeding_group_risk CHECK (risk_level IN ('low','medium','high','critical')),
      ADD CONSTRAINT ck_feeding_group_validity CHECK (valid_until IS NULL OR valid_until >= valid_from),
      ADD CONSTRAINT ck_feeding_group_revision CHECK (revision > 0)""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_group_revisions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      revision INTEGER NOT NULL CHECK (revision > 0),
      snapshot JSONB NOT NULL,
      reason VARCHAR(500) NOT NULL,
      changed_by VARCHAR(160) NOT NULL,
      changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_group_revision UNIQUE (tenant_id,group_id,revision)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_group_revisions_timeline ON domain_agrar.feeding_group_revisions (tenant_id,group_id,revision DESC)")
    op.execute("""INSERT INTO domain_agrar.feeding_group_revisions
      (id,tenant_id,group_id,revision,snapshot,reason,changed_by,changed_at)
      SELECT g.id || '-revision-1',g.tenant_id,g.id,1,to_jsonb(g),'Bestandsuebernahme',
             COALESCE(g.updated_by,g.created_by),COALESCE(g.updated_at,g.created_at)
      FROM domain_agrar.feeding_groups g
      ON CONFLICT (tenant_id,group_id,revision) DO NOTHING""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_group_revision()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'feeding_group_revisions are immutable';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_group_revision ON domain_agrar.feeding_group_revisions")
    op.execute("""CREATE TRIGGER trg_immutable_feeding_group_revision
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_group_revisions
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_group_revision()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_group_revision ON domain_agrar.feeding_group_revisions")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_group_revision()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_group_revisions_timeline")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_group_revisions")
    for column in (
        "revision", "valid_until", "valid_from", "risk_level", "milk_urea_mg_dl",
        "milk_protein_pct", "milk_fat_pct", "gestation_day", "pregnancy_status", "profile_code",
    ):
        op.execute(f"ALTER TABLE domain_agrar.feeding_groups DROP COLUMN IF EXISTS {column}")  # noqa: S608 -- fixed allowlist
