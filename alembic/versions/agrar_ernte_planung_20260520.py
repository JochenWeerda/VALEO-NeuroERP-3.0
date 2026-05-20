"""agrar_ernte_planung — domain_agrar.ernte_planung table for harvest overview

Revision ID: agrar_ernte_planung_20260520
Revises: ops_wave107_remaining_stubs_20260520
Create Date: 2026-05-20
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "agrar_ernte_planung_20260520"
down_revision = "ops_wave107_remaining_stubs_20260520"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.create_table(
        "ernte_planung",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("schlag", sa.String(255), nullable=False),
        sa.Column("kultur", sa.String(120), nullable=False),
        sa.Column("datum", sa.Date, nullable=False),
        sa.Column("menge", sa.Float, nullable=False, server_default="0"),
        sa.Column("ertrag", sa.Float, nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), server_default="geplant"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_agrar",
    )
    op.create_index("ix_ernte_planung_tenant", "ernte_planung", ["tenant_id"], schema="domain_agrar")
    op.create_index("ix_ernte_planung_datum", "ernte_planung", ["datum"], schema="domain_agrar")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_agrar.ernte_planung")
