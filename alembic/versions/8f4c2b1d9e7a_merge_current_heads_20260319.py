"""merge current heads for deterministic single-head bootstrap

Revision ID: 8f4c2b1d9e7a
Revises: accruals_provisions_20260305, workflow_version_20260307, crm_consent_seg_001, crm_phase4_links_20260305, einkauf_missing_20260305, sales_cn_ret_pl_20260305
Create Date: 2026-03-19 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f4c2b1d9e7a"
down_revision: Union[str, None] = (
    "accruals_provisions_20260305",
    "workflow_version_20260307",
    "crm_consent_seg_001",
    "crm_phase4_links_20260305",
    "einkauf_missing_20260305",
    "sales_cn_ret_pl_20260305",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
