"""merge heads: feed_qs_wf_cockpit_repair + pricing_staffelrabatt_artikel_m2m

Revision ID: 42e0e183bd0c
Revises: feed_qs_wf_cockpit_repair_20260626, pricing_staffelrabatt_artikel_m2m_20260702
Create Date: 2026-07-02 10:53:34.106193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42e0e183bd0c'
down_revision: Union[str, None] = ('feed_qs_wf_cockpit_repair_20260626', 'pricing_staffelrabatt_artikel_m2m_20260702')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
