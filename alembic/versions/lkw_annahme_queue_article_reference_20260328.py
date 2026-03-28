"""LKW-Annahme-Queue article reference

Revision ID: lkw_annahme_queue_article_reference_20260328
Revises: agrar_settlement_campaign_reference_20260327
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "lkw_annahme_queue_article_reference_20260328"
down_revision: Union[str, tuple[str, ...], None] = "agrar_settlement_campaign_reference_20260327"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "lkw_annahme_queue",
        sa.Column("article_id", sa.String(), nullable=True),
        schema="domain_inventory",
    )
    op.create_foreign_key(
        "fk_lkw_annahme_queue_article_id",
        "lkw_annahme_queue",
        "articles",
        ["article_id"],
        ["id"],
        source_schema="domain_inventory",
        referent_schema="domain_inventory",
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_lkw_annahme_queue_article_id",
        "lkw_annahme_queue",
        ["article_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_lkw_annahme_queue_article_id", table_name="lkw_annahme_queue", schema="domain_inventory")
    op.drop_constraint("fk_lkw_annahme_queue_article_id", "lkw_annahme_queue", schema="domain_inventory", type_="foreignkey")
    op.drop_column("lkw_annahme_queue", "article_id", schema="domain_inventory")
