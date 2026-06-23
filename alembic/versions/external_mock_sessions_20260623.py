"""EXTERNAL-MOCK-HARNESS-001: Mock-Session-Log fuer Dev/Test.

Revision ID: external_mock_sessions_20260623
Revises: meldewesen_lifecycle_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "external_mock_sessions_20260623"
down_revision = "meldewesen_lifecycle_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_dev_mock")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_dev_mock.mock_sessions (
            id          BIGSERIAL PRIMARY KEY,
            tenant_id   TEXT NOT NULL,
            system      TEXT NOT NULL,
            action      TEXT NOT NULL,
            request     JSONB,
            response    JSONB,
            called_at   TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_mock_sessions_tenant_system
            ON domain_dev_mock.mock_sessions (tenant_id, system)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_dev_mock.mock_sessions CASCADE")
    op.execute("DROP SCHEMA IF EXISTS domain_dev_mock CASCADE")
