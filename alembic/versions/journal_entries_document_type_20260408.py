"""domain_erp.journal_entries: document_type ergaenzen (GoBD Belegart)

Revision ID: journal_entries_document_type_20260408
Revises: einkauf_bestellungen_dedupe_unique_20260407
Create Date: 2026-04-08

`ensure_journal_entries_table_20260303` legt document_type nur bei Neu-Anlage der Tabelle an.
Bestehende Installationen ohne diese Spalte brauchen ALTER TABLE.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "journal_entries_document_type_20260408"
down_revision: Union[str, None] = "einkauf_bestellungen_dedupe_unique_20260407"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    je = conn.execute(text("SELECT to_regclass('domain_erp.journal_entries')")).scalar()
    if not je:
        return
    r = conn.execute(
        text(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'domain_erp'
              AND table_name = 'journal_entries'
              AND column_name = 'document_type'
            """
        )
    )
    if r.scalar() is None:
        op.execute(
            text(
                "ALTER TABLE domain_erp.journal_entries "
                "ADD COLUMN document_type VARCHAR(50) NULL"
            )
        )


def downgrade() -> None:
    op.execute(text("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS document_type"))
