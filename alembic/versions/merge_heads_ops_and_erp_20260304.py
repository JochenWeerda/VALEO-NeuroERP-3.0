"""merge heads: domain_ops (missing_ops) and domain_erp (finance tables)

Revision ID: merge_heads_20260304
Revises: missing_ops_20260304, d1e2f3a4b5c6
Create Date: 2026-03-04

Ein einziger Head, damit bei Neuinstallation 'alembic upgrade head' alle Tabellen anlegt.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "merge_heads_20260304"
down_revision: Union[str, None] = ("missing_ops_20260304", "d1e2f3a4b5c6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
