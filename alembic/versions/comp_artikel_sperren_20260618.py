"""COMP-SPERR-001: Artikel-Sperr-Engine (artikel_sperren)

Revision ID: comp_artikel_sperren_20260618
Revises: log_carrier_invoices_20260618
Create Date: 2026-06-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "comp_artikel_sperren_20260618"
down_revision = "log_carrier_invoices_20260618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artikel_sperren",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("artikel_id", sa.String(36), nullable=False),
        sa.Column("sperrgrund", sa.String(50), nullable=False,
                  comment="NACHBAUPFLICHT|FUTTERMITTELRECHT|ZULASSUNG_ABGELAUFEN|MYKOTOXIN|QUALITAET|MANUELL"),
        sa.Column("gesperrt_bis", sa.Date, nullable=True, comment="NULL = unbegrenzt"),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("gesperrt_am", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("status", sa.String(20), nullable=False, server_default="AKTIV",
                  comment="AKTIV|AUFGEHOBEN"),
        sa.UniqueConstraint("tenant_id", "artikel_id", name="uq_artikel_sperren_tenant_artikel"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_artikel_sperren_tenant_status",
        "artikel_sperren",
        ["tenant_id", "status"],
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_artikel_sperren_tenant_status", table_name="artikel_sperren", schema="domain_shared")
    op.drop_table("artikel_sperren", schema="domain_shared")
