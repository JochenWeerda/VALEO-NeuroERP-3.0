"""Unified master-data audit + tenant four-eyes policy (FEED-RBAC-048).

Revision ID: feed_rbac_audit_20260717
Revises: feed_assist_20260717
"""

from alembic import op

revision = "feed_rbac_audit_20260717"
down_revision = "feed_assist_20260717"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_master_data_audit_events (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      entity_type VARCHAR(24) NOT NULL
        CHECK (entity_type IN ('business','feed','analysis','grant')),
      entity_id VARCHAR NOT NULL,
      event_type VARCHAR(60) NOT NULL,
      actor VARCHAR(160) NOT NULL,
      reason VARCHAR(2000),
      delta JSONB NOT NULL DEFAULT '{}'::jsonb,
      occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_md_audit_entity
      ON domain_agrar.feeding_master_data_audit_events (tenant_id, entity_id, occurred_at DESC)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_md_audit_type
      ON domain_agrar.feeding_master_data_audit_events (tenant_id, entity_type, occurred_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_md_audit()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'master data audit events are append-only';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_md_audit ON domain_agrar.feeding_master_data_audit_events")
    op.execute("""CREATE TRIGGER trg_immutable_md_audit
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_master_data_audit_events
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_md_audit()""")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_tenant_policies (
      tenant_id VARCHAR PRIMARY KEY REFERENCES domain_shared.tenants(id),
      four_eyes_approval BOOLEAN NOT NULL DEFAULT FALSE,
      updated_by VARCHAR(160) NOT NULL,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_tenant_policies")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_md_audit ON domain_agrar.feeding_master_data_audit_events")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_md_audit()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_md_audit_type")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_md_audit_entity")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_master_data_audit_events")
