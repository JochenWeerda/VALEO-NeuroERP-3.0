"""add audit fields, contract/customer links, DMS ref to drying rule sets

Revision ID: agrar_drying_rules_audit_contract_dms_20260217
Revises: agrar_drying_rules_20260217
Create Date: 2026-02-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "agrar_drying_rules_audit_contract_dms_20260217"
down_revision = "agrar_drying_rules_20260217"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add audit, contract, customer, DMS fields to drying_rule_sets
    op.add_column(
        "drying_rule_sets",
        sa.Column("created_by", sa.String(length=64), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "drying_rule_sets",
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "drying_rule_sets",
        sa.Column("contract_id", sa.String(), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "drying_rule_sets",
        sa.Column("customer_id", sa.String(), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "drying_rule_sets",
        sa.Column("is_customer_specific", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema="domain_inventory",
    )
    op.add_column(
        "drying_rule_sets",
        sa.Column("justification", sa.Text(), nullable=True, comment="Begründung für kundenspezifische Sonderregelungen"),
        schema="domain_inventory",
    )
    op.add_column(
        "drying_rule_sets",
        sa.Column("document_id", sa.String(length=64), nullable=True, comment="DMS-Referenz für Tabelle/Formel-Dokument"),
        schema="domain_inventory",
    )

    # Foreign keys
    op.create_foreign_key(
        "fk_drying_rule_sets_contract",
        "drying_rule_sets",
        "agrar_contracts",
        ["contract_id"],
        ["id"],
        source_schema="domain_inventory",
        referent_schema="domain_inventory",
    )
    op.create_foreign_key(
        "fk_drying_rule_sets_customer",
        "drying_rule_sets",
        "customers",
        ["customer_id"],
        ["id"],
        source_schema="domain_inventory",
        referent_schema="domain_crm",
    )

    # Index for contract lookups
    op.create_index(
        "ix_drying_rule_sets_contract",
        "drying_rule_sets",
        ["contract_id"],
        unique=False,
        schema="domain_inventory",
    )
    # Index for customer-specific rules
    op.create_index(
        "ix_drying_rule_sets_customer",
        "drying_rule_sets",
        ["customer_id", "is_customer_specific"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_drying_rule_sets_customer", table_name="drying_rule_sets", schema="domain_inventory")
    op.drop_index("ix_drying_rule_sets_contract", table_name="drying_rule_sets", schema="domain_inventory")
    op.drop_constraint("fk_drying_rule_sets_customer", "drying_rule_sets", schema="domain_inventory", type_="foreignkey")
    op.drop_constraint("fk_drying_rule_sets_contract", "drying_rule_sets", schema="domain_inventory", type_="foreignkey")
    op.drop_column("drying_rule_sets", "document_id", schema="domain_inventory")
    op.drop_column("drying_rule_sets", "justification", schema="domain_inventory")
    op.drop_column("drying_rule_sets", "is_customer_specific", schema="domain_inventory")
    op.drop_column("drying_rule_sets", "customer_id", schema="domain_inventory")
    op.drop_column("drying_rule_sets", "contract_id", schema="domain_inventory")
    op.drop_column("drying_rule_sets", "updated_by", schema="domain_inventory")
    op.drop_column("drying_rule_sets", "created_by", schema="domain_inventory")


