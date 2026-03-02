"""Docflow: Create-Idempotency-Tabelle + Docflow-Link UNIQUE (GoBD Schritt 3)

Revision ID: docflow_create_idemp_20260301
Revises: docflow_core_20260215
Create Date: 2026-03-01

- create_request_idempotency: Idempotency für POST Create (key -> doc_id)
- document_header_links: Ein Link pro Quelle+Relation (UNIQUE), verhindert Doppelbelege beim Convert
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "docflow_create_idemp_20260301"
down_revision = "docflow_core_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_docflow")
    op.create_table(
        "create_request_idempotency",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("doc_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_docflow_create_idempotency"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_create_idemp_tenant_key",
        "create_request_idempotency",
        ["tenant_id", "idempotency_key"],
        unique=True,
        schema="domain_docflow",
    )

    op.create_table(
        "document_header_links",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("from_header_id", sa.String(length=36), nullable=False),
        sa.Column("to_header_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["from_header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "from_header_id", "relation_type", name="uq_docflow_header_link_source_relation"
        ),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_header_links_from_relation",
        "document_header_links",
        ["tenant_id", "from_header_id", "relation_type"],
        unique=True,
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_index("ix_docflow_header_links_from_relation", table_name="document_header_links", schema="domain_docflow")
    op.drop_table("document_header_links", schema="domain_docflow")
    op.drop_index("ix_docflow_create_idemp_tenant_key", table_name="create_request_idempotency", schema="domain_docflow")
    op.drop_table("create_request_idempotency", schema="domain_docflow")
