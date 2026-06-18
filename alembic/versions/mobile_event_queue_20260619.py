"""MOB-SYNC-001: Mobile Offline-Sync Event-Queue

Revision ID: mobile_event_queue_20260619
Revises: wms_material_flow_stock_link_20260619
Create Date: 2026-06-19
"""

from __future__ import annotations
from alembic import op

revision = "mobile_event_queue_20260619"
down_revision = "wms_material_flow_stock_link_20260619"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_ops.mobile_event_queue (
            id              TEXT PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            device_id       TEXT NOT NULL,
            event_type      TEXT NOT NULL,
            payload         JSONB NOT NULL DEFAULT '{}',
            sync_status     TEXT NOT NULL DEFAULT 'pending'
                CHECK (sync_status IN ('pending','processing','done','failed')),
            error_message   TEXT,
            idempotency_key TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            processed_at    TIMESTAMPTZ,
            CONSTRAINT uq_mobile_event_idempotency
                UNIQUE (tenant_id, device_id, idempotency_key)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_mobile_queue_tenant_status
        ON domain_ops.mobile_event_queue (tenant_id, sync_status, created_at)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.mobile_event_queue")
