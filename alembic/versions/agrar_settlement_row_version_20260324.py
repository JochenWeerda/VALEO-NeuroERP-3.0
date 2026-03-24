"""AgrarSettlement optimistic locking: row_version

Revision ID: agrar_settlement_row_version_20260324
Revises: 8f4c2b1d9e7a, articles_image_url_20260322
Create Date: 2026-03-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "agrar_settlement_row_version_20260324"
down_revision: Union[str, tuple[str, ...], None] = (
    "8f4c2b1d9e7a",
    "articles_image_url_20260322",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agrar_settlements",
        sa.Column(
            "row_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
            comment="Optimistic locking (SQLAlchemy version_id_col)",
        ),
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_column("agrar_settlements", "row_version", schema="domain_inventory")
