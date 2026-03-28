"""LKW-Annahme-Queue Klaerungsdaten

Revision ID: lkw_annahme_queue_klaerung_20260328
Revises: lkw_annahme_queue_article_reference_20260328
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "lkw_annahme_queue_klaerung_20260328"
down_revision: Union[str, tuple[str, ...], None] = "lkw_annahme_queue_article_reference_20260328"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "lkw_annahme_queue",
        sa.Column("klaerung", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_column("lkw_annahme_queue", "klaerung", schema="domain_inventory")
