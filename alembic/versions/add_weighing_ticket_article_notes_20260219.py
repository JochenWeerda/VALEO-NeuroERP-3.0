"""add_weighing_ticket_article_notes_20260219

Revision ID: add_wt_article_notes_20260219
Revises: add_vat_modes_20260217
Create Date: 2026-02-19 10:00:00.000000

Erweitert weighing_tickets um:
- article_group (Warengruppe, z.B. 'Kraftfutter Nordkraft', 'Getreide')
- article_id (FK -> articles, optionale Ware)
- notes (Notizen/Bemerkungen, z.B. 'Dienstleistungswiegung')
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_wt_article_notes_20260219'
down_revision: Union[str, None] = 'add_vat_modes_20260217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "weighing_tickets",
        sa.Column(
            "article_group",
            sa.String(length=80),
            nullable=True,
            comment="Warengruppe/Artikelgruppe (z.B. Kraftfutter Nordkraft, Getreide)",
        ),
        schema="domain_inventory",
    )

    op.add_column(
        "weighing_tickets",
        sa.Column(
            "article_id",
            sa.String(),
            sa.ForeignKey("domain_inventory.articles.id", ondelete="SET NULL"),
            nullable=True,
            comment="Optionaler Artikel (FK)",
        ),
        schema="domain_inventory",
    )

    op.add_column(
        "weighing_tickets",
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
            comment="Notizen/Bemerkungen",
        ),
        schema="domain_inventory",
    )

    op.create_index(
        "ix_weighing_tickets_article_group",
        "weighing_tickets",
        ["article_group"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_weighing_tickets_article_group",
        table_name="weighing_tickets",
        schema="domain_inventory",
    )
    op.drop_column("weighing_tickets", "notes", schema="domain_inventory")
    op.drop_column("weighing_tickets", "article_id", schema="domain_inventory")
    op.drop_column("weighing_tickets", "article_group", schema="domain_inventory")
