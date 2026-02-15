"""Add constraints and indexes for business partner discount/price items.

Revision ID: business_partner_item_constraints_20260214
Revises: business_partner_discount_price_tables_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "business_partner_item_constraints_20260214"
down_revision = "business_partner_discount_price_tables_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_bp_di_discount_percent_range",
        "business_partner_discount_items",
        "discount_percent >= 0 AND discount_percent <= 100",
        schema="domain_crm",
    )
    op.create_check_constraint(
        "ck_bp_di_valid_range",
        "business_partner_discount_items",
        "valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from",
        schema="domain_crm",
    )
    op.create_check_constraint(
        "ck_bp_di_source_type",
        "business_partner_discount_items",
        "source_type IS NULL OR source_type IN ('import','batch','internal')",
        schema="domain_crm",
    )

    op.create_check_constraint(
        "ck_bp_pa_valid_range",
        "business_partner_price_agreements",
        "valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from",
        schema="domain_crm",
    )
    op.create_check_constraint(
        "ck_bp_pa_nonnegative",
        "business_partner_price_agreements",
        "(price_net IS NULL OR price_net >= 0) "
        "AND (price_incl_freight IS NULL OR price_incl_freight >= 0) "
        "AND (special_freight IS NULL OR special_freight >= 0)",
        schema="domain_crm",
    )
    op.create_check_constraint(
        "ck_bp_pa_source_type",
        "business_partner_price_agreements",
        "source_type IS NULL OR source_type IN ('import','batch','internal')",
        schema="domain_crm",
    )

    op.create_index(
        "ix_bp_discount_items_partner_valid_to",
        "business_partner_discount_items",
        ["partner_id", "valid_to"],
        unique=False,
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_price_agreements_partner_valid_to",
        "business_partner_price_agreements",
        ["partner_id", "valid_to"],
        unique=False,
        schema="domain_crm",
    )

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_bp_discount_items_period_key
        ON domain_crm.business_partner_discount_items (
          partner_id,
          article_number,
          COALESCE(valid_from, DATE '1900-01-01'),
          COALESCE(valid_to, DATE '9999-12-31'),
          COALESCE(source_type, '')
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_bp_price_agreements_period_key
        ON domain_crm.business_partner_price_agreements (
          partner_id,
          article_number,
          COALESCE(valid_from, DATE '1900-01-01'),
          COALESCE(valid_to, DATE '9999-12-31'),
          COALESCE(source_type, '')
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_crm.ux_bp_price_agreements_period_key")
    op.execute("DROP INDEX IF EXISTS domain_crm.ux_bp_discount_items_period_key")

    op.drop_index(
        "ix_bp_price_agreements_partner_valid_to",
        table_name="business_partner_price_agreements",
        schema="domain_crm",
    )
    op.drop_index(
        "ix_bp_discount_items_partner_valid_to",
        table_name="business_partner_discount_items",
        schema="domain_crm",
    )

    op.drop_constraint("ck_bp_pa_source_type", "business_partner_price_agreements", schema="domain_crm", type_="check")
    op.drop_constraint("ck_bp_pa_nonnegative", "business_partner_price_agreements", schema="domain_crm", type_="check")
    op.drop_constraint("ck_bp_pa_valid_range", "business_partner_price_agreements", schema="domain_crm", type_="check")
    op.drop_constraint("ck_bp_di_source_type", "business_partner_discount_items", schema="domain_crm", type_="check")
    op.drop_constraint("ck_bp_di_valid_range", "business_partner_discount_items", schema="domain_crm", type_="check")
    op.drop_constraint("ck_bp_di_discount_percent_range", "business_partner_discount_items", schema="domain_crm", type_="check")
