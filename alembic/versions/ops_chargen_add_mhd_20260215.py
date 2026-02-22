"""add mhd to ops_chargen

Revision ID: ops_chargen_add_mhd_20260215
Revises: admin_mobile_routing_connectors_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "ops_chargen_add_mhd_20260215"
down_revision = "admin_mobile_routing_connectors_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("ops_chargen", schema="domain_ops")}
    if "mhd" not in cols:
        op.add_column("ops_chargen", sa.Column("mhd", sa.DateTime(timezone=True), nullable=True), schema="domain_ops")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("ops_chargen", schema="domain_ops")}
    if "mhd" in cols:
        op.drop_column("ops_chargen", "mhd", schema="domain_ops")
