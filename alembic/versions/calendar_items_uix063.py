"""UIX-063: Planungskalender Read-Model und ICS-Token.

Revision ID: calendar_items_uix063
Revises: inv_lot_depth_spec_p1_08
"""
from __future__ import annotations

from alembic import op

revision = "calendar_items_uix063"
down_revision = "inv_lot_depth_spec_p1_08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.calendar_items (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
            source VARCHAR(48) NOT NULL,
            source_key VARCHAR(128) NOT NULL,
            layer VARCHAR(16) NOT NULL,
            item_type VARCHAR(48) NOT NULL,
            title VARCHAR(200) NOT NULL,
            starts_at TIMESTAMPTZ NOT NULL,
            ends_at TIMESTAMPTZ,
            all_day BOOLEAN NOT NULL DEFAULT false,
            status VARCHAR(16) NOT NULL DEFAULT 'projected',
            object_type VARCHAR(64),
            object_id VARCHAR(64),
            object_screen_id VARCHAR(96),
            object_route VARCHAR(200),
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ,
            CONSTRAINT uq_calendar_items_source UNIQUE (tenant_id, source, source_key),
            CONSTRAINT ck_calendar_items_status CHECK (status IN ('projected', 'proposed', 'confirmed', 'dismissed'))
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_calendar_items_range
        ON domain_shared.calendar_items (tenant_id, starts_at, layer)
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.calendar_ics_tokens (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
            user_ref VARCHAR(128) NOT NULL DEFAULT 'default',
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            rotated_at TIMESTAMPTZ
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_calendar_ics_tokens_lookup
        ON domain_shared.calendar_ics_tokens (tenant_id, user_ref, active)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_calendar_ics_tokens_lookup")
    op.execute("DROP TABLE IF EXISTS domain_shared.calendar_ics_tokens")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_calendar_items_range")
    op.execute("DROP TABLE IF EXISTS domain_shared.calendar_items")
