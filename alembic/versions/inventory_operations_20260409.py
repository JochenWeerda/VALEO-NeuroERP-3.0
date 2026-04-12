"""Add source_document fields to stock_movements

Revision ID: inventory_operations_20260409
Revises: perf_indexes_20260408
Create Date: 2026-04-09
"""

from alembic import op
import sqlalchemy as sa

revision = "inventory_operations_20260409"
down_revision = "perf_indexes_20260408"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add source_document_id and source_document_type to stock_movements
    op.add_column(
        "inventory_stock_movements",
        sa.Column("source_document_id", sa.String(64), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "inventory_stock_movements",
        sa.Column("source_document_type", sa.String(40), nullable=True),
        schema="domain_inventory",
    )

    # Index for document chain lookups
    op.create_index(
        "ix_stock_movements_source_doc",
        "inventory_stock_movements",
        ["source_document_type", "source_document_id"],
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stock_movements_source_doc",
        table_name="inventory_stock_movements",
        schema="domain_inventory",
    )
    op.drop_column("inventory_stock_movements", "source_document_type", schema="domain_inventory")
    op.drop_column("inventory_stock_movements", "source_document_id", schema="domain_inventory")
