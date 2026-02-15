"""admin api key management

Revision ID: admin_api_keys_20260215
Revises: inventory_charge_lineage_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "admin_api_keys_20260215"
down_revision = "inventory_charge_lineage_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_prefix", sa.String(length=24), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column(
            "ip_allowlist",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_api_keys_tenant_name"),
        sa.CheckConstraint(
            "status IN ('active','revoked','expired')",
            name="chk_api_keys_status",
        ),
        sa.CheckConstraint(
            "rate_limit_per_minute IS NULL OR rate_limit_per_minute > 0",
            name="chk_api_keys_rate_limit_positive",
        ),
        schema="domain_shared",
    )
    op.create_index(
        "ix_api_keys_tenant_status",
        "api_keys",
        ["tenant_id", "status"],
        unique=False,
        schema="domain_shared",
    )
    op.create_index(
        "ix_api_keys_prefix",
        "api_keys",
        ["key_prefix"],
        unique=False,
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_api_keys_prefix", table_name="api_keys", schema="domain_shared")
    op.drop_index("ix_api_keys_tenant_status", table_name="api_keys", schema="domain_shared")
    op.drop_table("api_keys", schema="domain_shared")

