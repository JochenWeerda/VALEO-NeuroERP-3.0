"""Streckengeschaefte persistent (public.streckengeschaefte); merge mehrerer Alembic-Heads.

Revision ID: streckengeschaefte_table_merge_20260424
Revises: nr_20260417_001, flow_spine_lifecycle_20260417, grundfutteranalysen_20260419, rations_zugang_dsgvo_20260420
Create Date: 2026-04-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "streckengeschaefte_table_merge_20260424"
down_revision = (
    "nr_20260417_001",
    "flow_spine_lifecycle_20260417",
    "grundfutteranalysen_20260419",
    "rations_zugang_dsgvo_20260420",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'streckengeschaefte'"
        )
    )
    if r.scalar() is not None:
        return

    op.create_table(
        "streckengeschaefte",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("strecke_nr", sa.String(length=64), nullable=False),
        sa.Column("datum", sa.Date(), nullable=False),
        sa.Column("niederlassung", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("partie_nr", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("kostenstelle", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("lagerhalle", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("nls_nr", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("erledigt", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("lieferant_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("lieferant_nr", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("kontrakt_nr", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("artikel", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("netto", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("mwst", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("brutto", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("rechnungsnr", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("bediener", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("notiz", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "erstellt",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "strecke_nr", name="uq_streckengeschaefte_tenant_strecke_nr"),
    )
    op.create_index("ix_streckengeschaefte_tenant_id", "streckengeschaefte", ["tenant_id"])
    op.create_index("ix_streckengeschaefte_strecke_nr", "streckengeschaefte", ["strecke_nr"])


def downgrade() -> None:
    op.drop_index("ix_streckengeschaefte_strecke_nr", table_name="streckengeschaefte")
    op.drop_index("ix_streckengeschaefte_tenant_id", table_name="streckengeschaefte")
    op.drop_table("streckengeschaefte")
