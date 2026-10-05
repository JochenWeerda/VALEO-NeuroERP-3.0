"""Immutable ration templates (FEED-EDITOR-025).

Revision ID: feed_editor_templates_20260716
Revises: feed_editor_evaluations_20260715
"""

from alembic import op

revision = "feed_editor_templates_20260716"
down_revision = "feed_editor_evaluations_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.ration_templates (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      business_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_businesses(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      name VARCHAR(240) NOT NULL,
      description VARCHAR(2000),
      source_ration_version_id VARCHAR NOT NULL REFERENCES domain_agrar.ration_versions(id),
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_ration_template_name UNIQUE (tenant_id, business_id, name)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_ration_templates_business
      ON domain_agrar.ration_templates (tenant_id, business_id, created_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_ration_template()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'ration_templates are immutable; create a new template';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_ration_template ON domain_agrar.ration_templates")
    op.execute("""CREATE TRIGGER trg_immutable_ration_template
      BEFORE UPDATE OR DELETE ON domain_agrar.ration_templates
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_ration_template()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_ration_template ON domain_agrar.ration_templates")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_ration_template()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_ration_templates_business")
    op.execute("DROP TABLE IF EXISTS domain_agrar.ration_templates")
