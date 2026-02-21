"""add drying rule sets (lookup/factor/normalization) and audit snapshot on agrar_settlements

Revision ID: agrar_drying_rules_20260217
Revises: add_delivery_note_position_fields_20260217
Create Date: 2026-02-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "agrar_drying_rules_20260217"
down_revision = "add_delivery_note_position_fields_20260217"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Config tables ───────────────────────────────────────────────
    op.create_table(
        "drying_rule_sets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("crop_code", sa.String(length=40), nullable=False),
        sa.Column("site_id", sa.String(length=64), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("method", sa.String(length=40), nullable=False),
        sa.Column("base_moisture_pct", sa.DECIMAL(5, 2), nullable=False),
        sa.Column("rounding_mode", sa.String(length=20), nullable=False, server_default="ROUND_NEAREST"),
        sa.Column("clamp_mode", sa.String(length=20), nullable=False, server_default="HARD_ERROR"),
        sa.Column("min_moisture_pct", sa.DECIMAL(5, 2), nullable=False, server_default="0"),
        sa.Column("max_moisture_pct", sa.DECIMAL(5, 2), nullable=False, server_default="60"),
        sa.Column("start_threshold_moisture_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("fee_basis", sa.String(length=20), nullable=False, server_default="INVOICE_WEIGHT"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_drying_rule_sets_crop_site_valid",
        "drying_rule_sets",
        ["tenant_id", "crop_code", "site_id", "valid_from", "valid_to", "version"],
        unique=False,
        schema="domain_inventory",
    )

    op.create_table(
        "drying_rule_lookup_rows",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("rule_set_id", sa.String(), nullable=False),
        sa.Column("moisture_pct", sa.DECIMAL(5, 1), nullable=False),
        sa.Column("entzug_pct_points", sa.DECIMAL(5, 1), nullable=False),
        sa.Column("loss_pct", sa.DECIMAL(8, 4), nullable=False),
        sa.Column("fee_value", sa.DECIMAL(12, 4), nullable=True),
        sa.Column("fee_unit", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["rule_set_id"], ["domain_inventory.drying_rule_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "uq_drying_lookup_rule_moisture",
        "drying_rule_lookup_rows",
        ["rule_set_id", "moisture_pct"],
        unique=True,
        schema="domain_inventory",
    )

    op.create_table(
        "drying_rule_factor_ranges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("rule_set_id", sa.String(), nullable=False),
        sa.Column("from_moisture_incl", sa.DECIMAL(5, 1), nullable=False),
        sa.Column("to_moisture_incl", sa.DECIMAL(5, 1), nullable=False),
        sa.Column("factor", sa.DECIMAL(8, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["rule_set_id"], ["domain_inventory.drying_rule_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_drying_factor_rule_from_to",
        "drying_rule_factor_ranges",
        ["rule_set_id", "from_moisture_incl", "to_moisture_incl"],
        unique=False,
        schema="domain_inventory",
    )

    # ── Audit snapshot on settlements ───────────────────────────────
    op.add_column(
        "agrar_settlements",
        sa.Column(
            "drying_result",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_column("agrar_settlements", "drying_result", schema="domain_inventory")
    op.drop_index("ix_drying_factor_rule_from_to", table_name="drying_rule_factor_ranges", schema="domain_inventory")
    op.drop_table("drying_rule_factor_ranges", schema="domain_inventory")
    op.drop_index("uq_drying_lookup_rule_moisture", table_name="drying_rule_lookup_rows", schema="domain_inventory")
    op.drop_table("drying_rule_lookup_rows", schema="domain_inventory")
    op.drop_index("ix_drying_rule_sets_crop_site_valid", table_name="drying_rule_sets", schema="domain_inventory")
    op.drop_table("drying_rule_sets", schema="domain_inventory")



