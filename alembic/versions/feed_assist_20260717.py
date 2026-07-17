"""Audited deterministic assist proposals (FEED-AI-046).

Revision ID: feed_assist_20260717
Revises: feed_benchmark_20260717
"""

from alembic import op

revision = "feed_assist_20260717"
down_revision = "feed_benchmark_20260717"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_assist_proposals (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      agent VARCHAR(60) NOT NULL,
      objective VARCHAR(400) NOT NULL,
      group_id VARCHAR,
      content JSONB NOT NULL,
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_assist_proposals_group
      ON domain_agrar.feeding_assist_proposals (tenant_id, group_id, created_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_assist_proposal()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'assist proposals are append-only';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_assist_proposal ON domain_agrar.feeding_assist_proposals")
    op.execute("""CREATE TRIGGER trg_immutable_assist_proposal
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_assist_proposals
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_assist_proposal()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_assist_proposal ON domain_agrar.feeding_assist_proposals")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_assist_proposal()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_assist_proposals_group")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_assist_proposals")
