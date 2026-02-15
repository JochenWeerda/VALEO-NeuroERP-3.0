"""Add business partner contacts and instructions tables.

Revision ID: business_partner_contacts_instructions_20260214
Revises: business_partner_item_constraints_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "business_partner_contacts_instructions_20260214"
down_revision = "business_partner_item_constraints_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_partner_instructions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("instruction_text", sa.Text(), nullable=False),
        sa.Column("instruction_priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("instruction_priority IN ('low','normal','high','critical')", name="ck_bp_instr_priority"),
        sa.CheckConstraint("valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from", name="ck_bp_instr_valid_range"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_instructions_partner_id", "business_partner_instructions", ["partner_id"], unique=False, schema="domain_crm")

    op.create_table(
        "business_partner_contacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("partner_id", sa.String(length=36), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("salutation", sa.String(length=40), nullable=True),
        sa.Column("brief_salutation", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=60), nullable=True),
        sa.Column("first_name", sa.String(length=120), nullable=True),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("position", sa.String(length=120), nullable=True),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("phone_1", sa.String(length=60), nullable=True),
        sa.Column("phone_2", sa.String(length=60), nullable=True),
        sa.Column("mobile", sa.String(length=60), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("street", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("hobbies", sa.Text(), nullable=True),
        sa.Column("info_1", sa.String(length=255), nullable=True),
        sa.Column("info_2", sa.String(length=255), nullable=True),
        sa.Column("invoice_email_recipient", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reminder_email_recipient", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("contact_type", sa.String(length=20), nullable=False, server_default="other"),
        sa.Column("cad_system", sa.String(length=120), nullable=True),
        sa.Column("software_systems", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_data_protection_officer", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["partner_id"], ["domain_crm.business_partners.partner_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("priority >= 0", name="ck_bp_contacts_priority_nonnegative"),
        sa.CheckConstraint("contact_type IN ('main','billing','logistics','sales','other')", name="ck_bp_contacts_contact_type"),
        schema="domain_crm",
    )
    op.create_index("ix_bp_contacts_partner_id", "business_partner_contacts", ["partner_id"], unique=False, schema="domain_crm")
    op.create_index("ix_bp_contacts_email", "business_partner_contacts", ["email"], unique=False, schema="domain_crm")


def downgrade() -> None:
    op.drop_index("ix_bp_contacts_email", table_name="business_partner_contacts", schema="domain_crm")
    op.drop_index("ix_bp_contacts_partner_id", table_name="business_partner_contacts", schema="domain_crm")
    op.drop_table("business_partner_contacts", schema="domain_crm")

    op.drop_index("ix_bp_instructions_partner_id", table_name="business_partner_instructions", schema="domain_crm")
    op.drop_table("business_partner_instructions", schema="domain_crm")
