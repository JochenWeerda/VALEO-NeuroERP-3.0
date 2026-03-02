"""GoBD: Archiv (document_artifacts) + E-Rechnung XML-Speicher

Revision ID: gobd_archiv_erechnung_20260301
Revises: merge_heads_20260301
Create Date: 2026-03-01

- document_artifacts: Belegartefakte mit Content-Hash (PDF/XML)
- invoice_xml_store: E-Rechnung XML als führendes Original (XRechnung/ZUGFeRD)
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "gobd_archiv_erechnung_20260301"
down_revision = "merge_heads_20260301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_artifacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("header_id", sa.String(length=36), nullable=False),
        sa.Column("artifact_type", sa.String(length=20), nullable=False),
        sa.Column("content_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "artifact_type IN ('pdf','xml','html','other')",
            name="chk_doc_artifact_type",
        ),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_doc_artifacts_header_type",
        "document_artifacts",
        ["tenant_id", "header_id", "artifact_type"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "invoice_xml_store",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("header_id", sa.String(length=36), nullable=False),
        sa.Column("content_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("format_type", sa.String(length=40), nullable=False, server_default="XRechnung"),
        sa.Column("validation_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("validation_errors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "header_id", name="uq_invoice_xml_header"),
        sa.CheckConstraint(
            "validation_status IN ('pending','valid','invalid')",
            name="chk_invoice_xml_validation",
        ),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_invoice_xml_tenant_created",
        "invoice_xml_store",
        ["tenant_id", "created_at"],
        unique=False,
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_index("ix_invoice_xml_tenant_created", table_name="invoice_xml_store", schema="domain_docflow")
    op.drop_table("invoice_xml_store", schema="domain_docflow")
    op.drop_index("ix_doc_artifacts_header_type", table_name="document_artifacts", schema="domain_docflow")
    op.drop_table("document_artifacts", schema="domain_docflow")
