"""Extend flow spine instances with lifecycle state and timeline events

Revision ID: flow_spine_lifecycle_20260417
Revises: crm_customers_search_index_20260414
Create Date: 2026-04-17
"""

from alembic import op
import sqlalchemy as sa


revision = "flow_spine_lifecycle_20260417"
down_revision = "crm_customers_search_index_20260414"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'domain_ops'
                  AND table_name = 'ops_flow_spine_instances'
              ) THEN
                ALTER TABLE domain_ops.ops_flow_spine_instances
                  ADD COLUMN IF NOT EXISTS lifecycle_status VARCHAR(32) NOT NULL DEFAULT 'draft',
                  ADD COLUMN IF NOT EXISTS business_status VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS resume_node_id VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS resume_route VARCHAR(255),
                  ADD COLUMN IF NOT EXISTS resume_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                  ADD COLUMN IF NOT EXISTS assigned_owner VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMPTZ DEFAULT NOW(),
                  ADD COLUMN IF NOT EXISTS blocked_until TIMESTAMPTZ,
                  ADD COLUMN IF NOT EXISTS completion_reason_code VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS cancellation_reason_category VARCHAR(80),
                  ADD COLUMN IF NOT EXISTS cancellation_reason_code VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS failure_reason_category VARCHAR(80),
                  ADD COLUMN IF NOT EXISTS failure_reason_code VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS reason_note TEXT,
                  ADD COLUMN IF NOT EXISTS closed_at TIMESTAMPTZ,
                  ADD COLUMN IF NOT EXISTS closed_by VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ,
                  ADD COLUMN IF NOT EXISTS cancelled_by VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS failed_at TIMESTAMPTZ,
                  ADD COLUMN IF NOT EXISTS failed_by VARCHAR(120),
                  ADD COLUMN IF NOT EXISTS version_no INTEGER NOT NULL DEFAULT 1;
              END IF;
            END
            $$;
            """
        )
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_ops.ops_flow_spine_instance_events (
            id VARCHAR(36) PRIMARY KEY,
            instance_id VARCHAR(36) NOT NULL REFERENCES domain_ops.ops_flow_spine_instances(id) ON DELETE CASCADE,
            process_key VARCHAR(120) NOT NULL,
            tenant_id VARCHAR(120) NOT NULL DEFAULT 'default',
            event_type VARCHAR(60) NOT NULL,
            from_lifecycle_status VARCHAR(32),
            to_lifecycle_status VARCHAR(32),
            from_business_status VARCHAR(120),
            to_business_status VARCHAR(120),
            node_id VARCHAR(120),
            actor_id VARCHAR(120),
            reason_category VARCHAR(80),
            reason_code VARCHAR(120),
            reason_note TEXT,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instances_lifecycle_status "
        "ON domain_ops.ops_flow_spine_instances (lifecycle_status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instance_events_instance_id "
        "ON domain_ops.ops_flow_spine_instance_events (instance_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instance_events_process_key "
        "ON domain_ops.ops_flow_spine_instance_events (process_key)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instance_events_event_type "
        "ON domain_ops.ops_flow_spine_instance_events (event_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_flow_spine_instance_events_created_at "
        "ON domain_ops.ops_flow_spine_instance_events (created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.ops_flow_spine_instance_events")
    op.execute("DROP INDEX IF EXISTS domain_ops.ix_flow_spine_instances_lifecycle_status")

    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'domain_ops'
                  AND table_name = 'ops_flow_spine_instances'
              ) THEN
                ALTER TABLE domain_ops.ops_flow_spine_instances
                  DROP COLUMN IF EXISTS lifecycle_status,
                  DROP COLUMN IF EXISTS business_status,
                  DROP COLUMN IF EXISTS resume_node_id,
                  DROP COLUMN IF EXISTS resume_route,
                  DROP COLUMN IF EXISTS resume_payload,
                  DROP COLUMN IF EXISTS assigned_owner,
                  DROP COLUMN IF EXISTS last_activity_at,
                  DROP COLUMN IF EXISTS blocked_until,
                  DROP COLUMN IF EXISTS completion_reason_code,
                  DROP COLUMN IF EXISTS cancellation_reason_category,
                  DROP COLUMN IF EXISTS cancellation_reason_code,
                  DROP COLUMN IF EXISTS failure_reason_category,
                  DROP COLUMN IF EXISTS failure_reason_code,
                  DROP COLUMN IF EXISTS reason_note,
                  DROP COLUMN IF EXISTS closed_at,
                  DROP COLUMN IF EXISTS closed_by,
                  DROP COLUMN IF EXISTS cancelled_at,
                  DROP COLUMN IF EXISTS cancelled_by,
                  DROP COLUMN IF EXISTS failed_at,
                  DROP COLUMN IF EXISTS failed_by,
                  DROP COLUMN IF EXISTS version_no;
              END IF;
            END
            $$;
            """
        )
    )
