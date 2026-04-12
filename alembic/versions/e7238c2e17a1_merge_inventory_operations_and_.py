"""merge inventory_operations and futtermittel heads

Revision ID: e7238c2e17a1
Revises: futtermittel_sorten_produktion_20260410, inventory_operations_20260409
Create Date: 2026-04-12 09:55:07.714977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7238c2e17a1'
down_revision: Union[str, None] = ('futtermittel_sorten_produktion_20260410', 'inventory_operations_20260409')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
