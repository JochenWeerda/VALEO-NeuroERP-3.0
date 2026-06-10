"""Merge CRM ownership and production-readiness migration branches.

Revision ID: merge_crm_owner_prod_20260610
Revises: crm_ownership_log_20260610, merge_supply_prod_20260610
"""

revision = "merge_crm_owner_prod_20260610"
down_revision = (
    "crm_ownership_log_20260610",
    "merge_supply_prod_20260610",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
