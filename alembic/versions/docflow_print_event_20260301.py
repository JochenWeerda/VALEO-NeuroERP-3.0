"""Docflow: Druck/Export als Ereignis (printed_at, print_count) — GoBD Schritt 3

Revision ID: docflow_print_event_20260301
Revises: docflow_create_idemp_20260301
Create Date: 2026-03-01

- document_headers: printed_at, printed_by, print_count (Druck als Event, keine Sperre)
- optional: exported_at, exported_by für Export-Events
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "docflow_print_event_20260301"
down_revision = "docflow_create_idemp_20260301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "document_headers",
        sa.Column("printed_at", sa.DateTime(timezone=True), nullable=True),
        schema="domain_docflow",
    )
    op.add_column(
        "document_headers",
        sa.Column("printed_by", sa.String(length=100), nullable=True),
        schema="domain_docflow",
    )
    op.add_column(
        "document_headers",
        sa.Column("print_count", sa.Integer(), nullable=False, server_default="0"),
        schema="domain_docflow",
    )
    op.add_column(
        "document_headers",
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True),
        schema="domain_docflow",
    )
    op.add_column(
        "document_headers",
        sa.Column("exported_by", sa.String(length=100), nullable=True),
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_column("document_headers", "exported_by", schema="domain_docflow")
    op.drop_column("document_headers", "exported_at", schema="domain_docflow")
    op.drop_column("document_headers", "print_count", schema="domain_docflow")
    op.drop_column("document_headers", "printed_by", schema="domain_docflow")
    op.drop_column("document_headers", "printed_at", schema="domain_docflow")
