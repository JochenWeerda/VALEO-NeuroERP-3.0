"""Merge CRM capture inbox and POS fiscal provider branches.

Revision ID: merge_crm_pos_20260609
Revises: crm_capture_inbox_kim_20260609, pos_fiscal_providers_20260609
"""

revision = "merge_crm_pos_20260609"
down_revision = (
    "crm_capture_inbox_kim_20260609",
    "pos_fiscal_providers_20260609",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
