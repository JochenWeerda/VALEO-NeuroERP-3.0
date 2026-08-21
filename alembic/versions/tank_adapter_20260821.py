"""Tank adapter inbox and delivery-note handover.

Revision ID: tank_adapter_20260821
Revises: mail_workspace_20260821
"""

from alembic import op

revision = "tank_adapter_20260821"
down_revision = "mail_workspace_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_ops;
      CREATE TABLE IF NOT EXISTS domain_ops.tank_adapter_intake (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, adapter_key TEXT NOT NULL,
        external_id TEXT NOT NULL, payload JSONB NOT NULL, payload_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'received', validation_errors JSONB NOT NULL DEFAULT '[]'::jsonb,
        rule_result JSONB NOT NULL DEFAULT '{}'::jsonb, zapfung_id TEXT,
        delivery_handover_id TEXT, retry_count INTEGER NOT NULL DEFAULT 0,
        received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), processed_at TIMESTAMPTZ,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,adapter_key,external_id),
        CHECK (status IN ('received','validated','error','processed'))
      );
      CREATE INDEX IF NOT EXISTS ix_tank_adapter_inbox
        ON domain_ops.tank_adapter_intake (tenant_id,status,adapter_key,received_at);
      CREATE TABLE IF NOT EXISTS domain_ops.tank_delivery_note_outbox (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, intake_id TEXT NOT NULL,
        event_type TEXT NOT NULL DEFAULT 'tank.delivery-note.requested',
        idempotency_key TEXT NOT NULL, payload JSONB NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        delivered_at TIMESTAMPTZ, error_message TEXT,
        UNIQUE (tenant_id,idempotency_key),
        CHECK (status IN ('pending','delivered','error'))
      );
      CREATE TABLE IF NOT EXISTS domain_ops.tank_adapter_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, intake_id TEXT NOT NULL,
        action TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
        payload_hash TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_ops.tank_adapter_audit;
      DROP TABLE IF EXISTS domain_ops.tank_delivery_note_outbox;
      DROP TABLE IF EXISTS domain_ops.tank_adapter_intake;
    """)
