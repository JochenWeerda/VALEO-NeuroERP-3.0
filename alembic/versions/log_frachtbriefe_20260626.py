"""LOG-FRACHTBRIEF-001: Frachtbrief-Tabelle fuer /api/v1/logistik/frachtbriefe.

Revision ID: log_frachtbriefe_20260626
Revises: external_mock_sessions_20260623
Create Date: 2026-06-26
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "log_frachtbriefe_20260626"
down_revision = "external_mock_sessions_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_logistics")
    op.create_table(
        "frachtbriefe",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("nummer", sa.String(60), nullable=False),
        sa.Column("kennzeichen", sa.String(20), nullable=True),
        sa.Column("artikel", sa.String(120), nullable=True),
        sa.Column("menge", sa.Numeric(12, 3), nullable=True),
        sa.Column("absender", sa.String(120), nullable=True),
        sa.Column("empfaenger", sa.String(120), nullable=True),
        sa.Column("datum", sa.Date, nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="erstellt",
        ),
        sa.Column("tour_id", sa.String(36), nullable=True),
        sa.Column("lieferschein_ref", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('erstellt','unterwegs','zugestellt','storniert')",
            name="chk_frachtbriefe_status",
        ),
        sa.UniqueConstraint("tenant_id", "nummer", name="uq_frachtbriefe_tenant_nummer"),
        schema="domain_logistics",
    )
    op.create_index(
        "ix_frachtbriefe_tenant_datum",
        "frachtbriefe",
        ["tenant_id", "datum"],
        schema="domain_logistics",
    )


def downgrade() -> None:
    op.drop_index("ix_frachtbriefe_tenant_datum", table_name="frachtbriefe", schema="domain_logistics")
    op.drop_table("frachtbriefe", schema="domain_logistics")
