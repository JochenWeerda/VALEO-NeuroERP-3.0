"""Fracht-Tarif: Storno-Spalten (soft, auditierbar).

Revision ID: log_freight_tariff_storno_20260613
Revises: feed_chain_verbrauch_20260612

WAVE-PHYS-CHAIN-000 / LOG-FREIGHT-STORNO-001: Tarife bleiben in der DB,
werden aber fuer simulate/calculate ausgeschlossen (status STORNIERT).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "log_freight_tariff_storno_20260613"
down_revision: Union[str, Sequence[str], None] = "feed_chain_verbrauch_20260612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_logistics.freight_tariffs
            ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'AKTIV',
            ADD COLUMN IF NOT EXISTS storno_ts TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS storno_grund TEXT;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_logistics.freight_tariffs DROP COLUMN IF EXISTS storno_grund;
        ALTER TABLE domain_logistics.freight_tariffs DROP COLUMN IF EXISTS storno_ts;
        ALTER TABLE domain_logistics.freight_tariffs DROP COLUMN IF EXISTS status;
        """
    )
