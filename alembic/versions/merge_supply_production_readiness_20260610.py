"""Merge supply-chain and production-readiness migration branches.

Revision ID: merge_supply_prod_20260610
Revises: normalize_fin_hr_20260610, supply_chain_events_20260610
"""

revision = "merge_supply_prod_20260610"
down_revision = (
    "normalize_fin_hr_20260610",
    "supply_chain_events_20260610",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
