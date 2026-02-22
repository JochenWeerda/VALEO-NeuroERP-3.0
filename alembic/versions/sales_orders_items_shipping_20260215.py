"""Add sales_order_items relation and shipping_method on sales_orders.

Revision ID: sales_orders_items_shipping_20260215
Revises: articles_master_fields_gap_83_20260215
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "sales_orders_items_shipping_20260215"
down_revision = "articles_master_fields_gap_83_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sales_orders",
        sa.Column("shipping_method", sa.String(length=40), nullable=True),
        schema="domain_crm",
    )

    op.create_table(
        "sales_order_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("order_id", sa.String(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("article_number", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("discount_percent", sa.Numeric(7, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("line_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["domain_crm.sales_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", "line_number", name="uq_sales_order_items_order_line"),
        sa.CheckConstraint("quantity >= 0", name="ck_sales_order_items_qty_nonneg"),
        sa.CheckConstraint("unit_price >= 0", name="ck_sales_order_items_price_nonneg"),
        sa.CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="ck_sales_order_items_discount_range",
        ),
        schema="domain_crm",
    )
    op.create_index(
        "ix_sales_order_items_order_id",
        "sales_order_items",
        ["order_id"],
        unique=False,
        schema="domain_crm",
    )
    op.create_index(
        "ix_sales_order_items_article_number",
        "sales_order_items",
        ["article_number"],
        unique=False,
        schema="domain_crm",
    )


def downgrade() -> None:
    op.drop_index("ix_sales_order_items_article_number", table_name="sales_order_items", schema="domain_crm")
    op.drop_index("ix_sales_order_items_order_id", table_name="sales_order_items", schema="domain_crm")
    op.drop_table("sales_order_items", schema="domain_crm")
    op.drop_column("sales_orders", "shipping_method", schema="domain_crm")
