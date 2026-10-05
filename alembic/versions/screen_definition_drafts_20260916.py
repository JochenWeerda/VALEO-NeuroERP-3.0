"""Studio ScreenDefinition drafts for Masken-Studio persistency.

Revision ID: screen_definition_drafts_20260916
Revises: sales_invoice_lines_20260915
Create Date: 2026-09-16
"""

from alembic import op
import sqlalchemy as sa

revision = "screen_definition_drafts_20260916"
down_revision = "sales_invoice_lines_20260915"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_shared.screen_definition_drafts (
              id             VARCHAR PRIMARY KEY,
              tenant_id      VARCHAR NOT NULL REFERENCES domain_shared.tenants(id) ON DELETE CASCADE,
              screen_id      VARCHAR(96) NOT NULL,
              base_screen_id VARCHAR(96),
              definition     JSONB NOT NULL,
              status         VARCHAR(16) NOT NULL DEFAULT 'draft',
              readiness      JSONB,
              created_by     VARCHAR(64) NOT NULL,
              updated_by     VARCHAR(64) NOT NULL,
              updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
              CONSTRAINT uq_screen_definition_drafts_tenant_screen UNIQUE (tenant_id, screen_id)
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              ALTER TABLE domain_shared.screen_definition_drafts
                ADD CONSTRAINT ck_screen_definition_drafts_status
                CHECK (status IN ('draft', 'review', 'published_temp', 'retired'));
            EXCEPTION
              WHEN duplicate_object THEN NULL;
            END
            $$
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE INDEX IF NOT EXISTS ix_screen_definition_drafts_published
              ON domain_shared.screen_definition_drafts (tenant_id, status)
            """
        )
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_screen_definition_drafts_published")
    op.execute("DROP TABLE IF EXISTS domain_shared.screen_definition_drafts")
