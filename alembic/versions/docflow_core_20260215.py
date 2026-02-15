"""docflow core tables and command idempotency

Revision ID: docflow_core_20260215
Revises: merge_sales_orders_and_consignment_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "docflow_core_20260215"
down_revision = "merge_sales_orders_and_consignment_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_docflow")

    op.create_table(
        "number_series",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("doc_type", sa.String(length=40), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("prefix", sa.String(length=20), nullable=False),
        sa.Column("counter", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("width", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "doc_type", "year", name="uq_docflow_number_series_scope"),
        schema="domain_docflow",
    )

    op.create_table(
        "document_headers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("doc_type", sa.String(length=40), nullable=False),
        sa.Column("doc_number", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("source_system", sa.String(length=40), nullable=False, server_default="docflow"),
        sa.Column("source_ref", sa.String(length=80), nullable=True),
        sa.Column("customer_id", sa.String(length=64), nullable=True),
        sa.Column("supplier_id", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("total_net", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("total_tax", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("total_gross", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("document_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("posting_date", sa.Date(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "doc_type", "doc_number", name="uq_docflow_header_number"),
        sa.CheckConstraint(
            "status IN ('draft','open','completed','posted','reversed','cancelled')",
            name="chk_docflow_header_status",
        ),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_headers_tenant_type_created",
        "document_headers",
        ["tenant_id", "doc_type", "created_at"],
        unique=False,
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_headers_source",
        "document_headers",
        ["source_system", "source_ref"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "document_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("header_id", sa.String(length=36), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("source_line_id", sa.String(length=36), nullable=True),
        sa.Column("article_number", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("unit_price", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("discount_percent", sa.Numeric(7, 3), nullable=False, server_default="0"),
        sa.Column("tax_rate", sa.Numeric(6, 3), nullable=False, server_default="0"),
        sa.Column("line_total_net", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("line_total_tax", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("line_total_gross", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("batch_id", sa.String(length=64), nullable=True),
        sa.Column("charge", sa.String(length=64), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("header_id", "line_number", name="uq_docflow_item_line"),
        sa.CheckConstraint("quantity >= 0", name="chk_docflow_item_qty_non_negative"),
        sa.CheckConstraint("unit_price >= 0", name="chk_docflow_item_price_non_negative"),
        sa.CheckConstraint("discount_percent >= 0 AND discount_percent <= 100", name="chk_docflow_item_discount_range"),
        sa.CheckConstraint("tax_rate >= 0 AND tax_rate <= 100", name="chk_docflow_item_tax_range"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_items_tenant_article",
        "document_items",
        ["tenant_id", "article_number"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "document_links",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("from_header_id", sa.String(length=36), nullable=False),
        sa.Column("to_header_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=40), nullable=False),
        sa.Column("from_item_id", sa.String(length=36), nullable=True),
        sa.Column("to_item_id", sa.String(length=36), nullable=True),
        sa.Column("quantity_linked", sa.Numeric(14, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["from_header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_item_id"], ["domain_docflow.document_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_item_id"], ["domain_docflow.document_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("quantity_linked >= 0", name="chk_docflow_link_qty_non_negative"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_links_from_to",
        "document_links",
        ["tenant_id", "from_header_id", "to_header_id"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "document_postings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("header_id", sa.String(length=36), nullable=False),
        sa.Column("posting_type", sa.String(length=20), nullable=False),
        sa.Column("journal_entry_id", sa.String(length=64), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("idempotency_key", sa.String(length=120), nullable=True),
        sa.Column("outbox_event_id", sa.String(length=64), nullable=True),
        sa.Column("posted_by", sa.String(length=100), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("posting_type IN ('post','reverse')", name="chk_docflow_posting_type"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_docflow_postings_header_posted",
        "document_postings",
        ["tenant_id", "header_id", "posted_at"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "command_idempotency_keys",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("command_name", sa.String(length=40), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "command_name",
            "resource_id",
            "idempotency_key",
            name="uq_docflow_command_idempotency",
        ),
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_table("command_idempotency_keys", schema="domain_docflow")
    op.drop_index("ix_docflow_postings_header_posted", table_name="document_postings", schema="domain_docflow")
    op.drop_table("document_postings", schema="domain_docflow")
    op.drop_index("ix_docflow_links_from_to", table_name="document_links", schema="domain_docflow")
    op.drop_table("document_links", schema="domain_docflow")
    op.drop_index("ix_docflow_items_tenant_article", table_name="document_items", schema="domain_docflow")
    op.drop_table("document_items", schema="domain_docflow")
    op.drop_index("ix_docflow_headers_source", table_name="document_headers", schema="domain_docflow")
    op.drop_index("ix_docflow_headers_tenant_type_created", table_name="document_headers", schema="domain_docflow")
    op.drop_table("document_headers", schema="domain_docflow")
    op.drop_table("number_series", schema="domain_docflow")
