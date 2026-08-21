"""Team calendar ownership and privacy model.

Revision ID: team_calendar_20260821
Revises: query_center_20260821
"""

from alembic import op

revision = "team_calendar_20260821"
down_revision = "query_center_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      ALTER TABLE domain_shared.calendar_items ADD COLUMN IF NOT EXISTS owner_id TEXT;
      ALTER TABLE domain_shared.calendar_items ADD COLUMN IF NOT EXISTS team_id TEXT;
      ALTER TABLE domain_shared.calendar_items ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'public';
      ALTER TABLE domain_shared.calendar_items ADD COLUMN IF NOT EXISTS response_status TEXT NOT NULL DEFAULT 'accepted';
      ALTER TABLE domain_shared.calendar_items DROP CONSTRAINT IF EXISTS ck_calendar_items_visibility;
      ALTER TABLE domain_shared.calendar_items ADD CONSTRAINT ck_calendar_items_visibility
        CHECK (visibility IN ('public','team','free_busy','private'));
      ALTER TABLE domain_shared.calendar_items DROP CONSTRAINT IF EXISTS ck_calendar_items_response;
      ALTER TABLE domain_shared.calendar_items ADD CONSTRAINT ck_calendar_items_response
        CHECK (response_status IN ('accepted','tentative','declined'));
      CREATE INDEX IF NOT EXISTS ix_calendar_items_team_view
        ON domain_shared.calendar_items (tenant_id, team_id, owner_id, starts_at, response_status);
      CREATE TABLE IF NOT EXISTS domain_shared.calendar_team_memberships (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, team_id TEXT NOT NULL,
        user_ref TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'member', active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,team_id,user_ref)
      );
      CREATE INDEX IF NOT EXISTS ix_calendar_team_membership_user
        ON domain_shared.calendar_team_memberships (tenant_id,user_ref,active);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_shared.calendar_team_memberships;
      DROP INDEX IF EXISTS domain_shared.ix_calendar_items_team_view;
      ALTER TABLE domain_shared.calendar_items DROP COLUMN IF EXISTS response_status;
      ALTER TABLE domain_shared.calendar_items DROP COLUMN IF EXISTS visibility;
      ALTER TABLE domain_shared.calendar_items DROP COLUMN IF EXISTS team_id;
      ALTER TABLE domain_shared.calendar_items DROP COLUMN IF EXISTS owner_id;
    """)
