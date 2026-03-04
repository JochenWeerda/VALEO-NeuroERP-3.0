"""add_kontrakte_module_tables_20260303

Revision ID: c1d2e3f4a5b6
Revises: b0c1d2e3f4a5
Create Date: 2026-03-03

Adds valeo kontrakte module tables in schema domain_ops.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, schema: str, table: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = :schema AND table_name = :table"
        ),
        {"schema": schema, "table": table},
    )
    return r.scalar() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "domain_ops", "kon_contract"):
        return  # Tabellen existieren bereits (z. B. manuell angelegt)
    op.create_table(
        "kon_contract",
        sa.Column("contract_id", sa.String(), nullable=False),
        sa.Column("contract_no", sa.String(length=50), nullable=False),
        sa.Column("contract_type", sa.String(length=20), nullable=False),
        sa.Column("branch_id", sa.String(length=64), nullable=True),
        sa.Column("clerk_id", sa.String(length=64), nullable=True),
        sa.Column("party_id", sa.String(length=64), nullable=False),
        sa.Column("debitor_kto", sa.String(length=64), nullable=True),
        sa.Column("kreditor_kto", sa.String(length=64), nullable=True),
        sa.Column("contract_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quantity_type", sa.String(length=20), nullable=False),
        sa.Column("total_quantity", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=20), nullable=False, server_default="kg"),
        sa.Column("allow_overdelivery", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OFFEN"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("payment_terms", sa.Text(), nullable=True),
        sa.Column("conditions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("pricing_model", sa.String(length=30), nullable=True),
        sa.Column("min_price", sa.DECIMAL(14, 4), nullable=True),
        sa.Column("premium_type", sa.String(length=30), nullable=True),
        sa.Column("premium_value", sa.DECIMAL(14, 4), nullable=True),
        sa.Column("basis_reference", sa.String(length=120), nullable=True),
        sa.Column("pricing_window_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pricing_window_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("contract_id", name="pk_kon_contract"),
        schema="domain_ops",
    )
    op.create_index("ix_kon_contract_contract_no", "kon_contract", ["contract_no"], unique=True, schema="domain_ops")
    op.create_index("ix_kon_contract_party_id", "kon_contract", ["party_id"], unique=False, schema="domain_ops")
    op.create_index("ix_kon_contract_status", "kon_contract", ["status"], unique=False, schema="domain_ops")
    op.create_index("ix_kon_contract_validity", "kon_contract", ["valid_from", "valid_to"], unique=False, schema="domain_ops")

    op.create_table(
        "kon_contract_line",
        sa.Column("line_id", sa.String(), nullable=False),
        sa.Column("contract_id", sa.String(), nullable=False),
        sa.Column("position_no", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("description1", sa.String(length=255), nullable=True),
        sa.Column("description2", sa.String(length=255), nullable=True),
        sa.Column("qty_contract", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("price_unit", sa.String(length=20), nullable=True),
        sa.Column("unit_price", sa.DECIMAL(14, 4), nullable=True),
        sa.Column("discount_pct", sa.DECIMAL(8, 4), nullable=True),
        sa.Column("surcharge", sa.DECIMAL(14, 4), nullable=True),
        sa.Column("rebate_type", sa.String(length=30), nullable=True),
        sa.Column("is_bio", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_matif", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["domain_ops.kon_contract.contract_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("line_id", name="pk_kon_contract_line"),
        sa.UniqueConstraint("contract_id", "position_no", name="uq_kon_contract_line_contract_pos"),
        schema="domain_ops",
    )
    op.create_index("ix_kon_contract_line_article_id", "kon_contract_line", ["article_id"], unique=False, schema="domain_ops")
    op.create_index("ix_kon_contract_line_contract_id", "kon_contract_line", ["contract_id"], unique=False, schema="domain_ops")

    op.create_table(
        "kon_contract_movement",
        sa.Column("movement_id", sa.String(), nullable=False),
        sa.Column("contract_id", sa.String(), nullable=False),
        sa.Column("line_id", sa.String(), nullable=True),
        sa.Column("order_no", sa.String(length=64), nullable=True),
        sa.Column("delivery_note_no", sa.String(length=64), nullable=True),
        sa.Column("invoice_no", sa.String(length=64), nullable=True),
        sa.Column("movement_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("quantity", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.DECIMAL(14, 4), nullable=True),
        sa.Column("route_no", sa.String(length=64), nullable=True),
        sa.Column("is_invoiced", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["domain_ops.kon_contract.contract_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["line_id"], ["domain_ops.kon_contract_line.line_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("movement_id", name="pk_kon_contract_movement"),
        schema="domain_ops",
    )
    op.create_index("ix_kon_contract_movement_contract_date", "kon_contract_movement", ["contract_id", "movement_date"], unique=False, schema="domain_ops")
    op.create_index("ix_kon_contract_movement_line_id", "kon_contract_movement", ["line_id"], unique=False, schema="domain_ops")

    op.create_table(
        "kon_audit_log",
        sa.Column("audit_id", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("field_name", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("changed_by", sa.String(length=100), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("audit_id", name="pk_kon_audit_log"),
        schema="domain_ops",
    )
    op.create_index("ix_kon_audit_log_entity_id", "kon_audit_log", ["entity_id"], unique=False, schema="domain_ops")
    op.create_index("ix_kon_audit_log_changed_at", "kon_audit_log", ["changed_at"], unique=False, schema="domain_ops")

    op.create_table(
        "kon_number_range",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("contract_type", sa.String(length=20), nullable=False),
        sa.Column("branch_id", sa.String(length=64), nullable=True),
        sa.Column("prefix", sa.String(length=20), nullable=False),
        sa.Column("next_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("padding", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_kon_number_range"),
        sa.UniqueConstraint("tenant_id", "contract_type", "branch_id", name="uq_kon_number_range_scope"),
        schema="domain_ops",
    )
    op.create_index("ix_kon_number_range_contract_type", "kon_number_range", ["contract_type"], unique=False, schema="domain_ops")


def downgrade() -> None:
    op.drop_table("kon_number_range", schema="domain_ops")
    op.drop_table("kon_audit_log", schema="domain_ops")
    op.drop_table("kon_contract_movement", schema="domain_ops")
    op.drop_table("kon_contract_line", schema="domain_ops")
    op.drop_table("kon_contract", schema="domain_ops")
