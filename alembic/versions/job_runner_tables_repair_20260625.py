"""Repair job runner tables for runtime sweep category A.

Revision ID: job_runner_tables_repair_20260625
Revises: hr_planning_tables_20260625
Create Date: 2026-06-25
"""

from alembic import op


revision = "job_runner_tables_repair_20260625"
down_revision = "hr_planning_tables_20260625"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.jobs (
            id              VARCHAR PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            schedule_id     VARCHAR,
            job_type        VARCHAR(80) NOT NULL,
            status          VARCHAR(20) NOT NULL DEFAULT 'pending',
            triggered_at    TIMESTAMPTZ DEFAULT NOW(),
            completed_at    TIMESTAMPTZ,
            error_message   TEXT,
            dry_run         BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_tenant_status ON domain_shared.jobs (tenant_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_triggered_at ON domain_shared.jobs (triggered_at)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.job_artifacts (
            id                 VARCHAR PRIMARY KEY,
            job_id             VARCHAR NOT NULL REFERENCES domain_shared.jobs(id) ON DELETE CASCADE,
            artifact_key       VARCHAR(120) NOT NULL,
            content_type       VARCHAR(80) NOT NULL,
            file_path          VARCHAR(512),
            file_size_bytes    BIGINT,
            checksum_sha256    VARCHAR(64),
            created_at         TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_job_artifacts_job_id ON domain_shared.job_artifacts (job_id)"
    )


def downgrade() -> None:
    # Repair migration: do not drop shared operational data on downgrade.
    pass
