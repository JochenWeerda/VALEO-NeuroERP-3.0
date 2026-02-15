"""docflow pos tse compliance table

Revision ID: docflow_pos_tse_compliance_20260215
Revises: docflow_core_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "docflow_pos_tse_compliance_20260215"
down_revision = "docflow_core_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pos_receipt_compliance",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("header_id", sa.String(length=36), nullable=False),
        sa.Column("terminal_id", sa.String(length=60), nullable=False),
        sa.Column("cash_register_id", sa.String(length=60), nullable=True),
        sa.Column("transaction_type", sa.String(length=20), nullable=False, server_default="sale"),
        sa.Column("payment_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tse_transaction_id", sa.String(length=120), nullable=False),
        sa.Column("tse_signature", sa.Text(), nullable=False),
        sa.Column("tse_signature_counter", sa.BigInteger(), nullable=True),
        sa.Column("transaction_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("transaction_ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("receipt_issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dsfinvk_export_batch_id", sa.String(length=120), nullable=True),
        sa.Column("correction_type", sa.String(length=20), nullable=True),
        sa.Column("original_header_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["header_id"], ["domain_docflow.document_headers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["original_header_id"], ["domain_docflow.document_headers.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "header_id", name="uq_pos_tse_header"),
        sa.CheckConstraint(
            "transaction_type IN ('sale','storno','retoure','voucher_sale','voucher_redeem')",
            name="chk_pos_tse_transaction_type",
        ),
        sa.CheckConstraint(
            "correction_type IS NULL OR correction_type IN ('storno','retoure')",
            name="chk_pos_tse_correction_type",
        ),
        sa.CheckConstraint(
            "(correction_type IS NULL AND original_header_id IS NULL) OR "
            "(correction_type IS NOT NULL AND original_header_id IS NOT NULL)",
            name="chk_pos_tse_original_ref",
        ),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_pos_tse_tenant_terminal_time",
        "pos_receipt_compliance",
        ["tenant_id", "terminal_id", "transaction_ended_at"],
        unique=False,
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_index("ix_pos_tse_tenant_terminal_time", table_name="pos_receipt_compliance", schema="domain_docflow")
    op.drop_table("pos_receipt_compliance", schema="domain_docflow")
