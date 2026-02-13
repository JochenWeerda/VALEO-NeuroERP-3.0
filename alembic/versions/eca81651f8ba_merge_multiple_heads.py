"""Merge multiple heads

Revision ID: eca81651f8ba
Revises: 7f8529f27eb0, add_agrar_mod, 4601a09c0fc1
Create Date: 2025-10-16 06:38:49.706725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca81651f8ba'
down_revision: Union[str, None] = ('7f8529f27eb0', 'add_agrar_mod', '4601a09c0fc1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
