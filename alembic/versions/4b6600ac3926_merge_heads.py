"""merge heads

Revision ID: 4b6600ac3926
Revises: add_crm_discount, add_documents_json, portal_001, procurement_p0_001
Create Date: 2026-02-10 10:42:34.098810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


***REMOVED*** revision identifiers, used by Alembic.
revision: str = '4b6600ac3926'
down_revision: Union[str, None] = ('add_crm_discount', 'add_documents_json', 'portal_001', 'procurement_p0_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
