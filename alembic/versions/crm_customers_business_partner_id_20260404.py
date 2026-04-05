"""domain_crm.customers.business_partner_id — Verknüpfung CRM-Kunde ↔ Business Partner (Stammdaten)

Revision ID: crm_customers_business_partner_id_20260404
Revises: bp_merge_tab23_json_20260330
Create Date: 2026-04-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "crm_customers_business_partner_id_20260404"
down_revision: Union[str, None] = "bp_merge_tab23_json_20260330"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("business_partner_id", sa.String(length=36), nullable=True),
        schema="domain_crm",
    )
    op.create_foreign_key(
        "fk_customers_business_partner_id",
        "customers",
        "business_partners",
        ["business_partner_id"],
        ["partner_id"],
        source_schema="domain_crm",
        referent_schema="domain_crm",
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_domain_crm_customers_business_partner_id",
        "customers",
        ["business_partner_id"],
        unique=False,
        schema="domain_crm",
    )


def downgrade() -> None:
    op.drop_index("ix_domain_crm_customers_business_partner_id", table_name="customers", schema="domain_crm")
    op.drop_constraint("fk_customers_business_partner_id", "customers", schema="domain_crm", type_="foreignkey")
    op.drop_column("customers", "business_partner_id", schema="domain_crm")
