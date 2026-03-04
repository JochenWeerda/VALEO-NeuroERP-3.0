"""add_commodity_position_tables_20260304

Revision ID: pos_commodity_20260304
Revises: 05c409bd64c6
Create Date: 2026-03-04

Adds Commodity Position Management tables in schema domain_ops:
pos_position_rule, pos_position_override, pos_position_snapshot.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "pos_commodity_20260304"
down_revision: Union[str, None] = "05c409bd64c6"
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
    if _table_exists(conn, "domain_ops", "pos_position_rule"):
        return

    op.create_table(
        "pos_position_rule",
        sa.Column("rule_id", sa.String(), nullable=False),
        sa.Column("scope_type", sa.String(length=20), nullable=False),
        sa.Column("scope_id", sa.String(length=64), nullable=False),
        sa.Column("neg_tolerance_qty", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("max_short_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("yellow_threshold", sa.DECIMAL(14, 3), nullable=True),
        sa.Column("red_threshold", sa.DECIMAL(14, 3), nullable=True),
        sa.Column("approval_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("approval_role", sa.String(length=30), nullable=True),
        sa.Column("active_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("rule_id", name="pk_pos_position_rule"),
        schema="domain_ops",
    )
    op.create_index("ix_pos_position_rule_scope", "pos_position_rule", ["scope_type", "scope_id"], unique=False, schema="domain_ops")
    op.create_index("ix_pos_position_rule_tenant", "pos_position_rule", ["tenant_id"], unique=False, schema="domain_ops")

    op.create_table(
        "pos_position_override",
        sa.Column("override_id", sa.String(), nullable=False),
        sa.Column("branch_id", sa.String(length=64), nullable=True),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("period_key", sa.String(length=20), nullable=False),
        sa.Column("requested_by", sa.String(length=100), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="REQUESTED"),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("related_doc_type", sa.String(length=50), nullable=True),
        sa.Column("related_doc_id", sa.String(length=64), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("override_id", name="pk_pos_position_override"),
        schema="domain_ops",
    )
    op.create_index("ix_pos_position_override_branch_article_period", "pos_position_override", ["branch_id", "article_id", "period_key"], unique=False, schema="domain_ops")
    op.create_index("ix_pos_position_override_status", "pos_position_override", ["status"], unique=False, schema="domain_ops")
    op.create_index("ix_pos_position_override_tenant", "pos_position_override", ["tenant_id"], unique=False, schema="domain_ops")

    op.create_table(
        "pos_position_snapshot",
        sa.Column("snapshot_id", sa.String(), nullable=False),
        sa.Column("branch_id", sa.String(length=64), nullable=True),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("period_mode", sa.String(length=5), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("period_key", sa.String(length=20), nullable=False),
        sa.Column("qty_buy_open", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("qty_sell_open", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("qty_net", sa.DECIMAL(14, 3), nullable=False, server_default="0"),
        sa.Column("qty_tolerance", sa.DECIMAL(14, 3), nullable=True),
        sa.Column("severity", sa.String(length=10), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("snapshot_id", name="pk_pos_position_snapshot"),
        schema="domain_ops",
    )
    op.create_index("ix_pos_position_snapshot_branch_article_period", "pos_position_snapshot", ["branch_id", "article_id", "period_key"], unique=False, schema="domain_ops")
    op.create_index("ix_pos_position_snapshot_as_of_date", "pos_position_snapshot", ["as_of_date"], unique=False, schema="domain_ops")
    op.create_index("ix_pos_position_snapshot_tenant", "pos_position_snapshot", ["tenant_id"], unique=False, schema="domain_ops")


def downgrade() -> None:
    op.drop_table("pos_position_snapshot", schema="domain_ops")
    op.drop_table("pos_position_override", schema="domain_ops")
    op.drop_table("pos_position_rule", schema="domain_ops")
