"""Add normalized Tab 23/24/25 structures for business partners.

Revision ID: business_partner_tab_23_24_25_20260214
Revises: business_partner_contacts_instructions_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "business_partner_tab_23_24_25_20260214"
down_revision = "business_partner_contacts_instructions_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_partner_addresses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("address_type", sa.String(length=20), nullable=False, server_default="customer"),
        sa.Column("name_1", sa.String(length=255), nullable=True),
        sa.Column("name_2", sa.String(length=255), nullable=True),
        sa.Column("name_3", sa.String(length=255), nullable=True),
        sa.Column("street", sa.String(length=120), nullable=True),
        sa.Column("house_number", sa.String(length=40), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=True, server_default="DE"),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("po_box", sa.String(length=40), nullable=True),
        sa.Column("po_box_postal_code", sa.String(length=20), nullable=True),
        sa.Column("po_box_city", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=60), nullable=True),
        sa.Column("fax", sa.String(length=60), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("salutation", sa.String(length=40), nullable=True),
        sa.Column("brief_salutation", sa.String(length=120), nullable=True),
        sa.Column("free_field_1", sa.String(length=255), nullable=True),
        sa.Column("free_field_2", sa.String(length=255), nullable=True),
        sa.Column("free_field_3", sa.String(length=255), nullable=True),
        sa.Column("area_code", sa.String(length=80), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "address_type IN ('customer','invoice','shipping','postal')",
            name="ck_bp_addr_type",
        ),
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_addr_partner_id",
        "business_partner_addresses",
        ["partner_id"],
        unique=False,
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_addr_partner_type_default",
        "business_partner_addresses",
        ["partner_id", "address_type", "is_default"],
        unique=False,
        schema="domain_crm",
    )

    op.create_table(
        "business_partner_billing_configs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("customer_group", sa.String(length=80), nullable=True),
        sa.Column("customer_type", sa.String(length=40), nullable=True),
        sa.Column("account_statement_print", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("account_statement_separate", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("account_statement_reprint", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_account_statement_number", sa.Integer(), nullable=True),
        sa.Column("last_account_statement_date", sa.Date(), nullable=True),
        sa.Column("account_balance", sa.Numeric(14, 2), nullable=True),
        sa.Column("print_ad_text", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("shipping_expenses_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("settlement_mode", sa.String(length=20), nullable=True),
        sa.Column("admin_overhead_surcharge_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("invoice_number_range", sa.String(length=80), nullable=True),
        sa.Column("bonus_eligible", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("self_billing_sales", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("self_billing_purchase", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("remarkable_claim", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("vat_optimizer", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("partner_id", name="uq_bp_billing_partner"),
        sa.CheckConstraint(
            "customer_type IS NULL OR customer_type IN ('standard','organ','group_internal')",
            name="ck_bp_billing_customer_type",
        ),
        sa.CheckConstraint(
            "settlement_mode IS NULL OR settlement_mode IN ('single','collective')",
            name="ck_bp_billing_settlement_mode",
        ),
        sa.CheckConstraint(
            "admin_overhead_surcharge_percent IS NULL OR (admin_overhead_surcharge_percent >= 0 AND admin_overhead_surcharge_percent <= 100)",
            name="ck_bp_billing_overhead_percent_range",
        ),
        sa.CheckConstraint(
            "last_account_statement_number IS NULL OR last_account_statement_number >= 0",
            name="ck_bp_billing_last_statement_nonnegative",
        ),
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_billing_partner_id",
        "business_partner_billing_configs",
        ["partner_id"],
        unique=True,
        schema="domain_crm",
    )

    op.create_table(
        "business_partner_cpd_accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("cpd_customer_number", sa.String(length=64), nullable=False),
        sa.Column("debtor_account", sa.String(length=40), nullable=True),
        sa.Column("search_term", sa.String(length=120), nullable=True),
        sa.Column("name_1", sa.String(length=255), nullable=False),
        sa.Column("name_2", sa.String(length=255), nullable=True),
        sa.Column("name_3", sa.String(length=255), nullable=True),
        sa.Column("street", sa.String(length=120), nullable=True),
        sa.Column("house_number", sa.String(length=40), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=True, server_default="DE"),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("po_box", sa.String(length=40), nullable=True),
        sa.Column("po_box_city", sa.String(length=120), nullable=True),
        sa.Column("phone_1", sa.String(length=60), nullable=True),
        sa.Column("phone_2", sa.String(length=60), nullable=True),
        sa.Column("fax", sa.String(length=60), nullable=True),
        sa.Column("salutation", sa.String(length=40), nullable=True),
        sa.Column("brief_salutation", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("branch_office", sa.String(length=120), nullable=True),
        sa.Column("cost_center", sa.String(length=120), nullable=True),
        sa.Column("invoice_type", sa.String(length=40), nullable=True),
        sa.Column("collective_invoice", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("invoice_form_template", sa.String(length=80), nullable=True),
        sa.Column("sales_representative", sa.String(length=120), nullable=True),
        sa.Column("area_code", sa.String(length=80), nullable=True),
        sa.Column("cash_discount_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("cash_discount_days", sa.Integer(), nullable=True),
        sa.Column("payment_target_days", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpd_customer_number", name="uq_bp_cpd_customer_number"),
        sa.CheckConstraint(
            "cash_discount_percent IS NULL OR (cash_discount_percent >= 0 AND cash_discount_percent <= 100)",
            name="ck_bp_cpd_cash_discount_percent_range",
        ),
        sa.CheckConstraint(
            "cash_discount_days IS NULL OR cash_discount_days >= 0",
            name="ck_bp_cpd_cash_discount_days_nonnegative",
        ),
        sa.CheckConstraint(
            "payment_target_days IS NULL OR payment_target_days >= 0",
            name="ck_bp_cpd_payment_target_days_nonnegative",
        ),
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_cpd_partner_id",
        "business_partner_cpd_accounts",
        ["partner_id"],
        unique=False,
        schema="domain_crm",
    )
    op.create_index(
        "ix_bp_cpd_customer_number",
        "business_partner_cpd_accounts",
        ["cpd_customer_number"],
        unique=True,
        schema="domain_crm",
    )


def downgrade() -> None:
    op.drop_index("ix_bp_cpd_customer_number", table_name="business_partner_cpd_accounts", schema="domain_crm")
    op.drop_index("ix_bp_cpd_partner_id", table_name="business_partner_cpd_accounts", schema="domain_crm")
    op.drop_table("business_partner_cpd_accounts", schema="domain_crm")

    op.drop_index("ix_bp_billing_partner_id", table_name="business_partner_billing_configs", schema="domain_crm")
    op.drop_table("business_partner_billing_configs", schema="domain_crm")

    op.drop_index("ix_bp_addr_partner_type_default", table_name="business_partner_addresses", schema="domain_crm")
    op.drop_index("ix_bp_addr_partner_id", table_name="business_partner_addresses", schema="domain_crm")
    op.drop_table("business_partner_addresses", schema="domain_crm")
