"""merge_gdpr_base

Revision ID: 4e8447ad429a
Revises: crm_campaigns_20260524, merge_heads_20260522
Create Date: 2026-05-25

"""
from typing import Sequence, Union

revision: str = '4e8447ad429a'
down_revision = ('crm_campaigns_20260524', 'merge_heads_20260522')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
