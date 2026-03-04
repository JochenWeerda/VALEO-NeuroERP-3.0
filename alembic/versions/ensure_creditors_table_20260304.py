"""ensure creditors table exists after multi-head merges

Revision ID: b7c8d9e0f1a2
Revises: d1e2f3a4b5c6, missing_ops_20260304
Create Date: 2026-03-04 19:35:00
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "b7c8d9e0f1a2"
down_revision = "merge_heads_20260304"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")

    op.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS domain_erp.creditors (
                id VARCHAR(64) PRIMARY KEY,
                tenant_id VARCHAR(64),
                creditor_number VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                address JSONB,
                payment_terms VARCHAR(100) DEFAULT '30_days',
                current_balance NUMERIC(15,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )

    op.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_creditors_tenant_creditor_number
            ON domain_erp.creditors (tenant_id, creditor_number)
            """
        )
    )
    op.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_creditors_tenant_id
            ON domain_erp.creditors (tenant_id)
            """
        )
    )
    op.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_creditors_is_active
            ON domain_erp.creditors (is_active)
            """
        )
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_erp.creditors")
