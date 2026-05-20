"""merge_wave106_and_kontrakt_klasse_20260520

Revision ID: 31b00be545af
Revises: c68442f4d6dd, ops_wave106_operations_crud_20260519
Create Date: 2026-05-20 06:06:13.463896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31b00be545af'
down_revision: Union[str, None] = ('c68442f4d6dd', 'ops_wave106_operations_crud_20260519')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
