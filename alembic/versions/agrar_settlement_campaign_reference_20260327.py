"""AgrarSettlement campaign reference

Revision ID: agrar_settlement_campaign_reference_20260327
Revises: agrar_settlement_row_version_20260324
Create Date: 2026-03-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "agrar_settlement_campaign_reference_20260327"
down_revision: Union[str, tuple[str, ...], None] = "agrar_settlement_row_version_20260324"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agrar_settlements",
        sa.Column(
            "campaign_id",
            sa.String(length=64),
            nullable=True,
            comment="Erntefenster-Kampagnenreferenz fuer eindeutige Zuordnung im Kampagnenabschluss",
        ),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_agrar_settlements_campaign",
        "agrar_settlements",
        ["campaign_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_agrar_settlements_campaign", table_name="agrar_settlements", schema="domain_inventory")
    op.drop_column("agrar_settlements", "campaign_id", schema="domain_inventory")
