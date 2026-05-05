"""Add number_ranges table for configurable Debitor/Kreditor account numbering.

Revision ID: nr_20260417_001
Revises: None (standalone)
Create Date: 2026-04-17
"""

from alembic import op
import sqlalchemy as sa

revision = "nr_20260417_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.create_table(
        "number_ranges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String, sa.ForeignKey("domain_shared.tenants.id"), nullable=False),
        sa.Column("range_type", sa.String(60), nullable=False, index=True),
        sa.Column("prefix", sa.String(20), nullable=False, server_default=""),
        sa.Column("start_number", sa.Integer, nullable=False, server_default="10000"),
        sa.Column("current_value", sa.Integer, nullable=False, server_default="10000"),
        sa.Column("digit_count", sa.Integer, nullable=False, server_default="5"),
        sa.Column("reserved_prefix_digits", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "range_type", name="uq_number_range_tenant_type"),
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_table("number_ranges", schema="domain_shared")
