"""Add image_url to articles

Revision ID: articles_image_url_20260322
Revises:
Create Date: 2026-03-22

"""
from alembic import op
import sqlalchemy as sa

revision = 'articles_image_url_20260322'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'articles',
        sa.Column('image_url', sa.String(500), nullable=True, comment='Product image URL (auto-fetched or manually set)'),
        schema='domain_inventory',
    )


def downgrade() -> None:
    op.drop_column('articles', 'image_url', schema='domain_inventory')
