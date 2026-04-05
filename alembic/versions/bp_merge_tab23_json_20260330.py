"""Merge heads + domain_crm.business_partners.tab_23 JSONB (Tab-23 Stammdaten)

Revision ID: bp_merge_tab23_json_20260330
Revises: merge_wave104_20260326, neuroassist_state_graph_confidence_ledger_20260329
Create Date: 2026-03-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "bp_merge_tab23_json_20260330"
down_revision: Union[str, tuple[str, ...], None] = (
    "merge_wave104_20260326",
    "neuroassist_state_graph_confidence_ledger_20260329",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "business_partners",
        sa.Column("tab_23", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema="domain_crm",
    )


def downgrade() -> None:
    op.drop_column("business_partners", "tab_23", schema="domain_crm")
