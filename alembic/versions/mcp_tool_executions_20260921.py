"""Transactional replay journal for authenticated ERP tool calls."""
from alembic import op

revision = "mcp_tool_executions_20260921"
down_revision = "mask_action_audit_20260921"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE public.mcp_tool_executions (
            tenant_id VARCHAR(100) NOT NULL,
            tool_name VARCHAR(200) NOT NULL,
            idempotency_key VARCHAR(200) NOT NULL,
            actor_id TEXT NOT NULL,
            payload_hash VARCHAR(64) NOT NULL,
            result JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tenant_id, tool_name, idempotency_key)
        )
    """)


def downgrade():
    raise RuntimeError("Retain the replay journal to prevent duplicate writes; roll back application code only")
