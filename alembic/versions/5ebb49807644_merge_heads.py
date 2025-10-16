"""merge_heads

Revision ID: 5ebb49807644
Revises: ff7b1a7899b4, 69a59fde9295
Create Date: 2025-10-16 07:33:45.407179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ebb49807644'
down_revision: Union[str, None] = ('ff7b1a7899b4', '69a59fde9295')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
