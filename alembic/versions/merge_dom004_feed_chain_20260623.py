"""Merge parallel 2026-06-23 branches (DOM-*-004 wave + FEED-CHAIN-004).

Revision ID: merge_dom004_feed_chain_20260623
Revises: feed_chain_article_map_20260623, sales_ab_preisabweichung_20260623
Create Date: 2026-06-23

Parallele Agenten erzeugten zwei Heads nach ``inv_lot_trace_20260623``:
- ``agrar_partie_settlement`` → compliance → finance → sales
- ``feed_chain_article_map`` (FEED-CHAIN-004)

Ohne Merge scheitert ``alembic upgrade head`` (Singular) und init_db/Container-Bootstrap.
"""

from __future__ import annotations

revision = "merge_dom004_feed_chain_20260623"
down_revision = ("feed_chain_article_map_20260623", "sales_ab_preisabweichung_20260623")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
