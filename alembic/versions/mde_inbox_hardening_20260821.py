"""Harden the existing mobile sync queue for the MDE operator inbox.

Revision ID: mde_inbox_hardening_20260821
Revises: feed_recipes_20260717
Create Date: 2026-08-21
"""

from __future__ import annotations

from alembic import op


revision = "mde_inbox_hardening_20260821"
down_revision = "feed_recipes_20260717"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_ops.mobile_event_queue ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE domain_ops.mobile_event_queue ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMPTZ")
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'mobile_event_queue_sync_status_check'
                   AND conrelid = 'domain_ops.mobile_event_queue'::regclass
            ) THEN
                ALTER TABLE domain_ops.mobile_event_queue
                    DROP CONSTRAINT mobile_event_queue_sync_status_check;
            END IF;
        END $$
    """)
    op.execute("""
        ALTER TABLE domain_ops.mobile_event_queue
        ADD CONSTRAINT mobile_event_queue_sync_status_check
        CHECK (sync_status IN ('pending','processing','done','failed','quarantined'))
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_ops.mobile_event_queue_audit (
            id          TEXT PRIMARY KEY,
            tenant_id   TEXT NOT NULL,
            event_id    TEXT NOT NULL REFERENCES domain_ops.mobile_event_queue(id) ON DELETE CASCADE,
            action      TEXT NOT NULL,
            actor       TEXT NOT NULL,
            reason      TEXT NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_mobile_queue_audit_tenant_event
        ON domain_ops.mobile_event_queue_audit (tenant_id, event_id, created_at DESC)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.mobile_event_queue_audit")
    op.execute("ALTER TABLE domain_ops.mobile_event_queue DROP COLUMN IF EXISTS last_attempt_at")
    op.execute("ALTER TABLE domain_ops.mobile_event_queue DROP COLUMN IF EXISTS retry_count")
    op.execute("ALTER TABLE domain_ops.mobile_event_queue DROP CONSTRAINT IF EXISTS mobile_event_queue_sync_status_check")
    op.execute("""
        ALTER TABLE domain_ops.mobile_event_queue
        ADD CONSTRAINT mobile_event_queue_sync_status_check
        CHECK (sync_status IN ('pending','processing','done','failed'))
    """)
