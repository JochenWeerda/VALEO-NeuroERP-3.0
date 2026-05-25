"""Agribusiness farmers table

Revision ID: agribusiness_farmers_table_20260525
Revises: warehouse_wms_structure_20260517
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa

revision = "agribusiness_farmers_table_20260525"
down_revision = ("warehouse_wms_structure_20260517", "c137c1d3ba3a")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farmers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("farmer_number", sa.String(64), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(512), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(64), nullable=True),
        sa.Column("farmer_type", sa.String(64), nullable=True, server_default="standard"),
        sa.Column("status", sa.String(32), nullable=True, server_default="active"),
        sa.Column("portal_access_enabled", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_domain_shared_farmers_tenant_id",
        "farmers",
        ["tenant_id"],
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_domain_shared_farmers_tenant_id", table_name="farmers", schema="domain_shared")
    op.drop_table("farmers", schema="domain_shared")
