"""
Merge Alembic heads l3c_gap_001 and optimize_procurement_indexes_20260213.
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "merge_l3c_and_procurement_indexes_20260213"
down_revision: Union[str, Sequence[str], None] = (
    "l3c_gap_001",
    "optimize_procurement_indexes_20260213",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

