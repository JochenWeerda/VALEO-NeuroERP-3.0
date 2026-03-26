"""Merge Wave 104 migrations with main head

Revision ID: merge_wave104_20260326
Revises: agrar_settlement_row_version_20260324, pcn_meldungen_20260326
Create Date: 2026-03-26
"""

from alembic import op

revision = "merge_wave104_20260326"
down_revision = ("agrar_settlement_row_version_20260324", "pcn_meldungen_20260326")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
