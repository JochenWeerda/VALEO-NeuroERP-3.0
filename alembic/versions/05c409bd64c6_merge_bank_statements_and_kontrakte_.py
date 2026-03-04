"""merge bank_statements and kontrakte heads

Revision ID: 05c409bd64c6
Revises: c1d2e3f4a5b6, e4f5a6b7c8d9
Create Date: 2026-03-04 06:48:13.624260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05c409bd64c6'
down_revision: Union[str, None] = ('c1d2e3f4a5b6', 'e4f5a6b7c8d9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
