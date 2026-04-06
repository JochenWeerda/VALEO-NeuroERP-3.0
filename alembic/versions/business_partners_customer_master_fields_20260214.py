"""Add extended customer master fields to business_partners.

Revision ID: business_partners_customer_master_fields_20260214
Revises: inventory_stock_movements_l3_fields_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "business_partners_customer_master_fields_20260214"
down_revision = "inventory_stock_movements_l3_fields_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Neuinstallation: domain_crm.business_partners wurde in aelteren Migrationen nie angelegt,
    # aber nachfolgende ALTERs setzen voraus, dass die Tabelle existiert (CI: UndefinedTable).
    conn = op.get_bind()
    if conn.execute(text("SELECT to_regclass('domain_crm.business_partners')")).scalar() is None:
        op.execute(text("CREATE SCHEMA IF NOT EXISTS domain_crm"))
        op.execute(
            text(
                """
                CREATE TABLE domain_crm.business_partners (
                    partner_id VARCHAR(36) NOT NULL PRIMARY KEY,
                    tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
                    partner_number VARCHAR(64) NOT NULL,
                    name_1 VARCHAR(255) NOT NULL,
                    name_2 VARCHAR(255),
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ DEFAULT now(),
                    updated_at TIMESTAMPTZ
                )
                """
            )
        )
        op.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_domain_crm_bp_partner_number "
                "ON domain_crm.business_partners (partner_number)"
            )
        )

    op.add_column("business_partners", sa.Column("salutation", sa.String(length=40), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("first_name", sa.String(length=120), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("last_name", sa.String(length=120), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("account_holder", sa.String(length=255), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("bank_connection_active", sa.Boolean(), nullable=False, server_default=sa.text("true")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("payment_method", sa.String(length=40), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("price_group", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("discount_percent", sa.Numeric(7, 2), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("customer_group", sa.String(length=80), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("wants_account_statement", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("print_balance_on_invoice", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("invoice_print_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("delivery_note_print_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("calculate_shipping_flat", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("settlement_mode", sa.String(length=20), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("collective_settlement_code", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("bonus_recipient", sa.String(length=255), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("invoice_recipient", sa.String(length=255), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("self_billing_customer", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("customer_addition", sa.String(length=255), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("payment_target_days", sa.Integer(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("cash_discount_percent", sa.Numeric(7, 2), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("cash_discount_days", sa.Integer(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("dunning_procedure", sa.String(length=120), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("currency_code", sa.String(length=3), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("euro_conversion_rate", sa.Numeric(14, 6), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("interest_table_code", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("last_interest_date", sa.Date(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("last_interest_balance", sa.Numeric(14, 2), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("auto_offset_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")

    op.add_column("business_partners", sa.Column("loading_information", sa.Text(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("route_information", sa.Text(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("post_open_items_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("insurance_info", sa.String(length=255), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("statistics_code", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("agricultural_office", sa.String(length=120), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("operation_number", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("market_price_evaluation", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("threshold_value", sa.Numeric(14, 2), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("webshop_customer", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("fax_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")

    op.add_column("business_partners", sa.Column("industry_key", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("annual_revenue", sa.Numeric(14, 2), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("employee_count", sa.Integer(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("company_philosophy", sa.Text(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("competitive_differentiation", sa.Text(), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("invoice_dispatch_channel", sa.String(length=40), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("reminder_dispatch_channel", sa.String(length=40), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("contact_dispatch_channel", sa.String(length=40), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("zugferd_profile", sa.String(length=40), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("delivery_condition", sa.String(length=120), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("due_date_basis", sa.String(length=40), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("proforma_invoice", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("proforma_discount_1", sa.Numeric(7, 2), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("proforma_discount_2", sa.Numeric(7, 2), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("consent_valid_until", sa.Date(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("consent_note", sa.Text(), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("membership_number", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("membership_terminated", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("termination_reason", sa.String(length=255), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("membership_entry_date", sa.Date(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("termination_date", sa.Date(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("exit_date", sa.Date(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("mandatory_shares", sa.Integer(), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("terminated_mandatory_shares", sa.Integer(), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("tank_card_ean", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("customer_card_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("edifact_invoic", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("edifact_orders", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("edifact_desadv", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("webshop_customer_number", sa.String(length=80), nullable=True), schema="domain_crm")
    op.add_column("business_partners", sa.Column("webshop_description", sa.String(length=255), nullable=True), schema="domain_crm")

    op.add_column("business_partners", sa.Column("discount_items", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")), schema="domain_crm")
    op.add_column("business_partners", sa.Column("price_agreements", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")), schema="domain_crm")


def downgrade() -> None:
    columns = [
        "price_agreements",
        "discount_items",
        "webshop_description",
        "webshop_customer_number",
        "edifact_desadv",
        "edifact_orders",
        "edifact_invoic",
        "customer_card_flag",
        "tank_card_ean",
        "terminated_mandatory_shares",
        "mandatory_shares",
        "exit_date",
        "termination_date",
        "membership_entry_date",
        "termination_reason",
        "membership_terminated",
        "membership_number",
        "consent_note",
        "consent_valid_until",
        "proforma_discount_2",
        "proforma_discount_1",
        "proforma_invoice",
        "due_date_basis",
        "delivery_condition",
        "zugferd_profile",
        "contact_dispatch_channel",
        "reminder_dispatch_channel",
        "invoice_dispatch_channel",
        "competitive_differentiation",
        "company_philosophy",
        "employee_count",
        "annual_revenue",
        "industry_key",
        "fax_blocked",
        "webshop_customer",
        "threshold_value",
        "market_price_evaluation",
        "operation_number",
        "agricultural_office",
        "statistics_code",
        "insurance_info",
        "post_open_items_blocked",
        "route_information",
        "loading_information",
        "auto_offset_enabled",
        "last_interest_balance",
        "last_interest_date",
        "interest_table_code",
        "euro_conversion_rate",
        "currency_code",
        "dunning_procedure",
        "cash_discount_days",
        "cash_discount_percent",
        "payment_target_days",
        "customer_addition",
        "self_billing_customer",
        "invoice_recipient",
        "bonus_recipient",
        "collective_settlement_code",
        "settlement_mode",
        "calculate_shipping_flat",
        "delivery_note_print_blocked",
        "invoice_print_blocked",
        "print_balance_on_invoice",
        "wants_account_statement",
        "customer_group",
        "discount_percent",
        "price_group",
        "payment_method",
        "bank_connection_active",
        "account_holder",
        "last_name",
        "first_name",
        "salutation",
    ]
    for column in columns:
        op.drop_column("business_partners", column, schema="domain_crm")
