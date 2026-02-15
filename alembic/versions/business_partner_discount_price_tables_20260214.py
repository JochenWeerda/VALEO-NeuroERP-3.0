"""Add normalized discount and price agreement tables for business partners.

Revision ID: business_partner_discount_price_tables_20260214
Revises: business_partners_customer_master_fields_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "business_partner_discount_price_tables_20260214"
down_revision = "business_partners_customer_master_fields_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_partner_discount_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("article_number", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("discount_percent", sa.Numeric(7, 2), nullable=False, server_default="0"),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("discount_list_number", sa.String(length=64), nullable=True),
        sa.Column("source_type", sa.String(length=20), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_discount_items_partner_id",
        "business_partner_discount_items",
        ["partner_id"],
        unique=False,
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_discount_items_article_number",
        "business_partner_discount_items",
        ["article_number"],
        unique=False,
        schema="domain_crm",
    )

    op.create_table(
        "business_partner_price_agreements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("article_number", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("price_net", sa.Numeric(14, 4), nullable=True),
        sa.Column("price_incl_freight", sa.Numeric(14, 4), nullable=True),
        sa.Column("price_unit", sa.String(length=20), nullable=True),
        sa.Column("discount_allowed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("special_freight", sa.Numeric(14, 4), nullable=True),
        sa.Column("payment_condition", sa.String(length=120), nullable=True),
        sa.Column("source_type", sa.String(length=20), nullable=True),
        sa.Column("operator_name", sa.String(length=120), nullable=True),
        sa.Column("operator_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_price_agreements_partner_id",
        "business_partner_price_agreements",
        ["partner_id"],
        unique=False,
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_price_agreements_article_number",
        "business_partner_price_agreements",
        ["article_number"],
        unique=False,
        schema="domain_crm",
    )


def downgrade() -> None:
    op.drop_index("ix_bp_price_agreements_article_number", table_name="business_partner_price_agreements", schema="domain_crm")
    op.drop_index("ix_bp_price_agreements_partner_id", table_name="business_partner_price_agreements", schema="domain_crm")
    op.drop_table("business_partner_price_agreements", schema="domain_crm")

    op.drop_index("ix_bp_discount_items_article_number", table_name="business_partner_discount_items", schema="domain_crm")
    op.drop_index("ix_bp_discount_items_partner_id", table_name="business_partner_discount_items", schema="domain_crm")
    op.drop_table("business_partner_discount_items", schema="domain_crm")
