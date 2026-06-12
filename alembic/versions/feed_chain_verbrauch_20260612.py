"""Futtermittel-Produktionsauftrag: Verbrauchs-Snapshot + Charge-Referenz.

Revision ID: feed_chain_verbrauch_20260612
Revises: log_logistics_core_20260612

FEED-CHAIN-001: ``verbrauch`` (JSONB) hält fest, was bei Freigabe tatsächlich
abgezogen wurde (Mischprotokoll-Grundlage; Storno restauriert exakt diesen
Snapshot statt des aktuellen Rezepts). ``charge_id`` verweist auf die bei
``fertig`` erzeugte Fertigwaren-Charge in ``domain_ops.ops_chargen``.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "feed_chain_verbrauch_20260612"
down_revision: Union[str, Sequence[str], None] = "log_logistics_core_20260612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_shared.futtermittel_produktionsauftraege
            ADD COLUMN IF NOT EXISTS verbrauch JSONB,
            ADD COLUMN IF NOT EXISTS charge_id VARCHAR(64);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_shared.futtermittel_produktionsauftraege
            DROP COLUMN IF EXISTS charge_id,
            DROP COLUMN IF EXISTS verbrauch;
        """
    )
