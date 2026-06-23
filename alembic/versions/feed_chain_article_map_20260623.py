"""FEED-CHAIN-004: Einzelfuttermittel → inventory.articles Mapping-Spalte.

Revision ID: feed_chain_article_map_20260623
Revises: inv_lot_trace_20260623
"""

from __future__ import annotations

from alembic import op

revision = "feed_chain_article_map_20260623"
down_revision = "inv_lot_trace_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_shared.futtermittel_einzelfutter
            ADD COLUMN IF NOT EXISTS inventory_article_id VARCHAR(64);
        CREATE INDEX IF NOT EXISTS ix_ef_inventory_article
            ON domain_shared.futtermittel_einzelfutter (tenant_id, inventory_article_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS domain_shared.ix_ef_inventory_article;
        ALTER TABLE domain_shared.futtermittel_einzelfutter
            DROP COLUMN IF EXISTS inventory_article_id;
        """
    )
