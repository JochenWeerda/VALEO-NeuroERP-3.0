"""FIBU Connector Framework: Profile, Runs, Run-Items (domain_erp)

Revision ID: fibu_connector_framework_20260301
Revises: connectors_lohn_quadriga_20260301
Create Date: 2026-03-01

Einheitlicher Workflow für Lohn (PAYROLL) und Quadriga (Anlagenbuchhaltung):
- fibu_connector_profiles: Konfiguration/Mapping pro Mandant + Typ
- fibu_connector_runs: Import-Läufe mit Status (DRAFT→PARSED→VALIDATED→POSTED/FAILED/CANCELLED/REVERSED)
- fibu_connector_run_items: Zeilen pro Run (Preview, Fehler, posted_entity_id)
Artefakt-Metadaten (Hash, storage_key) auf Run; document_artifacts hat FK auf document_headers.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "fibu_connector_framework_20260301"
down_revision = "connectors_lohn_quadriga_20260301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fibu_connector_profiles",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("connector_type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("mapping", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "connector_type IN ('PAYROLL','QUADRIGA')",
            name="chk_fibu_connector_profile_type",
        ),
        schema="domain_erp",
    )
    op.create_index(
        "ix_fibu_connector_profiles_tenant_type",
        "fibu_connector_profiles",
        ["tenant_id", "connector_type"],
        unique=False,
        schema="domain_erp",
    )

    op.create_table(
        "fibu_connector_runs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("connector_type", sa.String(20), nullable=False),
        sa.Column("direction", sa.String(20), nullable=False, server_default="IMPORT"),
        sa.Column("profile_id", sa.String(36), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("source_artifact_storage_key", sa.String(500), nullable=True),
        sa.Column("source_artifact_sha256", sa.String(64), nullable=True),
        sa.Column("source_artifact_file_name", sa.String(255), nullable=True),
        sa.Column("protocol_artifact_storage_key", sa.String(500), nullable=True),
        sa.Column("protocol_artifact_sha256", sa.String(64), nullable=True),
        sa.Column("counts", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("totals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "connector_type IN ('PAYROLL','QUADRIGA')",
            name="chk_fibu_connector_run_type",
        ),
        sa.CheckConstraint(
            "direction IN ('IMPORT','EXPORT')",
            name="chk_fibu_connector_run_direction",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT','PARSED','VALIDATED','POSTED','FAILED','CANCELLED','REVERSED')",
            name="chk_fibu_connector_run_status",
        ),
        schema="domain_erp",
    )
    op.create_index(
        "ix_fibu_connector_runs_tenant_type",
        "fibu_connector_runs",
        ["tenant_id", "connector_type"],
        unique=False,
        schema="domain_erp",
    )
    op.create_index(
        "ix_fibu_connector_runs_tenant_idempotency",
        "fibu_connector_runs",
        ["tenant_id", "connector_type", "idempotency_key"],
        unique=True,
        schema="domain_erp",
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_index(
        "ix_fibu_connector_runs_created",
        "fibu_connector_runs",
        ["tenant_id", "created_at"],
        unique=False,
        schema="domain_erp",
    )

    op.create_table(
        "fibu_connector_run_items",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("line_no", sa.Integer(), nullable=False),
        sa.Column("item_type", sa.String(30), nullable=False, server_default="JOURNAL_ENTRY_LINE"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validation_errors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("posted_entity_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="OK"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["run_id"], ["domain_erp.fibu_connector_runs.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "item_type IN ('JOURNAL_ENTRY_LINE','OPEN_ITEM','ASSET_POSTING')",
            name="chk_fibu_connector_item_type",
        ),
        sa.CheckConstraint(
            "status IN ('OK','ERROR','POSTED')",
            name="chk_fibu_connector_item_status",
        ),
        schema="domain_erp",
    )
    op.create_index(
        "ix_fibu_connector_run_items_run_status",
        "fibu_connector_run_items",
        ["run_id", "status"],
        unique=False,
        schema="domain_erp",
    )


def downgrade() -> None:
    op.drop_index("ix_fibu_connector_run_items_run_status", table_name="fibu_connector_run_items", schema="domain_erp")
    op.drop_table("fibu_connector_run_items", schema="domain_erp")
    op.drop_index("ix_fibu_connector_runs_created", table_name="fibu_connector_runs", schema="domain_erp")
    op.drop_index("ix_fibu_connector_runs_tenant_idempotency", table_name="fibu_connector_runs", schema="domain_erp")
    op.drop_index("ix_fibu_connector_runs_tenant_type", table_name="fibu_connector_runs", schema="domain_erp")
    op.drop_table("fibu_connector_runs", schema="domain_erp")
    op.drop_index("ix_fibu_connector_profiles_tenant_type", table_name="fibu_connector_profiles", schema="domain_erp")
    op.drop_table("fibu_connector_profiles", schema="domain_erp")
