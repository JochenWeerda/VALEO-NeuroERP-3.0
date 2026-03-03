"""add_article_price_thresholds_20260303

Revision ID: d7e8f9a0b1c2
Revises: b2c3d4e5f6a7
Create Date: 2026-03-03

Tabelle article_price_thresholds für Price-Monitoring-Worker (Min/Max-Alerts).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "article_price_thresholds",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("domain_shared.tenants.id"), nullable=False),
        sa.Column("article_id", sa.String(), sa.ForeignKey("domain_inventory.articles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("warengruppe", sa.String(length=80), nullable=True),
        sa.Column("crop_code", sa.String(length=20), nullable=True),
        sa.Column("min_eur_per_ton", sa.DECIMAL(10, 2), nullable=True, comment="Untere Schwellen-Alert"),
        sa.Column("max_eur_per_ton", sa.DECIMAL(10, 2), nullable=True, comment="Obere Schwellen-Alert"),
        sa.Column("effective_from", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema="domain_inventory",
    )
    op.create_primary_key("pk_article_price_thresholds", "article_price_thresholds", ["id"], schema="domain_inventory")
    op.create_index("ix_article_price_thresholds_tenant_id", "article_price_thresholds", ["tenant_id"], schema="domain_inventory")
    op.create_index("ix_article_price_thresholds_article_id", "article_price_thresholds", ["article_id"], schema="domain_inventory")
    op.create_index("ix_article_price_thresholds_crop_code", "article_price_thresholds", ["crop_code"], schema="domain_inventory")


def downgrade() -> None:
    op.drop_table("article_price_thresholds", schema="domain_inventory")
