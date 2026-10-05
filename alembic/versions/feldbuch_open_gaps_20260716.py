"""Ackerschlagkartei open-gaps: Register, AUM, Lager, Offline client_ref.

Revision ID: feldbuch_open_gaps_20260716
Revises: feldbuch_inkrement1_20260716
"""

from alembic import op

revision = "feldbuch_open_gaps_20260716"
down_revision = "feldbuch_inkrement1_20260716"
branch_labels = None
depends_on = None

_COLS = [
    ("register_daten", "JSONB"),
    ("aum_code", "VARCHAR(40)"),
    ("lager_artikel_id", "VARCHAR"),
    ("lager_charge", "VARCHAR(80)"),
    ("lager_verbrauch", "DOUBLE PRECISION"),
    ("client_ref", "VARCHAR(120)"),
]


def upgrade() -> None:
    for col, typ in _COLS:
        op.execute(
            f"ALTER TABLE domain_agrar.feldbuch_massnahmen "
            f"ADD COLUMN IF NOT EXISTS {col} {typ}"
        )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_feldbuch_massnahmen_client_ref "
        "ON domain_agrar.feldbuch_massnahmen (client_ref)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feldbuch_massnahmen_client_ref")
    for col, _ in _COLS:
        op.execute(
            f"ALTER TABLE domain_agrar.feldbuch_massnahmen DROP COLUMN IF EXISTS {col}"
        )
