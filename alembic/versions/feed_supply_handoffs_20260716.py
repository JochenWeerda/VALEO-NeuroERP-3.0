"""Controlled feeding supply procurement handoffs (FEED-SUP-028).

Revision ID: feed_supply_handoffs_20260716
Revises: feed_plan_versions_20260716
"""
from alembic import op

revision = "feed_supply_handoffs_20260716"
down_revision = "feed_plan_versions_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_supply_handoffs (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      plan_version_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_plan_versions(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      feed_id VARCHAR NOT NULL,
      projection JSONB NOT NULL,
      status VARCHAR(30) NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed','accepted','rejected','cancelled')),
      idempotency_key VARCHAR(160) NOT NULL,
      request_hash VARCHAR(64) NOT NULL,
      reason VARCHAR(2000) NOT NULL,
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id,idempotency_key)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_supply_handoffs_plan
      ON domain_agrar.feeding_supply_handoffs (tenant_id,plan_version_id,created_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_supply_handoff()
      RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'feeding supply handoffs are append-only'; END; $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_supply_handoff ON domain_agrar.feeding_supply_handoffs")
    op.execute("""CREATE TRIGGER trg_immutable_feeding_supply_handoff BEFORE UPDATE OR DELETE
      ON domain_agrar.feeding_supply_handoffs FOR EACH ROW
      EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_supply_handoff()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_supply_handoff ON domain_agrar.feeding_supply_handoffs")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_supply_handoff()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_supply_handoffs")
