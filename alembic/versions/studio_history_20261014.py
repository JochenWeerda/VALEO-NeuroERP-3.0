"""Transactional append-only Studio revision history."""
from alembic import op
revision = "studio_history_20261014"
down_revision = "control_findings_20261013"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE domain_shared.screen_definition_history (
      id VARCHAR(36) PRIMARY KEY, tenant_id VARCHAR NOT NULL,
      draft_id VARCHAR NOT NULL, actor VARCHAR NOT NULL,
      action VARCHAR(24) NOT NULL, previous_revision VARCHAR(64),
      revision VARCHAR(64) NOT NULL, snapshot JSONB NOT NULL,
      recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX ix_studio_history_tenant_draft ON domain_shared.screen_definition_history(tenant_id,draft_id,recorded_at,id);
    CREATE FUNCTION domain_shared.reject_studio_history_mutation() RETURNS trigger
      LANGUAGE plpgsql AS $$ BEGIN
        RAISE EXCEPTION 'Studio history is append-only';
      END $$;
    CREATE TRIGGER studio_history_append_only BEFORE UPDATE OR DELETE
      ON domain_shared.screen_definition_history FOR EACH ROW
      EXECUTE FUNCTION domain_shared.reject_studio_history_mutation();
    CREATE TRIGGER studio_history_no_truncate BEFORE TRUNCATE
      ON domain_shared.screen_definition_history FOR EACH STATEMENT
      EXECUTE FUNCTION domain_shared.reject_studio_history_mutation();
    """)


def downgrade():
    op.execute("DROP TABLE domain_shared.screen_definition_history")
    op.execute("DROP FUNCTION domain_shared.reject_studio_history_mutation()")
