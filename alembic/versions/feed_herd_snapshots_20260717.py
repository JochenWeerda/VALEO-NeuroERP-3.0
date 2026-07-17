"""Animal group snapshots + parameter confirmation (FEED-HERD-043).

Revision ID: feed_herd_snapshots_20260717
Revises: feed_reports_types_20260716
"""

from alembic import op

revision = "feed_herd_snapshots_20260717"
down_revision = "feed_reports_types_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.animal_group_snapshots (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      snapshot_date DATE NOT NULL,
      cow_count INTEGER,
      kpis JSONB NOT NULL DEFAULT '{}'::jsonb,
      source VARCHAR(40) NOT NULL DEFAULT 'herd_data',
      source_observation_id VARCHAR,
      condensed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_animal_group_snapshot UNIQUE (tenant_id, group_id, snapshot_date)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_animal_group_snapshots_group
      ON domain_agrar.animal_group_snapshots (tenant_id, group_id, snapshot_date DESC)""")
    op.execute("""ALTER TABLE domain_agrar.feeding_groups
      ADD COLUMN IF NOT EXISTS parameters_confirmed_at TIMESTAMPTZ""")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_agrar.feeding_groups DROP COLUMN IF EXISTS parameters_confirmed_at")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_animal_group_snapshots_group")
    op.execute("DROP TABLE IF EXISTS domain_agrar.animal_group_snapshots")
