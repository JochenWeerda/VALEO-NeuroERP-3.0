"""Eingangslieferschein: gegen welche Bestellung abgeglichen, und wann.

Revision ID: lieferschein_abgleich_20261007
Revises: ebilanz_persist_20261007

Bis 07.10.2026 liess sich derselbe Eingangslieferschein beliebig oft gegen eine
Bestellung abgleichen; jeder Lauf zaehlte die gelieferte Menge erneut auf die
Bestellpositionen. Der Abgleich haelt jetzt fest, dass er gelaufen ist.

Additiv: zwei nullbare Spalten, keine Datenaenderung.
"""

from alembic import op

revision = "lieferschein_abgleich_20261007"
down_revision = "ebilanz_persist_20261007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE public.einkauf_lieferscheine "
        "ADD COLUMN IF NOT EXISTS abgleich_bestellung_id VARCHAR(36), "
        "ADD COLUMN IF NOT EXISTS abgeglichen_am TIMESTAMPTZ"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE public.einkauf_lieferscheine "
        "DROP COLUMN IF EXISTS abgeglichen_am, "
        "DROP COLUMN IF EXISTS abgleich_bestellung_id"
    )
