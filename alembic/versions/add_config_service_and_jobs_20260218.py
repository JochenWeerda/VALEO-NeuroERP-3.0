"""add_config_service_and_jobs_20260218

Revision ID: add_config_jobs_20260218
Revises: add_sysprops_20260218
Create Date: 2026-02-18 14:00:00.000000

Core Platform: Config Service (connectors, reporting-units, schedules) + Job Runner.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_config_jobs_20260218"
down_revision: Union[str, None] = "add_sysprops_20260218"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Connectors (API-Keys, Zertifikate, Credentials) ─────────────────────────
    op.create_table(
        "connectors",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("connector_key", sa.String(length=80), nullable=False, comment="z.B. intrastat, datev, zoll"),
        sa.Column("connector_type", sa.String(length=40), nullable=False, comment="api / oauth2 / cert / basic"),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Keys/URLs, verschlüsselt"),
        sa.Column("secrets_encrypted", sa.Text(), nullable=True, comment="Vault/KMS-Referenz oder DB-encrypted blob"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index("ix_connectors_tenant_key", "connectors", ["tenant_id", "connector_key"], unique=True, schema="domain_shared")

    # ── Reporting Units (Firmen / Meldeeinheiten) ───────────────────────────────
    op.create_table(
        "reporting_units",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("unit_key", sa.String(length=80), nullable=False, comment="z.B. DE123456789"),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("connector_id", sa.String(), nullable=True),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["connector_id"], ["domain_shared.connectors.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index("ix_reporting_units_tenant_key", "reporting_units", ["tenant_id", "unit_key"], unique=True, schema="domain_shared")

    # ── Schedules (Zeitpläne für Meldungen / Jobs) ─────────────────────────────
    op.create_table(
        "schedules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("schedule_key", sa.String(length=80), nullable=False, comment="z.B. intrastat_monthly, datev_export"),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("reporting_unit_id", sa.String(), nullable=True),
        sa.Column("cron_expr", sa.String(length=120), nullable=True, comment="Cron-Expression"),
        sa.Column("lead_days", sa.Integer(), nullable=False, server_default="5", comment="Tage vor Stichtag"),
        sa.Column("use_workday_rule", sa.Boolean(), nullable=False, server_default=sa.text("false"), comment="10. Arbeitstag etc."),
        sa.Column("output_format", sa.String(length=20), nullable=True, comment="csv / xml / json"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporting_unit_id"], ["domain_shared.reporting_units.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index("ix_schedules_tenant_key", "schedules", ["tenant_id", "schedule_key"], unique=True, schema="domain_shared")

    # ── Jobs (Lauf-Log / Artefakte) ────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("schedule_id", sa.String(), nullable=True),
        sa.Column("job_type", sa.String(length=80), nullable=False, comment="z.B. intrastat_export, datev_export"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending", comment="pending / running / completed / failed"),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_id"], ["domain_shared.schedules.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index("ix_jobs_tenant_status", "jobs", ["tenant_id", "status"], schema="domain_shared")
    op.create_index("ix_jobs_triggered_at", "jobs", ["triggered_at"], schema="domain_shared")

    # ── Job Artifacts (CSV/XML/JSON Outbox) ────────────────────────────────────
    op.create_table(
        "job_artifacts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("artifact_key", sa.String(length=120), nullable=False, comment="z.B. intrastat_2025-01.csv"),
        sa.Column("content_type", sa.String(length=80), nullable=False, comment="text/csv, application/xml, application/json"),
        sa.Column("file_path", sa.String(length=512), nullable=True, comment="Outbox/S3 path"),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["domain_shared.jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index("ix_job_artifacts_job_id", "job_artifacts", ["job_id"], schema="domain_shared")


def downgrade() -> None:
    op.drop_table("job_artifacts", schema="domain_shared")
    op.drop_index("ix_jobs_triggered_at", table_name="jobs", schema="domain_shared")
    op.drop_index("ix_jobs_tenant_status", table_name="jobs", schema="domain_shared")
    op.drop_table("jobs", schema="domain_shared")
    op.drop_index("ix_schedules_tenant_key", table_name="schedules", schema="domain_shared")
    op.drop_table("schedules", schema="domain_shared")
    op.drop_index("ix_reporting_units_tenant_key", table_name="reporting_units", schema="domain_shared")
    op.drop_table("reporting_units", schema="domain_shared")
    op.drop_index("ix_connectors_tenant_key", table_name="connectors", schema="domain_shared")
    op.drop_table("connectors", schema="domain_shared")
