"""Add sales_offers, sales_offer_items, sales_orders, sales_order_items to domain_crm

Revision ID: sales_angebot_auftrag_tables_20260225
Revises: fuhrpark_tables_speditionen_20260225
Create Date: 2026-02-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "sales_angebot_auftrag_tables_20260225"
down_revision = "fuhrpark_tables_speditionen_20260225"
branch_labels = None
depends_on = None


def _table_exists(inspector, tablename: str, schema: str = "domain_crm") -> bool:
    return tablename in inspector.get_table_names(schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # ── domain_crm.sales_offers ───────────────────────────────────────────
    if not _table_exists(inspector, "sales_offers"):
        op.create_table(
            "sales_offers",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("tenant_id", sa.String, nullable=False),
            sa.Column("offer_number", sa.String(64), nullable=False),
            sa.Column("customer_id", sa.String, nullable=True),
            sa.Column("customer_name", sa.String(255), nullable=True),
            sa.Column("subject", sa.String(255), nullable=False, server_default=""),
            sa.Column("description", sa.Text, nullable=True, server_default=""),
            sa.Column("total_amount", sa.Numeric(14, 2), server_default="0"),
            sa.Column("currency", sa.String(10), server_default="EUR"),
            sa.Column("status", sa.String(30), server_default="offen"),
            sa.Column("contact_person", sa.String(255), nullable=True),
            sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_pauschale", sa.Boolean, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("version", sa.Integer, server_default="1"),
            sa.UniqueConstraint("tenant_id", "offer_number", name="uq_sales_offers_tenant_number"),
            schema="domain_crm",
        )
        op.create_index("ix_crm_sales_offers_tenant", "sales_offers", ["tenant_id"], schema="domain_crm")
        op.create_index("ix_crm_sales_offers_status", "sales_offers", ["status"], schema="domain_crm")
        op.create_index("ix_crm_sales_offers_customer", "sales_offers", ["customer_id"], schema="domain_crm")
        op.create_index("ix_crm_sales_offers_deleted", "sales_offers", ["deleted_at"], schema="domain_crm")

    # ── domain_crm.sales_offer_items ──────────────────────────────────────
    if not _table_exists(inspector, "sales_offer_items"):
        op.create_table(
            "sales_offer_items",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("tenant_id", sa.String, nullable=False),
            sa.Column(
                "offer_id",
                sa.String,
                sa.ForeignKey("domain_crm.sales_offers.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("line_number", sa.Integer, nullable=False),
            sa.Column("article_number", sa.String(80), nullable=False),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("quantity", sa.Numeric(14, 4), nullable=False, server_default="0"),
            sa.Column("unit", sa.String(20), nullable=True, server_default="kg"),
            sa.Column("unit_price", sa.Numeric(14, 4), nullable=False, server_default="0"),
            sa.Column("ek_price", sa.Numeric(14, 4), nullable=True),
            sa.Column("discount_percent", sa.Numeric(5, 2), server_default="0"),
            sa.Column("line_total", sa.Numeric(14, 2), server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_crm",
        )
        op.create_index("ix_crm_offer_items_offer_id", "sales_offer_items", ["offer_id"], schema="domain_crm")

    # ── domain_crm.sales_orders ───────────────────────────────────────────
    if not _table_exists(inspector, "sales_orders"):
        op.create_table(
            "sales_orders",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("tenant_id", sa.String, nullable=False),
            sa.Column("sales_offer_id", sa.String, nullable=True),
            sa.Column("customer_id", sa.String, nullable=True),
            sa.Column("customer_name", sa.String(255), nullable=True),
            sa.Column("order_number", sa.String(64), nullable=False),
            sa.Column("subject", sa.String(255), nullable=False, server_default=""),
            sa.Column("description", sa.Text, nullable=True, server_default=""),
            sa.Column("total_amount", sa.Numeric(14, 2), server_default="0"),
            sa.Column("currency", sa.String(10), server_default="EUR"),
            sa.Column("status", sa.String(30), server_default="open"),
            sa.Column("contact_person", sa.String(255), nullable=True),
            sa.Column("delivery_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("delivery_address", sa.Text, nullable=True),
            sa.Column("shipping_method", sa.String(100), nullable=True),
            sa.Column("payment_terms", sa.String(100), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_pauschale", sa.Boolean, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("version", sa.Integer, server_default="1"),
            sa.UniqueConstraint("tenant_id", "order_number", name="uq_sales_orders_tenant_number"),
            schema="domain_crm",
        )
        op.create_index("ix_crm_sales_orders_tenant", "sales_orders", ["tenant_id"], schema="domain_crm")
        op.create_index("ix_crm_sales_orders_status", "sales_orders", ["status"], schema="domain_crm")
        op.create_index("ix_crm_sales_orders_customer", "sales_orders", ["customer_id"], schema="domain_crm")
        op.create_index("ix_crm_sales_orders_deleted", "sales_orders", ["deleted_at"], schema="domain_crm")
        op.create_index("ix_crm_sales_orders_offer", "sales_orders", ["sales_offer_id"], schema="domain_crm")

    # ── domain_crm.sales_order_items ──────────────────────────────────────
    if not _table_exists(inspector, "sales_order_items"):
        op.create_table(
            "sales_order_items",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("tenant_id", sa.String, nullable=False),
            sa.Column(
                "order_id",
                sa.String,
                sa.ForeignKey("domain_crm.sales_orders.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("line_number", sa.Integer, nullable=False),
            sa.Column("article_number", sa.String(80), nullable=False),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("quantity", sa.Numeric(14, 4), nullable=False, server_default="0"),
            sa.Column("unit", sa.String(20), nullable=True, server_default="kg"),
            sa.Column("unit_price", sa.Numeric(14, 4), nullable=False, server_default="0"),
            sa.Column("ek_price", sa.Numeric(14, 4), nullable=True),
            sa.Column("discount_percent", sa.Numeric(5, 2), server_default="0"),
            sa.Column("line_total", sa.Numeric(14, 2), server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_crm",
        )
        op.create_index("ix_crm_order_items_order_id", "sales_order_items", ["order_id"], schema="domain_crm")


def downgrade() -> None:
    op.drop_table("sales_order_items", schema="domain_crm")
    op.drop_table("sales_orders", schema="domain_crm")
    op.drop_table("sales_offer_items", schema="domain_crm")
    op.drop_table("sales_offers", schema="domain_crm")
