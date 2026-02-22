"""Close 8.11 business partner field gaps with normalized CRM tables.

Revision ID: business_partner_gap_811_normalized_20260214
Revises: einkauf_lieferschein_frachtauftrag_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "business_partner_gap_811_normalized_20260214"
down_revision = "einkauf_lieferschein_frachtauftrag_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_partner_pricing_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("direct_account", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("discount_settlement", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("self_pickup_discount_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("price_determination_mode", sa.String(length=80), nullable=True),
        sa.Column("direct_deduction", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("weekly_price_ec_basis", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("self_pickup_discount_percent IS NULL OR (self_pickup_discount_percent >= 0 AND self_pickup_discount_percent <= 100)", name="ck_bp_pr_self_pickup_discount_range"),
        sa.CheckConstraint("valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from", name="ck_bp_pr_valid_range"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_pr_partner_id", "business_partner_pricing_rules", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_interest_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("interest_table_debit_code", sa.String(length=80), nullable=True),
        sa.Column("interest_table_credit_code", sa.String(length=80), nullable=True),
        sa.Column("last_interest_date", sa.Date(), nullable=True),
        sa.Column("last_interest_balance", sa.Numeric(14, 2), nullable=True),
        sa.Column("auto_offset_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("currency_code", sa.String(length=3), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from", name="ck_bp_is_valid_range"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_is_partner_id", "business_partner_interest_settings", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_dispatch_media",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("dispatch_channel", sa.String(length=20), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("zugferd_profile", sa.String(length=40), nullable=True),
        sa.Column("recipient_email", sa.String(length=255), nullable=True),
        sa.Column("recipient_name", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("partner_id", "document_type", "dispatch_channel", name="uq_bp_dm_partner_doc_channel"),
        sa.CheckConstraint("dispatch_channel IN ('post','email','portal','edi','fax')", name="ck_bp_dm_channel"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_dm_partner_id", "business_partner_dispatch_media", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_cooperative_memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("membership_number", sa.String(length=80), nullable=True),
        sa.Column("account_number", sa.String(length=80), nullable=True),
        sa.Column("membership_status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("termination_date", sa.Date(), nullable=True),
        sa.Column("exit_date", sa.Date(), nullable=True),
        sa.Column("termination_reason", sa.String(length=255), nullable=True),
        sa.Column("mandatory_shares", sa.Integer(), nullable=True),
        sa.Column("terminated_mandatory_shares", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("membership_status IN ('active','terminated','exited')", name="ck_bp_cm_status"),
        sa.CheckConstraint("mandatory_shares IS NULL OR mandatory_shares >= 0", name="ck_bp_cm_mandatory_nonnegative"),
        sa.CheckConstraint("terminated_mandatory_shares IS NULL OR terminated_mandatory_shares >= 0", name="ck_bp_cm_terminated_nonnegative"),
        sa.CheckConstraint("terminated_mandatory_shares IS NULL OR mandatory_shares IS NULL OR terminated_mandatory_shares <= mandatory_shares", name="ck_bp_cm_terminated_le_mandatory"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_cm_partner_id", "business_partner_cooperative_memberships", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_email_distributions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("distribution_name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("partner_id", "distribution_name", "email", name="uq_bp_ed_partner_list_email"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_ed_partner_id", "business_partner_email_distributions", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_communities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("community_number", sa.String(length=80), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("community_number", name="uq_bp_comm_number"),
        schema="domain_crm",
    )

    op.create_table(
        "business_partner_community_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("community_id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("share_percent", sa.Numeric(7, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["community_id"], ["domain_crm.business_partner_communities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("community_id", "partner_id", name="uq_bp_comm_member"),
        sa.CheckConstraint("share_percent IS NULL OR (share_percent >= 0 AND share_percent <= 100)", name="ck_bp_comm_share_range"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_comm_member_community", "business_partner_community_members", ["community_id"], unique=False, schema="domain_crm")
    op.create_index("ix_bp_comm_member_partner", "business_partner_community_members", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("company_founded", sa.Date(), nullable=True),
        sa.Column("annual_revenue", sa.Numeric(14, 2), nullable=True),
        sa.Column("industry_key", sa.String(length=80), nullable=True),
        sa.Column("industry_name", sa.String(length=120), nullable=True),
        sa.Column("professional_association", sa.String(length=120), nullable=True),
        sa.Column("professional_association_number", sa.String(length=80), nullable=True),
        sa.Column("competitors", sa.Text(), nullable=True),
        sa.Column("bottlenecks", sa.Text(), nullable=True),
        sa.Column("organization_structure", sa.Text(), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("competitive_differentiation", sa.Text(), nullable=True),
        sa.Column("works_council", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("company_philosophy", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("partner_id", name="uq_bp_profile_partner"),
        sa.CheckConstraint("employee_count IS NULL OR employee_count >= 0", name="ck_bp_profile_employee_nonnegative"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_profile_partner_id", "business_partner_profiles", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_interface_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("tank_card_ean", sa.String(length=80), nullable=True),
        sa.Column("customer_card_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("edifact_invoic", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("edifact_orders", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("edifact_desadv", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("webshop_customer_number", sa.String(length=80), nullable=True),
        sa.Column("webshop_description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("partner_id", name="uq_bp_interface_partner"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_interface_partner_id", "business_partner_interface_profiles", ["partner_id"], unique=False, schema="domain_crm")


def downgrade() -> None:
    op.drop_index("ix_bp_interface_partner_id", table_name="business_partner_interface_profiles", schema="domain_crm")
    op.drop_table("business_partner_interface_profiles", schema="domain_crm")

    op.drop_index("ix_bp_profile_partner_id", table_name="business_partner_profiles", schema="domain_crm")
    op.drop_table("business_partner_profiles", schema="domain_crm")

    op.drop_index("ix_bp_comm_member_partner", table_name="business_partner_community_members", schema="domain_crm")
    op.drop_index("ix_bp_comm_member_community", table_name="business_partner_community_members", schema="domain_crm")
    op.drop_table("business_partner_community_members", schema="domain_crm")
    op.drop_table("business_partner_communities", schema="domain_crm")

    op.drop_index("ix_bp_ed_partner_id", table_name="business_partner_email_distributions", schema="domain_crm")
    op.drop_table("business_partner_email_distributions", schema="domain_crm")

    op.drop_index("ix_bp_cm_partner_id", table_name="business_partner_cooperative_memberships", schema="domain_crm")
    op.drop_table("business_partner_cooperative_memberships", schema="domain_crm")

    op.drop_index("ix_bp_dm_partner_id", table_name="business_partner_dispatch_media", schema="domain_crm")
    op.drop_table("business_partner_dispatch_media", schema="domain_crm")

    op.drop_index("ix_bp_is_partner_id", table_name="business_partner_interest_settings", schema="domain_crm")
    op.drop_table("business_partner_interest_settings", schema="domain_crm")

    op.drop_index("ix_bp_pr_partner_id", table_name="business_partner_pricing_rules", schema="domain_crm")
    op.drop_table("business_partner_pricing_rules", schema="domain_crm")
