"""Merge DOC- und PROC-Branch zu einem Alembic-Head.

Revision ID: merge_doc_proc_20260612
Revises: doc_followup_20260611, proc_rfq_20260611

Der parallele DOM-*-004-Ausbau hinterließ zwei offene Heads, die beide bei
``con_settlement_storno_20260611`` abzweigen:
  • DOC-Branch  (Claude):  …→sales_delivery_storno→doc_artifact_version→doc_followup
  • PROC-Branch (Cursor):  …→proc_three_way_inv→proc_follow_up→proc_ers_credit→proc_rfq
Diese Merge-Revision führt beide zusammen und stellt den Single-Head wieder her,
damit ``scripts/init_db.py`` (`upgrade head`, Singular) wieder durchläuft.
"""

from typing import Sequence, Union

revision: str = "merge_doc_proc_20260612"
down_revision: Union[str, Sequence[str], None] = (
    "doc_followup_20260611",
    "proc_rfq_20260611",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
